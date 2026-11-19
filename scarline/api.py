"""API JSON: sesi aktivitas (kuis/latihan/evaluasi/game), penyelesaian misi, dan kalkulator Lab."""
from __future__ import annotations

from flask import Blueprint, current_app, g, jsonify, request

from . import mathcore
from .content import (
    ASSESSMENT_TITLES,
    LESSON_BY_SLUG,
    LESSON_ORDER,
    QUESTION_BY_ID,
    REAL_BY_SLUG,
    SECRET_BY_SLUG,
    TRAINING_LEVELS,
    level_for_xp,
)
from .content.scar import say
from .games import DIFFICULTIES, GAME_BY_SLUG, V2_GAMES
from .mathcore import MathInputError
from .runs import (
    EXAM_KINDS,
    RunError,
    build_items,
    create_run,
    drop_run,
    get_run,
    public_payload,
    submit_answer,
    summarize,
    today_jakarta,
    training_title,
    user_answer_text,
)
from .security import api_login_required, get_db
from .services import AVATARS, FINAL_PASS_SCORE, LESSON_PASS_SCORE, LearningService, stars_for
from .supabase_client import SupabaseError

bp = Blueprint("api", __name__, url_prefix="/api")


def _svc() -> LearningService:
    return LearningService(get_db(), g.user_id, g.token)


def _err(msg: str, status: int = 400):
    return jsonify({"error": msg}), status


V2_MSG = "Fitur ini belum aktif: admin perlu menjalankan migrasi database 002_scarline_features.sql di Supabase (lihat README)."


def _need_v2(svc: LearningService):
    return None if svc.v2_ready() else _err(V2_MSG, 503)


@bp.errorhandler(RunError)
def _run_error(exc: RunError):
    return _err(str(exc), exc.status)


@bp.errorhandler(SupabaseError)
def _sb_error(exc: SupabaseError):
    current_app.logger.warning("Supabase error: %s (%s)", exc, exc.status)
    return _err(exc.friendly, 503 if exc.status in (0, 503) else 502)


def _stats_payload(svc: LearningService) -> dict:
    st = svc.stats()
    return {"total_xp": st.get("total_xp", 0), "level": level_for_xp(st.get("total_xp", 0))}


# ------------------------------------------------------------------ runs
@bp.post("/runs")
@api_login_required
def start_run():
    data = request.get_json(silent=True) or {}
    kind = data.get("kind")
    ref = str(data.get("ref", ""))
    svc = _svc()
    difficulty, count, timer = None, None, None
    extra = {}

    if kind == "lesson":
        if ref not in LESSON_BY_SLUG:
            return _err("Misi tidak ditemukan.", 404)
        if not svc.unlocked(ref, svc.completed_lessons()):
            return _err("Misi ini masih terkunci.", 403)
    elif kind == "training":
        if not ref.isdigit() or int(ref) not in TRAINING_LEVELS:
            return _err("Level latihan tidak valid.")
    elif kind == "daily":
        ref = today_jakarta()
        extra["claimed"] = bool(svc._svc("daily_claims", claim_date=ref, limit=1))
    elif kind == "final":
        done = svc.completed_lessons()
        if len(done) < len(LESSON_ORDER):
            return _err("Final Line Challenge terbuka setelah ketujuh misi selesai.", 403)
        try:
            count = int(data.get("count", 15))
        except (TypeError, ValueError):
            count = 15
        if count not in current_app.config["FINAL_QUESTION_OPTIONS"]:
            return _err("Jumlah soal tidak valid.")
        if data.get("timer"):
            timer = int(count * 90)  # 1,5 menit per soal
        ref = "final-challenge"
    elif kind in ("pretest", "posttest"):
        if (resp := _need_v2(svc)):
            return resp
        if kind == "posttest" and not svc.posttest_unlocked():
            return _err("Post-test terbuka setelah kamu menyelesaikan ketujuh misi dan mengerjakan Final Line Challenge.", 403)
        ref = kind
    elif kind == "secret":
        if (resp := _need_v2(svc)):
            return resp
        if ref not in SECRET_BY_SLUG:
            return _err("Misi rahasia tidak ditemukan.", 404)
        if not svc.secret_unlocked(ref, svc.challenge_map()):
            return _err("Misi rahasia ini masih terkunci. Tuntaskan misi sebelumnya dulu.", 403)
    elif kind == "reallife":
        if (resp := _need_v2(svc)):
            return resp
        if ref not in REAL_BY_SLUG:
            return _err("Studi kasus tidak ditemukan.", 404)
    elif kind == "mistake":
        if (resp := _need_v2(svc)):
            return resp
        row = svc.mistake(ref)
        if not row:
            return _err("Soal ini tidak ada di Mistake Notebook-mu.", 404)
        similar = svc.similar_question(ref, int(row.get("times_wrong") or 0) + int(data.get("attempt") or 0))
        ref = f"{ref}|{similar['id']}"
    elif kind == "game":
        if ref not in GAME_BY_SLUG:
            return _err("Game tidak ditemukan.", 404)
        if ref in V2_GAMES and (resp := _need_v2(svc)):
            return resp
        difficulty = data.get("difficulty", "easy")
        if difficulty not in DIFFICULTIES:
            return _err("Tingkat kesulitan tidak valid.")
    else:
        return _err("Jenis aktivitas tidak dikenal.")

    run_id, run = create_run(g.user_id, kind, ref, difficulty=difficulty, count=count, timer=timer)
    payload = public_payload(run_id, run)
    payload.update(extra)
    payload["scar"] = say("welcome")
    return jsonify(payload)


