"""Sesi aktivitas (run) untuk kuis, latihan, tantangan harian, evaluasi, dan game.

Server membuat soal/ronde dari *seed* acak dan menyimpannya di cookie sesi
yang ditandatangani. Browser hanya menerima data publik (tanpa kunci).
Setiap jawaban dinilai di server, sehingga skor tidak bisa dimanipulasi.
"""
from __future__ import annotations

import secrets
import time
from datetime import datetime, timedelta, timezone
from random import Random
from typing import Optional

from flask import session

from .content import FINAL_BANK, FINAL_TOPICS, LESSON_QUIZZES, TRAINING_BANK, TRAINING_LEVELS
from .content.scar import say
from .games import GAME_BY_SLUG
from .grading import answer_display, grade, public_question
from .mathcore import MathInputError

MAX_RUNS = 4
POINTS_BY_TRY = {1: 100, 2: 60, 3: 30}
JAKARTA = timezone(timedelta(hours=7))


class RunError(Exception):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.status = status


def today_jakarta() -> str:
    return datetime.now(JAKARTA).date().isoformat()


# ---------------------------------------------------------------- item builders
def daily_questions(day: str) -> list:
    rng = Random(f"scarline-daily-{day}")
    return [rng.choice(TRAINING_BANK[level]) for level in (1, 2, 3)]


def final_questions(seed: int, count: int) -> list:
    rng = Random(seed)
    groups = {t: [q for q in FINAL_BANK if q["topic"] == t] for t in FINAL_TOPICS}
    for g in groups.values():
        rng.shuffle(g)
    picked = []
    while len(picked) < min(count, len(FINAL_BANK)):
        for t in FINAL_TOPICS:
            if groups[t] and len(picked) < count:
                picked.append(groups[t].pop())
    picked.sort(key=lambda q: FINAL_TOPICS.index(q["topic"]))
    return picked


def build_items(run: dict) -> list:
    kind, ref = run["k"], run["r"]
    if kind == "lesson":
        return [{"public": public_question(q), "q": q} for q in LESSON_QUIZZES[ref]]
    if kind == "training":
        qs = list(TRAINING_BANK[int(ref)])
        Random(run["s"]).shuffle(qs)
        return [{"public": public_question(q), "q": q} for q in qs]
    if kind == "daily":
        return [{"public": public_question(q), "q": q} for q in daily_questions(ref)]
    if kind == "final":
        return [{"public": public_question(q), "q": q} for q in final_questions(run["s"], run["n"])]
    if kind == "game":
        rounds = GAME_BY_SLUG[ref].generate(Random(run["s"]), run["d"])
        return [{"public": r["public"], "round": r, "q": r.get("q")} for r in rounds]
    raise RunError("Jenis aktivitas tidak dikenal.")


# ---------------------------------------------------------------- session store
def _store() -> dict:
    runs = session.get("runs")
    if not isinstance(runs, dict):
        runs = {}
    return runs


def _save(runs: dict) -> None:
    session["runs"] = runs
    session.modified = True


def create_run(user_id: str, kind: str, ref: str, *, difficulty: Optional[str] = None,
               count: Optional[int] = None, timer: Optional[int] = None) -> tuple:
    run = {"u": user_id, "k": kind, "r": str(ref), "s": secrets.randbelow(2**31), "d": difficulty, "n": count,
           "tm": timer, "t0": time.time(), "tl": time.time(), "res": {}, "hearts": None}
    if kind == "game":
        info = GAME_BY_SLUG[ref].INFO
        if info.get("hearts"):
            run["hearts"] = info["hearts"]
    runs = _store()
    while len(runs) >= MAX_RUNS:
        oldest = min(runs, key=lambda k: runs[k].get("t0", 0))
        runs.pop(oldest)
    run_id = secrets.token_urlsafe(8)
    runs[run_id] = run
    _save(runs)
    return run_id, run


def get_run(run_id: str, user_id: str) -> dict:
    run = _store().get(run_id)
    if not run or run.get("u") != user_id:
        raise RunError("Sesi aktivitas tidak ditemukan atau sudah selesai. Mulai lagi, ya!", 404)
    return run


def drop_run(run_id: str) -> None:
    runs = _store()
    runs.pop(run_id, None)
    _save(runs)


def public_payload(run_id: str, run: dict) -> dict:
    items = build_items(run)
    payload = {"run_id": run_id, "kind": run["k"], "ref": run["r"], "difficulty": run["d"], "total": len(items),
               "items": [it["public"] for it in items], "timer": run.get("tm")}
    if run["k"] == "game":
        info = GAME_BY_SLUG[run["r"]].INFO
        payload["max_tries"] = info.get("max_tries", 3)
        payload["hearts"] = run.get("hearts")
    return payload


# ---------------------------------------------------------------- answering
def _grade_item(item: dict, answer, game_slug: Optional[str] = None) -> dict:
    if item.get("q") is not None:
        return grade(item["q"], answer)
    rnd = item["round"]
    res = GAME_BY_SLUG[game_slug].check(rnd, answer)
    res.setdefault("explain", rnd.get("hint", ""))
    res["answer_display"] = rnd.get("solution", "")
    return res


