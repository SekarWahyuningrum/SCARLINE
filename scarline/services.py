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

from datetime import datetime, timezone
from typing import Dict, List, Optional

from .content import ACHIEVEMENT_BY_SLUG, ACHIEVEMENTS, LESSON_BY_SLUG, LESSON_ORDER, level_for_xp
from .games import DIFFICULTIES, GAME_BY_SLUG
from .supabase_client import SupabaseError

LESSON_PASS_SCORE = 60  # mini quiz: minimal 2 dari 3 benar
FINAL_PASS_SCORE = 70


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
        }
        new = []
        for ach in ACHIEVEMENTS:
            slug = ach["slug"]
            if rules.get(slug) and slug not in have:
                inserted = self.db.upsert("user_achievements", {"user_id": self.user_id, "achievement_slug": slug},
                                          on_conflict="user_id,achievement_slug", ignore_duplicates=True)
                if inserted:
                    self._bump(ach["xp_bonus"])
                    self.log("lencana", f"Mendapat lencana {ach['title']}", ref=slug, xp=ach["xp_bonus"], status="diperoleh")
                    new.append({"slug": slug, "title": ach["title"], "description": ach["description"], "icon": ach["icon"], "xp_bonus": ach["xp_bonus"]})
        return new

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