@bp.post("/runs/<run_id>/answer")
@api_login_required
def answer(run_id):
    data = request.get_json(silent=True) or {}
    run = get_run(run_id, g.user_id)
    try:
        index = int(data.get("index"))
    except (TypeError, ValueError):
        return _err("Nomor soal tidak valid.")
    result = submit_answer(run_id, run, index, data.get("answer"))
    if result.get("invalid"):
        return jsonify(result), 422
    if run["k"] != "game" and result.get("done"):
        q = build_items(run)[index]["q"]
        svc = _svc()
        if run["k"] == "mistake":
            original = run["r"].split("|")[0]
            if result["correct"]:
                svc.master_mistake(original)
                result["mastered"] = True
        elif not result["correct"] and svc.v2_ready():
            svc.record_mistake(q["id"], user_answer_text(q, data.get("answer")), run["k"])
            result["saved_mistake"] = True
    return jsonify(result)


@bp.post("/runs/<run_id>/finish")
@api_login_required
def finish(run_id):
    data = request.get_json(silent=True) or {}
    run = get_run(run_id, g.user_id)
    svc = _svc()
    answers = data.get("answers") if isinstance(data.get("answers"), dict) else None
    result = summarize(run, answers)
    kind, ref = run["k"], run["r"]
    payload = {"kind": kind, "correct": result["correct"], "total": result["total"], "duration": result["duration"]}

    if kind == "game":
        saved = svc.record_game(slug=ref, difficulty=run["d"], score=result["score"], max_score=result["max_score"],
                                rounds_correct=result["correct"], rounds_total=result["total"], duration=result["duration"])
        payload.update({"score": result["score"], "max_score": result["max_score"], **saved})
        payload["scar"] = say("celebrate") if saved["percent"] >= 70 else say("encourage")
    else:
        if kind == "lesson":
            lesson = LESSON_BY_SLUG[ref]
            saved = svc.record_quiz(quiz_slug=f"lesson-{ref}", kind="lesson", title=f"Mini quiz Mission {lesson['no']:02d} — {lesson['region']}",
                                    correct=result["correct"], total=result["total"], duration=result["duration"], answers=result["answers_log"])
            saved["passed"] = saved["score"] >= LESSON_PASS_SCORE
        elif kind == "training":
            level = int(ref)
            saved = svc.record_quiz(quiz_slug=f"training-{level}", kind="training", title=training_title(level),
                                    correct=result["correct"], total=result["total"], duration=result["duration"], answers=result["answers_log"])
        elif kind == "daily":
            saved = svc.record_quiz(quiz_slug="daily", kind="daily", title=f"Tantangan Harian {ref}", correct=result["correct"],
                                    total=result["total"], duration=result["duration"], answers=result["answers_log"])
            claim = svc.claim_daily(ref, result["correct"], result["total"])
            saved["xp_awarded"] = claim["xp_awarded"]
            saved["already_claimed"] = claim["already"]
            saved["new_achievements"] = saved["new_achievements"] + claim["new_achievements"]
        elif kind in ("pretest", "posttest"):
            saved = svc.record_assessment(kind, correct=result["correct"], total=result["total"], duration=result["duration"],
                                          review=result["review"], answers=result["answers_log"])
            payload["review"] = result["review"]
            payload["title"] = ASSESSMENT_TITLES[kind]
            if kind == "posttest":
                payload["comparison"] = svc.comparison()
        elif kind in ("secret", "reallife"):
            saved = svc.record_challenge(kind, ref, result["correct"], result["total"])
        elif kind == "mistake":
            saved = {"score": round(result["correct"] * 100 / result["total"]), "xp_awarded": 0, "new_achievements": []}
        else:  # final
            saved = svc.record_quiz(quiz_slug="final-challenge", kind="final", title="Final Line Challenge", correct=result["correct"],
                                    total=result["total"], duration=result["duration"], answers=result["answers_log"],
                                    meta={"count": run["n"], "timer": bool(run.get("tm"))})
            saved["passed"] = saved["score"] >= FINAL_PASS_SCORE
            payload["review"] = result["review"]
            for rv in result["review"]:
                if not rv["correct"]:
                    svc.record_mistake(rv["id"], rv["your_answer"], "final")
        payload.update(saved)
        payload["scar"] = say("celebrate") if saved["score"] >= 70 else say("encourage")
    payload["stars"] = payload.get("stars", stars_for(payload.get("percent", payload.get("score", 0))))
    payload["stats"] = _stats_payload(svc)
    drop_run(run_id)
    return jsonify(payload)


