"""Lapisan data SCARLINE: progres, skor, XP, level, lencana, dan riwayat.

Aturan penting:
- Baca data untuk halaman memakai token siswa (RLS aktif).
- Tulis data hasil belajar memakai service role di server; setiap query
  SELALU difilter dengan ``user_id`` siswa yang sedang login.
- XP hanya diberikan untuk peningkatan nyata (misi pertama kali selesai,
  skor terbaik baru, klaim harian sekali sehari), sehingga refresh atau
  mengulang tidak menambah XP.
"""
from __future__ import annotations

import hashlib
import time
from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Optional

from .content import (
    ACHIEVEMENT_BY_SLUG,
    ACHIEVEMENTS,
    ASSESSMENT_TITLES,
    LESSON_BY_SLUG,
    LESSON_ORDER,
    QUESTION_BY_ID,
    REAL_CASES,
    SECRET_BY_SLUG,
    SECRET_MISSIONS,
    SECRET_ORDER,
    SECRET_PASS,
    TOPIC_LABELS,
    TOPIC_LESSON,
    V2_ACHIEVEMENTS,
    level_for_xp,
)
from .games import DIFFICULTIES, GAME_BY_SLUG, V2_GAMES
from .supabase_client import SupabaseError

LESSON_PASS_SCORE = 60  # mini quiz: minimal 2 dari 3 benar
FINAL_PASS_SCORE = 70
MASTERY_SCORE = 70      # topik dianggap dikuasai jika ≥ 70% benar
WIB = timezone(timedelta(hours=7))

ASSESSMENT_XP = {"pretest": 30, "posttest": 50}   # sekali, saat pertama kali dikerjakan
CHALLENGE_XP = {"secret": 50, "reallife": 40}     # sekali per misi/kasus, saat pertama kali tuntas
AVATARS = ["explorer", "scientist", "pilot", "artist", "astronaut", "detective"]
SOURCE_LABELS = {"lesson": "Mini quiz misi", "training": "Training Zone", "daily": "Tantangan Harian", "final": "Final Line Challenge",
                 "pretest": "Pre-Test", "posttest": "Post-Test", "secret": "Secret Mission", "reallife": "Real-Life Challenge",
                 "mistake": "Mistake Notebook"}

_V2_CACHE: Dict[int, tuple] = {}


def is_missing_table(exc: SupabaseError) -> bool:
    text = str(exc).lower()
    return exc.status == 404 or "schema cache" in text or "does not exist" in text or "pgrst205" in text


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def stars_for(pct: float) -> int:
    if pct >= 90:
        return 3
    if pct >= 70:
        return 2
    if pct >= 40:
        return 1
    return 0