def submit_answer(run_id: str, run: dict, index: int, answer) -> dict:
    if run["k"] == "final":
        raise RunError("Jawaban evaluasi dikirim sekaligus saat menyelesaikan evaluasi.")
    items = build_items(run)
    if not isinstance(index, int) or not 0 <= index < len(items):
        raise RunError("Nomor soal tidak valid.")
    key = str(index)
    state = run["res"].get(key) or [0, 0, 0, 0]  # correct, tries, points, done
    if state[3]:
        raise RunError("Soal ini sudah selesai dijawab.")
    if run.get("hearts") is not None and run["hearts"] <= 0:
        raise RunError("Nyawa habis. Permainan sudah berakhir.")

    try:
        result = _grade_item(items[index], answer, run["r"] if run["k"] == "game" else None)
    except MathInputError as exc:
        return {"invalid": True, "message": str(exc)}

    now = time.time()
    state[1] += 1
    tries = state[1]
    is_game = run["k"] == "game"
    info = GAME_BY_SLUG[run["r"]].INFO if is_game else {}
    max_tries = info.get("max_tries", 3) if is_game else 1
    bonus = 0
    if result["correct"]:
        state[0] = 1
        state[3] = 1
        if is_game and info.get("hearts"):
            state[2] = 100 if tries == 1 else 50
        elif is_game:
            state[2] = POINTS_BY_TRY.get(tries, 0)
            if info.get("speed_bonus") and tries == 1:
                elapsed = now - run.get("tl", now)
                bonus = int(max(0, min(1, (20 - elapsed) / 14)) * info["speed_bonus"])
                state[2] += bonus
        else:
            state[2] = 1
    else:
        if is_game and info.get("hearts"):
            run["hearts"] = max(0, run["hearts"] - 1)
        elif tries >= max_tries:
            state[3] = 1
    if state[3]:
        run["tl"] = now
    run["res"][key] = state
    runs = _store()
    runs[run_id] = run
    _save(runs)

    game_over = bool(is_game and info.get("hearts") and run["hearts"] <= 0)
    done = bool(state[3])
    reveal = done or game_over
    out = {
        "correct": result["correct"],
        "feedback": result.get("feedback", ""),
        "scar": say("correct") if result["correct"] else (say("encourage") if reveal else say("wrong")),
        "done": done,
        "tries": tries,
        "tries_left": None if info.get("hearts") else max(0, max_tries - tries),
        "points": state[2],
        "bonus": bonus,
        "score": sum(v[2] for v in run["res"].values()) if is_game else sum(v[0] for v in run["res"].values()),
        "hearts": run.get("hearts"),
        "game_over": game_over,
    }
    if reveal:
        out["explain"] = result.get("explain", "")
        out["answer_display"] = result.get("answer_display", "")
    if not is_game:
        out["explain"] = result.get("explain", "")
        out["answer_display"] = result.get("answer_display", "")
    return out


# ---------------------------------------------------------------- finishing
def summarize(run: dict, answers: Optional[dict] = None) -> dict:
    """Hitung hasil akhir. Untuk evaluasi akhir, ``answers`` = {index: jawaban}."""
    items = build_items(run)
    duration = int(time.time() - run["t0"])
    total = len(items)
    if run["k"] == "final":
        answers = answers or {}
        review = []
        correct = 0
        for i, it in enumerate(items):
            q = it["q"]
            raw = answers.get(str(i))
            ok, user_txt = False, "—"
            if raw is not None and raw != "":
                try:
                    ok = grade(q, raw)["correct"]
                    user_txt = _user_answer_text(q, raw)
                except MathInputError:
                    ok, user_txt = False, "(format tidak valid)"
            correct += int(ok)
            review.append({"index": i, "prompt": q["prompt"], "topic": q["topic"], "correct": ok, "your_answer": user_txt,
                           "answer_display": answer_display(q), "explain": q.get("explain", ""), "graph": q.get("graph"),
                           "type": q["type"]})
        return {"total": total, "correct": correct, "duration": duration, "review": review,
                "answers_log": [{"id": it["q"]["id"], "ok": r["correct"]} for it, r in zip(items, review)]}

    res = run["res"]
    correct = sum(1 for i in range(total) if res.get(str(i), [0])[0])
    out = {"total": total, "correct": correct, "duration": duration,
           "answers_log": [{"id": (it["q"] or {}).get("id", f"r{i}"), "ok": bool(res.get(str(i), [0])[0])} for i, it in enumerate(items)]}
    if run["k"] == "game":
        info = GAME_BY_SLUG[run["r"]].INFO
        per_round = 100 + (info.get("speed_bonus") or 0)
        out["score"] = sum(res.get(str(i), [0, 0, 0])[2] for i in range(total))
        out["max_score"] = per_round * total
    return out


def _user_answer_text(q: dict, raw) -> str:
    try:
        if q["type"] == "mc":
            return q["options"][int(raw)]
        if q["type"] == "tf":
            return "Benar" if raw in (True, "true") else "Salah"
        if q["type"] == "point":
            return f"({raw[0]}, {raw[1]})"
        if q["type"] == "line":
            return f"y = ({raw.get('m')})x + ({raw.get('c')})"
        if q["type"] == "match":
            return f"{len(raw)} pasangan"
    except (TypeError, ValueError, IndexError, KeyError, AttributeError):
        return "(format tidak valid)"
    return str(raw)


def training_title(level: int) -> str:
    return f"Training Level {level} — {TRAINING_LEVELS[level]['name']}"