# ------------------------------------------------------------------ lessons
@bp.post("/lessons/<slug>/complete")
@api_login_required
def complete_lesson(slug):
    if slug not in LESSON_BY_SLUG:
        return _err("Misi tidak ditemukan.", 404)
    svc = _svc()
    res = svc.complete_lesson(slug)
    if not res.get("ok"):
        return _err(res["error"], 403)
    res["stats"] = _stats_payload(svc)
    res["scar"] = say("mission_done")
    return jsonify(res)


# ------------------------------------------------------------------ lab
@bp.post("/lab/calc")
@api_login_required
def lab_calc():
    data = request.get_json(silent=True) or {}
    method = data.get("method")
    try:
        if method == "point-slope":
            res = mathcore.from_point_slope(data.get("m"), (data.get("x1"), data.get("y1")))
        elif method == "two-points":
            res = mathcore.from_two_points((data.get("x1"), data.get("y1")), (data.get("x2"), data.get("y2")))
        elif method == "slope-intercept":
            res = mathcore.from_slope_intercept(data.get("m"), data.get("c"))
        elif method == "gradient":
            res = mathcore.gradient_steps((data.get("x1"), data.get("y1")), (data.get("x2"), data.get("y2")))
        elif method == "origin":
            res = mathcore.through_origin(data.get("m"))
        else:
            return _err("Metode tidak dikenal.")
    except MathInputError as exc:
        return _err(str(exc), 422)
    for key in ("m_value", "c_value", "x_value"):
        if key in res and abs(res[key]) > 1e6:
            return _err("Angka terlalu besar untuk digambar. Gunakan angka yang lebih kecil.", 422)
    return jsonify(res)


# ------------------------------------------------------------------ SCAR AI Tutor
TUTOR_LIMIT = 40          # pesan per jam per sesi (mengendalikan biaya API)