class LearningService:
    def __init__(self, db, user_id: str, token: Optional[str] = None):
        self.db = db
        self.user_id = user_id
        self.token = token

    # ------------------------------------------------------------ helpers
    def _mine(self, table: str, *, order: Optional[str] = None, limit: Optional[int] = None, **filters) -> List[dict]:
        """SELECT milik siswa ini. Pakai token siswa jika ada (RLS), jika tidak service role + filter user."""
        f = {"user_id": self.user_id, **filters}
        return self.db.select(table, token=self.token, filters=f, order=order, limit=limit)

    def _svc(self, table: str, *, order: Optional[str] = None, limit: Optional[int] = None, **filters) -> List[dict]:
        f = {"user_id": self.user_id, **filters}
        return self.db.select(table, token=None, filters=f, order=order, limit=limit)

    # ------------------------------------------------------------ profile
    def profile(self) -> Optional[dict]:
        rows = self.db.select("profiles", token=self.token, filters={"id": self.user_id}, limit=1)
        return rows[0] if rows else None

    def ensure_profile(self, user: dict) -> dict:
        """Pastikan baris profiles & user_stats ada (fallback jika trigger belum terpasang)."""
        rows = self.db.select("profiles", token=None, filters={"id": self.user_id}, limit=1)
        if rows:
            self.stats()
            return rows[0]
        meta = user.get("user_metadata") or {}
        email = user.get("email", "")
        username = (meta.get("username") or email.split("@")[0] or "explorer")[:20].lower()
        row = {
            "id": self.user_id,
            "full_name": meta.get("full_name") or username,
            "username": username,
            "email": email,
            "class_name": meta.get("class_name") or "VIII",
        }
        created = self.db.upsert("profiles", row, on_conflict="id", ignore_duplicates=True)
        self.stats()
        return created[0] if created else row

    def update_profile(self, full_name: str, class_name: str) -> None:
        self.db.update("profiles", {"id": self.user_id}, {"full_name": full_name, "class_name": class_name, "updated_at": now_iso()})
        self.log("profil", "Memperbarui profil", status="selesai")

    # ------------------------------------------------------------ stats/xp
    def stats(self) -> dict:
        rows = self._svc("user_stats", limit=1)
        if rows:
            return rows[0]
        row = {"user_id": self.user_id, "total_xp": 0, "level": 1, "missions_completed": 0, "games_played": 0,
               "quizzes_taken": 0, "finals_taken": 0, "best_final_score": 0}
        created = self.db.upsert("user_stats", row, on_conflict="user_id", ignore_duplicates=True)
        return created[0] if created else row

    def _bump(self, xp: int = 0, **counters) -> dict:
        st = self.stats()
        values = {"updated_at": now_iso()}
        total = int(st.get("total_xp") or 0) + max(0, int(xp))
        values["total_xp"] = total
        values["level"] = level_for_xp(total)["level"]
        for key, delta in counters.items():
            if key.startswith("set_"):
                values[key[4:]] = delta
            else:
                values[key] = int(st.get(key) or 0) + delta
        rows = self.db.update("user_stats", {"user_id": self.user_id}, values)
        return rows[0] if rows else {**st, **values}

    def log(self, activity_type: str, title: str, *, ref: Optional[str] = None, score: Optional[int] = None,
            status: str = "selesai", xp: int = 0, meta: Optional[dict] = None) -> None:
        self.db.insert("activity_logs", {
            "user_id": self.user_id, "activity_type": activity_type, "title": title, "ref": ref,
            "score": score, "status": status, "xp_awarded": xp, "meta": meta or {},
        })

    # ------------------------------------------------------------ lessons
    def lesson_progress(self) -> Dict[str, dict]:
        return {r["lesson_slug"]: r for r in self._mine("lesson_progress")}

    def completed_lessons(self) -> List[str]:
        return [s for s, r in self.lesson_progress().items() if r.get("status") == "completed"]

    @staticmethod
    def unlocked(slug: str, completed: List[str]) -> bool:
        idx = LESSON_ORDER.index(slug)
        return idx == 0 or LESSON_ORDER[idx - 1] in completed

    def open_lesson(self, slug: str) -> None:
        rows = self._svc("lesson_progress", lesson_slug=slug, limit=1)
        if not rows:
            self.db.upsert("lesson_progress", {"user_id": self.user_id, "lesson_slug": slug, "status": "in_progress"},
                           on_conflict="user_id,lesson_slug", ignore_duplicates=True)
            lesson = LESSON_BY_SLUG[slug]
            self.log("materi", f"Membuka Mission {lesson['no']:02d} — {lesson['region']}", ref=slug, status="dibuka")

    def best_lesson_quiz(self, slug: str) -> int:
        rows = self._svc("quiz_attempts", quiz_slug=f"lesson-{slug}", order="score.desc", limit=1)
        return int(rows[0]["score"]) if rows else 0

    def complete_lesson(self, slug: str) -> dict:
        lesson = LESSON_BY_SLUG[slug]
        completed = self.completed_lessons()
        if slug in completed:
            return {"ok": True, "already": True, "xp_awarded": 0, "new_achievements": []}
        if not self.unlocked(slug, completed):
            return {"ok": False, "error": "Misi ini masih terkunci. Selesaikan misi sebelumnya dulu, ya!"}
        if self.best_lesson_quiz(slug) < LESSON_PASS_SCORE:
            return {"ok": False, "error": "Selesaikan mini quiz dengan minimal 2 jawaban benar sebelum menyelesaikan misi."}
        existing = self._svc("lesson_progress", lesson_slug=slug, limit=1)
        values = {"status": "completed", "completed_at": now_iso(), "updated_at": now_iso(), "quiz_score": self.best_lesson_quiz(slug)}
        if existing:
            rows = self.db.update("lesson_progress", {"user_id": self.user_id, "lesson_slug": slug, "status": ("neq", "completed")}, values)
            if not rows:  # sudah diselesaikan oleh request lain (double click)
                return {"ok": True, "already": True, "xp_awarded": 0, "new_achievements": []}
        else:
            self.db.insert("lesson_progress", {"user_id": self.user_id, "lesson_slug": slug, **values})
        xp = int(lesson["xp"])
        self._bump(xp, missions_completed=1)
        self.log("misi", f"Menyelesaikan Mission {lesson['no']:02d} — {lesson['region']}", ref=slug, status="selesai", xp=xp)
        new = self.evaluate_achievements()
        return {"ok": True, "already": False, "xp_awarded": xp, "new_achievements": new}

    # ------------------------------------------------------------ quizzes
    def record_quiz(self, *, quiz_slug: str, kind: str, title: str, correct: int, total: int, duration: int,
                    answers: list, meta: Optional[dict] = None) -> dict:
        score = round(correct * 100 / total) if total else 0
        prev = self._svc("quiz_attempts", quiz_slug=quiz_slug, order="score.desc", limit=1)
        prev_best_score = int(prev[0]["score"]) if prev else 0
        prev_best_correct = int(prev[0]["correct"]) if prev else 0
        if kind == "training":
            xp = 10 * max(0, correct - prev_best_correct)
        elif kind == "final":
            xp = 2 * max(0, score - prev_best_score)
        else:
            xp = 0
        stars = stars_for(score)
        self.db.insert("quiz_attempts", {
            "user_id": self.user_id, "quiz_slug": quiz_slug, "kind": kind, "score": score, "correct": correct,
            "total": total, "stars": stars, "xp_awarded": xp, "duration_seconds": duration, "answers": answers,
        })
        counters = {}
        if kind == "training":
            counters["quizzes_taken"] = 1
        if kind == "final":
            counters["finals_taken"] = 1
            st = self.stats()
            counters["set_best_final_score"] = max(int(st.get("best_final_score") or 0), score)
        self._bump(xp, **counters)
        status = "lulus" if (kind != "final" or score >= FINAL_PASS_SCORE) else "belum lulus"
        if kind == "lesson":
            status = "lulus" if score >= LESSON_PASS_SCORE else "belum lulus"
        self.log({"training": "latihan", "final": "evaluasi", "lesson": "mini quiz"}.get(kind, kind), title,
                 ref=quiz_slug, score=score, status=status, xp=xp, meta=meta)
        new = self.evaluate_achievements()
        return {"score": score, "stars": stars, "xp_awarded": xp, "best_before": prev_best_score, "new_achievements": new}

    def claim_daily(self, day: str, correct: int, total: int) -> dict:
        existing = self._svc("daily_claims", claim_date=day, limit=1)
        if existing:
            return {"already": True, "xp_awarded": 0, "new_achievements": []}
        xp = 10 * correct
        try:
            self.db.insert("daily_claims", {"user_id": self.user_id, "claim_date": day, "correct": correct, "total": total, "xp_awarded": xp})
        except SupabaseError:
            return {"already": True, "xp_awarded": 0, "new_achievements": []}
        self._bump(xp)
        self.log("tantangan harian", f"Tantangan Harian {day}", ref=day, score=round(correct * 100 / total) if total else 0, xp=xp)
        return {"already": False, "xp_awarded": xp, "new_achievements": self.evaluate_achievements()}

    # ------------------------------------------------------------ games
    @staticmethod
    def weighted(pct: float, difficulty: str) -> int:
        return round(pct * DIFFICULTIES.get(difficulty, DIFFICULTIES["easy"])["mult"])

    def best_game_weighted(self, slug: str) -> int:
        rows = self._svc("game_attempts", game_slug=slug)
        return max((self.weighted(float(r.get("percent") or 0), r.get("difficulty", "easy")) for r in rows), default=0)

    def record_game(self, *, slug: str, difficulty: str, score: int, max_score: int, rounds_correct: int,
                    rounds_total: int, duration: int) -> dict:
        pct = round(score * 100 / max_score, 1) if max_score else 0
        new_w = self.weighted(pct, difficulty)
        prev_w = self.best_game_weighted(slug)
        xp = min(150, max(0, new_w - prev_w))
        stars = stars_for(pct)
        self.db.insert("game_attempts", {
            "user_id": self.user_id, "game_slug": slug, "difficulty": difficulty, "score": score, "max_score": max_score,
            "percent": pct, "stars": stars, "xp_awarded": xp, "rounds_correct": rounds_correct,
            "rounds_total": rounds_total, "duration_seconds": duration,
        })
        self._bump(xp, games_played=1)
        title = GAME_BY_SLUG[slug].INFO["title"]
        self.log("game", f"Bermain {title} ({DIFFICULTIES[difficulty]['label']})", ref=slug, score=round(pct), xp=xp,
                 status="selesai", meta={"score": score, "max": max_score})
        return {"percent": pct, "stars": stars, "xp_awarded": xp, "new_achievements": self.evaluate_achievements()}

    # ------------------------------------------------------------ achievements
    def earned_achievements(self) -> Dict[str, dict]:
        return {r["achievement_slug"]: r for r in self._mine("user_achievements", order="earned_at.desc")}

    def evaluate_achievements(self) -> List[dict]:
        have = {r["achievement_slug"] for r in self._svc("user_achievements")}
        progress = {r["lesson_slug"]: r for r in self._svc("lesson_progress")}
        done = {s for s, r in progress.items() if r.get("status") == "completed"}
        games = self._svc("game_attempts")
        best_pct = {}
        for g in games:
            best_pct[g["game_slug"]] = max(best_pct.get(g["game_slug"], 0), float(g.get("percent") or 0))
        quizzes = self._svc("quiz_attempts")
        best_quiz = {}
        for q in quizzes:
            best_quiz[q["quiz_slug"]] = max(best_quiz.get(q["quiz_slug"], 0), int(q.get("score") or 0))
        best_final = max((v for k, v in best_quiz.items() if k == "final-challenge"), default=0)
        daily = self._svc("daily_claims", limit=1)

        rules = {
            "first-step": len(done) >= 1,
            "coordinate-hunter": "coordinate-city" in done and best_pct.get("coordinate-hunter", 0) >= 70,
            "gradient-master": "gradient-mountain" in done,
            "line-creator": "line-constructor" in done,
            "equation-expert": "equation-factory" in done and best_quiz.get("training-3", 0) >= 80,
            "parallel-detective": "parallel-perpendicular" in done,
            "game-explorer": len(set(best_pct) & set(GAME_BY_SLUG)) == len(GAME_BY_SLUG),
            "daily-spark": bool(daily),
            "scarline-champion": best_final >= FINAL_PASS_SCORE,
            "graph-architect": best_pct.get("line-builder", 0) >= 70 and best_pct.get("gradient-rush", 0) >= 70,
        }
        v2 = self.v2_ready()
        if v2 and (V2_ACHIEVEMENTS - have):
            pre = self.first_assessment("pretest")
            post = self.latest_assessment("posttest")
            challenges = self.challenge_map()
            rules.update({
                "coordinate-explorer": bool(pre) and "coordinate-city" in done,
                "equation-solver": all(challenges.get(("reallife", c["slug"]), {}).get("completed") for c in REAL_CASES),
                "line-detective": best_pct.get("line-detective", 0) >= 70,
                "daily-streak": self.streak()["best"] >= 3,
                "rising-line": bool(pre and post) and int(post["score"]) > int(pre["score"]),
                "master-of-straight-lines": all(challenges.get(("secret", m["slug"]), {}).get("completed") for m in SECRET_MISSIONS),
            })
        new = []
        for ach in ACHIEVEMENTS:
            slug = ach["slug"]
            if slug in V2_ACHIEVEMENTS and not v2:
                continue  # baris katalog lencana baru belum ada (migrasi 002 belum dijalankan)
            if rules.get(slug) and slug not in have:
                inserted = self.db.upsert("user_achievements", {"user_id": self.user_id, "achievement_slug": slug},
                                          on_conflict="user_id,achievement_slug", ignore_duplicates=True)
                if inserted:
                    self._bump(ach["xp_bonus"])
                    self.log("lencana", f"Mendapat lencana {ach['title']}", ref=slug, xp=ach["xp_bonus"], status="diperoleh")
                    new.append({"slug": slug, "title": ach["title"], "description": ach["description"], "icon": ach["icon"], "xp_bonus": ach["xp_bonus"]})
        return new

    # ------------------------------------------------------------ fitur v2 (migrasi 002)
    def v2_ready(self) -> bool:
        """True jika tabel migrasi 002 tersedia. Hasil disimpan sebentar agar tidak membebani database."""
        key = id(self.db)
        hit = _V2_CACHE.get(key)
        if hit and time.time() - hit[1] < (600 if hit[0] else 20):
            return hit[0]
        try:
            self.db.select("assessment_attempts", token=None, filters={"user_id": self.user_id}, limit=1)
            ok = True
        except SupabaseError as exc:
            if not is_missing_table(exc):
                raise
            ok = False
        _V2_CACHE[key] = (ok, time.time())
        return ok

    def posttest_unlocked(self, summary: Optional[dict] = None) -> bool:
        """Post-test dikerjakan SETELAH petualangan: ketujuh misi selesai dan Final Line Challenge sudah dikerjakan."""
        summary = summary or self.summary()
        return summary["final_unlocked"] and int(summary["stats"].get("finals_taken") or 0) > 0

    # ---- streak
    def active_days(self, limit: int = 400) -> List[date]:
        rows = self.db.select("activity_logs", token=None, filters={"user_id": self.user_id}, order="created_at.desc", limit=limit)
        days = set()
        for r in rows:
            try:
                ts = datetime.fromisoformat(str(r["created_at"]).replace("Z", "+00:00"))
            except (KeyError, ValueError):
                continue
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            days.add(ts.astimezone(WIB).date())
        return sorted(days)

    def streak(self) -> dict:
        days = self.active_days()
        today = datetime.now(WIB).date()
        best = run = 0
        prev = None
        for d in days:
            run = run + 1 if prev and (d - prev).days == 1 else 1
            best = max(best, run)
            prev = d
        current = 0
        day_set = set(days)
        cursor = today if today in day_set else today - timedelta(days=1)
        while cursor in day_set:
            current += 1
            cursor -= timedelta(days=1)
        last14 = [{"date": (today - timedelta(days=i)).isoformat(), "active": (today - timedelta(days=i)) in day_set} for i in range(13, -1, -1)]
        return {"current": current, "best": best, "today": today in day_set, "last14": last14, "total_days": len(days)}

    # ---- pre-test & post-test
    def assessments(self, kind: Optional[str] = None) -> List[dict]:
        if not self.v2_ready():
            return []
        filters = {"kind": kind} if kind else {}
        return self._mine("assessment_attempts", order="created_at.asc", **filters)

    def first_assessment(self, kind: str) -> Optional[dict]:
        rows = self._svc("assessment_attempts", kind=kind, order="created_at.asc", limit=1) if self.v2_ready() else []
        return rows[0] if rows else None

    def latest_assessment(self, kind: str) -> Optional[dict]:
        rows = self._svc("assessment_attempts", kind=kind, order="created_at.desc", limit=1) if self.v2_ready() else []
        return rows[0] if rows else None

    @staticmethod
    def topic_scores(review: List[dict]) -> Dict[str, dict]:
        out: Dict[str, dict] = {}
        for rv in review:
            t = out.setdefault(rv["topic"], {"correct": 0, "total": 0})
            t["total"] += 1
            t["correct"] += int(bool(rv["correct"]))
        return out

    def record_assessment(self, kind: str, *, correct: int, total: int, duration: int, review: List[dict], answers: list) -> dict:
        score = round(correct * 100 / total) if total else 0
        first = self.first_assessment(kind) is None
        xp = ASSESSMENT_XP[kind] if first else 0
        topics = self.topic_scores(review)
        self.db.insert("assessment_attempts", {
            "user_id": self.user_id, "kind": kind, "score": score, "correct": correct, "total": total,
            "duration_seconds": duration, "topic_scores": topics, "answers": answers,
        })
        if xp:
            self._bump(xp)
        self.log("asesmen", f"Mengerjakan {ASSESSMENT_TITLES[kind]}", ref=kind, score=score, xp=xp, status="selesai",
                 meta={"correct": correct, "total": total})
        for rv in review:
            if not rv["correct"]:
                self.record_mistake(rv["id"], rv.get("your_answer", ""), kind)
        return {"score": score, "xp_awarded": xp, "first": first, "new_achievements": self.evaluate_achievements()}

    def comparison(self) -> Optional[dict]:
        """Bandingkan pre-test pertama (kemampuan awal) dengan post-test terakhir. Jujur: tidak ada klaim naik jika tidak naik."""
        pre, post = self.first_assessment("pretest"), self.latest_assessment("posttest")
        if not pre or not post:
            return None
        a, b = int(pre["score"]), int(post["score"])
        diff = b - a
        pct = round(diff * 100 / a, 1) if a > 0 else None
        topics = []
        pre_t, post_t = pre.get("topic_scores") or {}, post.get("topic_scores") or {}
        for key, label in TOPIC_LABELS.items():
            pa, pb = pre_t.get(key), post_t.get(key)
            if not pa and not pb:
                continue
            pre_pct = round(pa["correct"] * 100 / pa["total"]) if pa else None
            post_pct = round(pb["correct"] * 100 / pb["total"]) if pb else None
            topics.append({"key": key, "label": label, "pre": pre_pct, "post": post_pct,
                           "mastered": post_pct is not None and post_pct >= MASTERY_SCORE,
                           "lesson": LESSON_BY_SLUG.get(TOPIC_LESSON.get(key, ""), {})})
        if diff > 0:
            verdict = f"Nilaimu naik {diff} poin, dari {a} menjadi {b}."
        elif diff == 0:
            verdict = f"Nilaimu sama dengan pre-test ({a}). Ulangi materi yang masih perlu ditingkatkan, lalu coba post-test lagi."
        else:
            verdict = f"Nilai post-test ({b}) lebih rendah {abs(diff)} poin dari pre-test ({a}). Tidak apa-apa — pelajari pembahasan dan topik yang masih perlu ditingkatkan, lalu coba lagi."
        return {"pre": a, "post": b, "diff": diff, "percent_change": pct, "improved": diff > 0, "verdict": verdict,
                "pre_date": pre["created_at"], "post_date": post["created_at"], "topics": topics,
                "mastered": [t for t in topics if t["mastered"]], "needs": [t for t in topics if t["post"] is not None and not t["mastered"]]}

    # ---- Mistake Notebook
    def record_mistake(self, question_id: str, your_answer: str, source: str) -> None:
        q = QUESTION_BY_ID.get(question_id)
        if not q or not self.v2_ready():
            return
        from .grading import answer_display  # impor lokal: hindari siklus impor

        existing = self._svc("mistakes", question_id=question_id, limit=1)
        if existing:
            self.db.update("mistakes", {"user_id": self.user_id, "question_id": question_id}, {
                "times_wrong": int(existing[0].get("times_wrong") or 1) + 1, "status": "perlu-latihan", "mastered_at": None,
                "your_answer": your_answer or "", "source": source, "updated_at": now_iso()})
            return
        self.db.upsert("mistakes", {
            "user_id": self.user_id, "question_id": question_id, "source": source, "topic": q.get("topic", "umum"),
            "prompt": q["prompt"], "your_answer": your_answer or "", "correct_answer": answer_display(q),
            "explanation": q.get("explain", ""), "status": "perlu-latihan", "times_wrong": 1,
        }, on_conflict="user_id,question_id", ignore_duplicates=True)

    def mistakes(self) -> List[dict]:
        return self._mine("mistakes", order="updated_at.desc", limit=200) if self.v2_ready() else []

    def mistake(self, question_id: str) -> Optional[dict]:
        rows = self._svc("mistakes", question_id=question_id, limit=1) if self.v2_ready() else []
        return rows[0] if rows else None

    def master_mistake(self, question_id: str) -> bool:
        rows = self.db.update("mistakes", {"user_id": self.user_id, "question_id": question_id, "status": ("neq", "dikuasai")},
                              {"status": "dikuasai", "mastered_at": now_iso(), "updated_at": now_iso()})
        if rows:
            q = QUESTION_BY_ID.get(question_id, {})
            self.log("mistake notebook", "Menguasai kembali soal yang pernah salah", ref=question_id, status="dikuasai",
                     meta={"topic": q.get("topic")})
        return bool(rows)

    @staticmethod
    def similar_question(question_id: str, attempt: int = 0) -> Optional[dict]:
        """Soal serupa: topik sama, soal berbeda. Dipilih bergiliran agar tidak selalu sama."""
        q = QUESTION_BY_ID.get(question_id)
        if not q:
            return None
        pool = sorted((c for c in QUESTION_BY_ID.values()
                       if c["id"] != question_id and c.get("topic") == q.get("topic") and c["type"] in ("mc", "tf", "num", "point", "line")),
                      key=lambda c: c["id"])
        if not pool:
            return q
        offset = int(hashlib.sha1(question_id.encode()).hexdigest(), 16)
        return pool[(offset + attempt) % len(pool)]

    # ---- SCAR's Diary
    def notes(self) -> List[dict]:
        return self._mine("diary_notes", order="updated_at.desc", limit=100) if self.v2_ready() else []

    def save_note(self, title: str, body: str, lesson_slug: Optional[str], note_id: Optional[str] = None) -> dict:
        values = {"title": title, "body": body, "lesson_slug": lesson_slug or None, "updated_at": now_iso()}
        if note_id:
            rows = self.db.update("diary_notes", {"user_id": self.user_id, "id": note_id}, values)
            if not rows:
                raise SupabaseError("Catatan tidak ditemukan.", 404)
            return rows[0]
        rows = self.db.insert("diary_notes", {"user_id": self.user_id, **values})
        self.log("diary", "Menulis catatan di SCAR's Diary", ref=lesson_slug, status="disimpan")
        return rows[0] if rows else values

    def delete_note(self, note_id: str) -> bool:
        return bool(self.db.delete("diary_notes", {"user_id": self.user_id, "id": note_id}))

    # ---- preferensi, bookmark, favorit
    DEFAULT_PREFS = {"theme": "light", "music": False, "sfx": True, "reduce_motion": False, "avatar": "explorer",
                     "bookmarks": [], "favorites": [], "reminder_time": None}

    def prefs(self) -> dict:
        if not self.v2_ready():
            return dict(self.DEFAULT_PREFS)
        rows = self._svc("user_preferences", limit=1)
        return {**self.DEFAULT_PREFS, **(rows[0] if rows else {})}

    def save_prefs(self, values: dict) -> dict:
        current = self.prefs()
        merged = {k: values.get(k, current.get(k)) for k in self.DEFAULT_PREFS}
        merged["user_id"] = self.user_id
        merged["updated_at"] = now_iso()
        rows = self.db.upsert("user_preferences", merged, on_conflict="user_id")
        return rows[0] if rows else merged

    def toggle_list_pref(self, key: str, slug: str) -> bool:
        prefs = self.prefs()
        items = list(prefs.get(key) or [])
        on = slug not in items
        items = items + [slug] if on else [s for s in items if s != slug]
        self.save_prefs({**prefs, key: items})
        return on

    # ---- Secret Mission & Real-Life Challenge
    def challenge_map(self) -> Dict[tuple, dict]:
        if not self.v2_ready():
            return {}
        return {(r["kind"], r["ref"]): r for r in self._svc("challenge_progress")}

    @staticmethod
    def secret_unlocked(slug: str, cmap: Dict[tuple, dict]) -> bool:
        idx = SECRET_ORDER.index(slug)
        return idx == 0 or bool(cmap.get(("secret", SECRET_ORDER[idx - 1]), {}).get("completed"))

    def record_challenge(self, kind: str, ref: str, correct: int, total: int) -> dict:
        score = round(correct * 100 / total) if total else 0
        passed = correct >= (SECRET_PASS if kind == "secret" else total - 1)
        existing = self._svc("challenge_progress", kind=kind, ref=ref, limit=1)
        prev = existing[0] if existing else {}
        first_completion = passed and not prev.get("completed")
        xp = CHALLENGE_XP[kind] if first_completion else 0
        values = {
            "best_score": max(int(prev.get("best_score") or 0), score),
            "points": max(int(prev.get("points") or 0), correct * 100),
            "completed": bool(prev.get("completed")) or passed,
            "attempts": int(prev.get("attempts") or 0) + 1,
            "xp_awarded": int(prev.get("xp_awarded") or 0) + xp,
            "updated_at": now_iso(),
        }
        if first_completion:
            values["completed_at"] = now_iso()
        if existing:
            self.db.update("challenge_progress", {"user_id": self.user_id, "kind": kind, "ref": ref}, values)
        else:
            self.db.upsert("challenge_progress", {"user_id": self.user_id, "kind": kind, "ref": ref, **values},
                           on_conflict="user_id,kind,ref")
        if xp:
            self._bump(xp)
        if kind == "secret":
            title = f"Secret Mission {SECRET_BY_SLUG[ref]['no']} — {SECRET_BY_SLUG[ref]['title']}"
        else:
            title = "Real-Life Challenge — " + next(c["title"] for c in REAL_CASES if c["slug"] == ref)
        self.log("misi rahasia" if kind == "secret" else "kehidupan nyata", title, ref=ref, score=score, xp=xp,
                 status="tuntas" if passed else "belum tuntas", meta={"points": correct * 100})
        return {"score": score, "passed": passed, "points": correct * 100, "xp_awarded": xp, "first_completion": first_completion,
                "new_achievements": self.evaluate_achievements()}

    # ---- rekomendasi belajar
    def topic_accuracy(self) -> Dict[str, dict]:
        """Akurasi per topik dari semua jawaban yang benar-benar tersimpan (kuis, latihan, evaluasi, asesmen)."""
        acc: Dict[str, dict] = {}

        def add(qid, ok):
            q = QUESTION_BY_ID.get(qid)
            if not q:
                return
            t = acc.setdefault(q.get("topic", "umum"), {"correct": 0, "total": 0})
            t["total"] += 1
            t["correct"] += int(bool(ok))

        for a in self._svc("quiz_attempts", order="created_at.desc", limit=120):
            for item in a.get("answers") or []:
                if isinstance(item, dict):
                    add(item.get("id"), item.get("ok"))
        for a in self.assessments():
            for item in a.get("answers") or []:
                if isinstance(item, dict):
                    add(item.get("id"), item.get("ok"))
        for t in acc.values():
            t["percent"] = round(t["correct"] * 100 / t["total"]) if t["total"] else 0
        return acc

    def recommendations(self, summary: Optional[dict] = None) -> List[dict]:
        summary = summary or self.summary()
        recs: List[dict] = []
        v2 = self.v2_ready()
        if v2 and not self.first_assessment("pretest"):
            recs.append({"icon": "target", "title": "Kerjakan Pre-Test dulu", "url": "/pretest", "cta": "Mulai Pre-Test",
                         "text": "10 soal singkat untuk mengetahui kemampuan awalmu. Nilainya tidak mengunci materi apa pun."})
        acc = self.topic_accuracy()
        weak = sorted((v["percent"], k) for k, v in acc.items() if v["total"] >= 2 and v["percent"] < 60)
        for pct, topic in weak[:2]:
            lesson = LESSON_BY_SLUG.get(TOPIC_LESSON.get(topic, ""))
            if lesson:
                recs.append({"icon": lesson["icon"], "title": f"Perkuat: {TOPIC_LABELS.get(topic, topic)}",
                             "url": f"/mission/{lesson['slug']}", "cta": f"Ulangi Mission {lesson['no']:02d}",
                             "text": f"Akurasimu di topik ini baru {pct}%. Baca ulang materi {lesson['region']} dan coba latihannya lagi."})
        if v2:
            open_mistakes = [m for m in self.mistakes() if m.get("status") != "dikuasai"]
            if open_mistakes:
                recs.append({"icon": "book", "title": f"{len(open_mistakes)} soal menunggu di Mistake Notebook", "url": "/mistakes",
                             "cta": "Latih soal serupa", "text": "Belajar dari kesalahan adalah jalan tercepat menjadi ahli. Kerjakan soal serupa sampai dikuasai."})
        strong = [k for k, v in acc.items() if v["total"] >= 3 and v["percent"] >= 85]
        nxt = summary.get("next_lesson")
        if nxt:
            why = f"Kamu sudah menguasai {TOPIC_LABELS.get(strong[0], strong[0])}. " if strong else ""
            recs.append({"icon": nxt["icon"], "title": f"Lanjutkan Mission {nxt['no']:02d}: {nxt['region']}", "url": f"/mission/{nxt['slug']}",
                         "cta": "Lanjutkan misi", "text": why + f"Materi berikutnya: {nxt['title']}."})
        elif "scarline-champion" not in summary.get("earned", {}):
            recs.append({"icon": "trophy", "title": "Taklukkan Final Line Challenge", "url": "/final", "cta": "Ke Final",
                         "text": "Ketujuh misi sudah selesai. Saatnya evaluasi akhir — nilai lulus 70."})
        elif v2 and not self.latest_assessment("posttest"):
            recs.append({"icon": "growth", "title": "Kerjakan Post-Test", "url": "/posttest", "cta": "Mulai Post-Test",
                         "text": "Bandingkan kemampuanmu sekarang dengan saat pre-test."})
        else:
            recs.append({"icon": "crown", "title": "Tantangan lanjutan", "url": "/secret", "cta": "Buka Secret Mission",
                         "text": "Kamu sudah menguasai materi utama! Coba Secret Mission dan game tingkat Sulit untuk menjadi Master of Straight Lines."})
        return recs[:4]

    # ---- sertifikat
    def certificate(self, summary: Optional[dict] = None) -> dict:
        summary = summary or self.summary()
        post = self.latest_assessment("posttest")
        done_all = len(summary["done"]) == len(LESSON_ORDER)
        need = []
        if not done_all:
            need.append(f"Selesaikan ketujuh misi ({len(summary['done'])}/7).")
        if not post:
            need.append("Kerjakan Post-Test.")
        if not post or not done_all:
            return {"eligible": False, "need": need}
        score = int(post["score"])
        earned = summary.get("earned", {})
        if "master-of-straight-lines" in earned and score >= 85:
            title = "Master of Straight Lines"
        elif score >= FINAL_PASS_SCORE or "scarline-champion" in earned:
            title = "SCARLINE Champion"
        else:
            title = "Line Explorer"
        return {"eligible": True, "score": score, "title": title, "date": post["created_at"], "need": []}

    # ------------------------------------------------------------ history/dashboard
    def activity(self, limit: int = 30) -> List[dict]:
        return self._mine("activity_logs", order="created_at.desc", limit=limit)

    def quiz_history(self, limit: int = 30) -> List[dict]:
        return self._mine("quiz_attempts", order="created_at.desc", limit=limit)

    def game_history(self, limit: int = 30) -> List[dict]:
        return self._mine("game_attempts", order="created_at.desc", limit=limit)

    def summary(self) -> dict:
        stats = self.stats()
        progress = self.lesson_progress()
        done = [s for s in LESSON_ORDER if progress.get(s, {}).get("status") == "completed"]
        earned = self.earned_achievements()
        games = self.game_history(200)
        best_by_game = {}
        for g in games:
            best_by_game[g["game_slug"]] = max(best_by_game.get(g["game_slug"], 0), float(g.get("percent") or 0))
        next_slug = next((s for s in LESSON_ORDER if s not in done), None)
        return {
            "stats": stats,
            "level": level_for_xp(stats.get("total_xp", 0)),
            "progress": progress,
            "done": done,
            "percent": round(len(done) * 100 / len(LESSON_ORDER)),
            "earned": earned,
            "achievements": [{**a, "earned": a["slug"] in earned, "earned_at": earned.get(a["slug"], {}).get("earned_at")} for a in ACHIEVEMENTS],
            "best_by_game": best_by_game,
            "games_finished": len(best_by_game),
            "next_lesson": LESSON_BY_SLUG.get(next_slug) if next_slug else None,
            "final_unlocked": len(done) == len(LESSON_ORDER),
        }


def achievement_info(slug: str) -> dict:
    return ACHIEVEMENT_BY_SLUG.get(slug, {})
