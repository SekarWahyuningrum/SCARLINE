"""Supabase tiruan (in-memory) KHUSUS untuk pengujian otomatis.

Meniru perilaku penting: Auth (sign up / sign in / refresh), PostgREST
(select/insert/upsert/update dengan filter eq/neq), constraint unik, dan RLS
(baca dengan token siswa hanya mengembalikan baris miliknya).
Aplikasi asli selalu memakai ``SupabaseClient`` yang terhubung ke Supabase.
"""
import copy
import itertools
import time
import uuid
from datetime import datetime, timezone

from scarline.supabase_client import SupabaseError

UNIQUE = {
    "profiles": [("id",), ("username",)],
    "lesson_progress": [("user_id", "lesson_slug")],
    "user_stats": [("user_id",)],
    "user_achievements": [("user_id", "achievement_slug")],
    "daily_claims": [("user_id", "claim_date")],
}
OWNER = {"profiles": "id"}
_clock = itertools.count()


class FakeSupabase:
    def __init__(self, configured=True, can_write=True):
        self.configured = configured
        self.can_write = can_write
        self.tables = {}
        self.users = {}       # email -> {id, email, password, meta}
        self.tokens = {}      # access_token -> user_id
        self.refresh_tokens = {}
        self.admin_created = []
        self.recover_calls = []
        self.trigger = True

    # ---------------------------------------------------------------- auth
    def _session(self, user, expires_in=3600):
        token, refresh = "at-" + uuid.uuid4().hex, "rt-" + uuid.uuid4().hex
        self.tokens[token] = user["id"]
        self.refresh_tokens[refresh] = user["id"]
        return {"access_token": token, "refresh_token": refresh, "expires_in": expires_in, "expires_at": int(time.time()) + expires_in,
                "user": {"id": user["id"], "email": user["email"], "user_metadata": user["meta"]}}

    def sign_up(self, email, password, metadata, redirect_to=""):
        if email in self.users:
            return {"id": self.users[email]["id"], "identities": []}
        uid = str(uuid.uuid4())
        user = {"id": uid, "email": email, "password": password, "meta": metadata}
        if self.trigger:
            try:
                self._insert_row("profiles", {"id": uid, "full_name": metadata["full_name"], "username": metadata["username"], "email": email, "class_name": metadata["class_name"]})
            except SupabaseError:
                raise SupabaseError("Database error saving new user", 500)
            self._insert_row("user_stats", {"user_id": uid, "total_xp": 0, "level": 1, "missions_completed": 0, "games_played": 0, "quizzes_taken": 0, "finals_taken": 0, "best_final_score": 0})
        self.users[email] = user
        return self._session(user)

    def admin_create_user(self, email, password, metadata):
        if email in self.users:
            raise SupabaseError("A user with this email address has already been registered", 422)
        session = self.sign_up(email, password, metadata)
        self.admin_created.append(email)
        return session["user"]

    def sign_in(self, email, password):
        user = self.users.get(email)
        if not user or user["password"] != password:
            raise SupabaseError("Invalid login credentials", 400)
        return self._session(user)

    def refresh(self, refresh_token):
        uid = self.refresh_tokens.pop(refresh_token, None)
        if not uid:
            raise SupabaseError("Invalid Refresh Token", 400)
        user = next(u for u in self.users.values() if u["id"] == uid)
        return self._session(user)

    def get_user(self, token):
        return {"id": self.tokens[token]}

    def sign_out(self, token):
        self.tokens.pop(token, None)

    def recover(self, email, redirect_to):
        self.recover_calls.append((email, redirect_to))

    def update_password(self, token, password):
        uid = self.tokens.get(token)
        if not uid:
            raise SupabaseError("invalid JWT", 401)
        for u in self.users.values():
            if u["id"] == uid:
                u["password"] = password
        return {}

    # ---------------------------------------------------------------- data
    @staticmethod
    def _match(row, filters):
        for col, val in (filters or {}).items():
            if isinstance(val, tuple):
                op, v = val
                if op == "neq" and row.get(col) == v:
                    return False
                if op == "eq" and row.get(col) != v:
                    return False
            elif row.get(col) != val:
                return False
        return True

    def select(self, table, *, token=None, filters=None, columns="*", order=None, limit=None):
        rows = [r for r in self.tables.get(table, []) if self._match(r, filters)]
        if token is not None:  # RLS: hanya baris milik pemilik token
            uid = self.tokens.get(token)
            if uid is None:
                raise SupabaseError("JWT expired", 401)
            owner = OWNER.get(table, "user_id")
            if table in ("profiles", "lesson_progress", "quiz_attempts", "game_attempts", "user_stats", "user_achievements", "activity_logs", "daily_claims"):
                rows = [r for r in rows if r.get(owner) == uid]
        if order:
            col, _, direction = order.partition(".")
            rows.sort(key=lambda r: (r.get(col) is None, r.get(col), r.get("_seq")), reverse=direction == "desc")
        if limit:
            rows = rows[:limit]
        return copy.deepcopy(rows)

    def _conflict(self, table, row):
        for cols in UNIQUE.get(table, []):
            for existing in self.tables.get(table, []):
                if all(existing.get(c) == row.get(c) for c in cols):
                    return existing
        return None

    def _insert_row(self, table, row):
        row = dict(row)
        if self._conflict(table, row):
            raise SupabaseError("duplicate key value violates unique constraint", 409)
        row.setdefault("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        for col in ("created_at", "earned_at", "updated_at"):
            row.setdefault(col, now)
        row["_seq"] = next(_clock)
        self.tables.setdefault(table, []).append(row)
        return row

    def insert(self, table, rows):
        rows = rows if isinstance(rows, list) else [rows]
        return [copy.deepcopy(self._insert_row(table, r)) for r in rows]

    def upsert(self, table, rows, on_conflict, ignore_duplicates=False):
        rows = rows if isinstance(rows, list) else [rows]
        out = []
        for r in rows:
            existing = self._conflict(table, r)
            if existing:
                if not ignore_duplicates:
                    existing.update(r)
                    out.append(copy.deepcopy(existing))
            else:
                out.append(copy.deepcopy(self._insert_row(table, r)))
        return out

    def update(self, table, filters, values, *, token=None):
        out = []
        for r in self.tables.get(table, []):
            if self._match(r, filters):
                r.update(values)
                out.append(copy.deepcopy(r))
        return out