@bp.post("/tutor")
@api_login_required
def tutor_chat():
    import time

    from flask import session

    from . import tutor

    data = request.get_json(silent=True) or {}
    message = str(data.get("message") or "").strip()
    if not message:
        return _err("Tulis pertanyaanmu dulu, ya!")
    if len(message) > tutor.MAX_CHARS:
        return _err(f"Pertanyaan terlalu panjang (maksimal {tutor.MAX_CHARS} karakter).")
    now = time.time()
    stamps = [t for t in session.get("tutor_ts", []) if now - t < 3600]
    if len(stamps) >= TUTOR_LIMIT:
        return _err("SCAR perlu istirahat sebentar. Kamu sudah bertanya banyak sekali dalam satu jam terakhir — coba lagi nanti, ya!", 429)
    session["tutor_ts"] = stamps + [now]
    cfg = current_app.config
    out = tutor.answer(message, data.get("history"), str(data.get("mode") or "tanya"), str(data.get("context") or ""),
                       cfg.get("ANTHROPIC_API_KEY"), cfg.get("TUTOR_MODEL"))
    if out.pop("error_type", None):
        current_app.logger.warning("Tutor AI gagal, memakai tutor dasar.")
    return jsonify(out)


# ------------------------------------------------------------------ SCAR's Diary
@bp.post("/diary")
@api_login_required
def diary_save():
    svc = _svc()
    if (resp := _need_v2(svc)):
        return resp
    data = request.get_json(silent=True) or {}
    if data.get("delete"):
        if not svc.delete_note(str(data.get("id") or "")):
            return _err("Catatan tidak ditemukan.", 404)
        return jsonify({"ok": True, "deleted": True})
    title = " ".join(str(data.get("title") or "").split())[:80]
    body = str(data.get("body") or "").strip()
    lesson = data.get("lesson_slug") or None
    if not title:
        return _err("Judul catatan wajib diisi.")
    if len(body) > 4000:
        return _err("Isi catatan maksimal 4000 karakter.")
    if lesson and lesson not in LESSON_BY_SLUG:
        return _err("Materi tidak dikenal.")
    note = svc.save_note(title, body, lesson, str(data["id"]) if data.get("id") else None)
    return jsonify({"ok": True, "note": note})


# ------------------------------------------------------------------ preferensi
@bp.post("/prefs")
@api_login_required
def save_prefs():
    svc = _svc()
    if (resp := _need_v2(svc)):
        return resp
    data = request.get_json(silent=True) or {}
    values = {}
    if data.get("theme") in ("light", "dark", "system"):
        values["theme"] = data["theme"]
    for key in ("music", "sfx", "reduce_motion"):
        if isinstance(data.get(key), bool):
            values[key] = data[key]
    if data.get("avatar") in AVATARS:
        values["avatar"] = data["avatar"]
    if "reminder_time" in data:
        rt = data.get("reminder_time")
        if rt and not (isinstance(rt, str) and len(rt) == 5 and rt[2] == ":" and rt[:2].isdigit() and rt[3:].isdigit()
                       and int(rt[:2]) < 24 and int(rt[3:]) < 60):
            return _err("Format jam pengingat harus HH:MM.")
        values["reminder_time"] = rt or None
    prefs = svc.save_prefs({**svc.prefs(), **values})
    return jsonify({"ok": True, "prefs": {k: prefs.get(k) for k in LearningService.DEFAULT_PREFS}})


@bp.post("/bookmark")
@api_login_required
def bookmark():
    svc = _svc()
    if (resp := _need_v2(svc)):
        return resp
    data = request.get_json(silent=True) or {}
    slug = data.get("slug")
    key = "favorites" if data.get("list") == "favorites" else "bookmarks"
    if slug not in LESSON_BY_SLUG:
        return _err("Materi tidak dikenal.", 404)
    on = svc.toggle_list_pref(key, slug)
    return jsonify({"ok": True, "on": on, "list": key})
