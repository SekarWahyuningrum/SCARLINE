"""Halaman SCARLINE (landing + halaman privat)."""
from __future__ import annotations

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from .auth import CLASS_RE, NAME_RE
from .content import (
    ACHIEVEMENTS,
    LESSON_BY_SLUG,
    LESSON_ORDER,
    LESSON_QUIZZES,
    LESSONS,
    TOPIC_LABELS,
    TRAINING_BANK,
    TRAINING_LEVELS,
    level_for_xp,
    next_lesson,
    prev_lesson,
)
from .content.scar import say
from .games import DIFFICULTIES, GAME_BY_SLUG, GAMES
from .runs import daily_questions, today_jakarta
from .security import current_auth, get_db, login_required
from .services import FINAL_PASS_SCORE, LESSON_PASS_SCORE, LearningService

bp = Blueprint("pages", __name__)


def _svc() -> LearningService:
    return LearningService(get_db(), g.user_id, g.token)


def _base(svc: LearningService) -> dict:
    profile = svc.profile() or {"full_name": "Line Explorer", "username": "explorer", "class_name": "-", "email": g.email}
    stats = svc.stats()
    g.header = {"profile": profile, "level": level_for_xp(stats.get("total_xp", 0))}
    return {"profile": profile, "stats": stats}


@bp.route("/")
def landing():
    return render_template("pages/landing.html", lessons=LESSONS, games=GAMES, logged_in=bool(current_auth()))


@bp.route("/dashboard")
@login_required
def dashboard():
    svc = _svc()
    ctx = _base(svc)
    summary = svc.summary()
    recent = svc.activity(6)
    day = today_jakarta()
    claimed = bool(svc._svc("daily_claims", claim_date=day, limit=1))
    return render_template(
        "pages/dashboard.html", **ctx, summary=summary, recent=recent, lessons=LESSONS, daily_claimed=claimed,
        greeting=say("welcome"),
    )


@bp.route("/map")
@login_required
def adventure_map():
    svc = _svc()
    ctx = _base(svc)
    summary = svc.summary()
    return render_template("pages/map.html", **ctx, summary=summary, lessons=LESSONS)


@bp.route("/mission/<slug>")
@login_required
def mission(slug):
    lesson = LESSON_BY_SLUG.get(slug)
    if not lesson:
        abort(404)
    svc = _svc()
    ctx = _base(svc)
    completed = svc.completed_lessons()
    if not svc.unlocked(slug, completed):
        prev = prev_lesson(slug)
        flash(f"Mission {lesson['no']:02d} masih terkunci. Selesaikan dulu Mission {prev['no']:02d} — {prev['region']}.", "info")
        return redirect(url_for("pages.adventure_map"))
    svc.open_lesson(slug)
    best = svc.best_lesson_quiz(slug)
    return render_template(
        "pages/mission.html", **ctx, lesson=lesson, completed=slug in completed, quiz_best=best,
        quiz_passed=best >= LESSON_PASS_SCORE, quiz_count=len(LESSON_QUIZZES[slug]), next_lesson=next_lesson(slug),
        prev_lesson=prev_lesson(slug), total=len(LESSONS),
    )


@bp.route("/lab")
@login_required
def lab():
    ctx = _base(_svc())
    return render_template("pages/lab.html", **ctx)


@bp.route("/training")
@login_required
def training():
    svc = _svc()
    ctx = _base(svc)
    attempts = svc.quiz_history(100)
    best = {}
    for a in attempts:
        if a["quiz_slug"].startswith("training-"):
            lvl = int(a["quiz_slug"].split("-")[1])
            best[lvl] = max(best.get(lvl, 0), int(a["score"]))
    return render_template("pages/training.html", **ctx, levels=TRAINING_LEVELS, bank=TRAINING_BANK, best=best)


@bp.route("/training/<int:level>")
@login_required
def training_level(level):
    if level not in TRAINING_LEVELS:
        abort(404)
    ctx = _base(_svc())
    return render_template("pages/quiz_run.html", **ctx, kind="training", ref=level,
                           title=f"Level {level} — {TRAINING_LEVELS[level]['name']}", subtitle=TRAINING_LEVELS[level]["desc"],
                           back_url=url_for("pages.training"))


@bp.route("/daily")
@login_required
def daily():
    svc = _svc()
    ctx = _base(svc)
    day = today_jakarta()
    claimed = bool(svc._svc("daily_claims", claim_date=day, limit=1))
    return render_template("pages/quiz_run.html", **ctx, kind="daily", ref=day, title="Tantangan Harian",
                           subtitle=f"3 soal spesial untuk hari ini ({day}). XP diberikan sekali per hari." + (" Kamu sudah mengklaim XP hari ini — tetap boleh berlatih!" if claimed else ""),
                           back_url=url_for("pages.dashboard"), count=len(daily_questions(day)))


@bp.route("/playground")
@login_required
def playground():
    svc = _svc()
    ctx = _base(svc)
    summary = svc.summary()
    return render_template("pages/playground.html", **ctx, games=GAMES, best=summary["best_by_game"])


@bp.route("/playground/<slug>")
@login_required
def game(slug):
    module = GAME_BY_SLUG.get(slug)
    if not module:
        abort(404)
    svc = _svc()
    ctx = _base(svc)
    history = [a for a in svc.game_history(100) if a["game_slug"] == slug][:5]
    return render_template("pages/game.html", **ctx, info=module.INFO, difficulties=DIFFICULTIES, history=history)


@bp.route("/final")
@login_required
def final():
    svc = _svc()
    ctx = _base(svc)
    summary = svc.summary()
    history = [a for a in svc.quiz_history(100) if a["quiz_slug"] == "final-challenge"]
    from flask import current_app

    return render_template("pages/final.html", **ctx, summary=summary, history=history, options=current_app.config["FINAL_QUESTION_OPTIONS"],
                           pass_score=FINAL_PASS_SCORE, topics=TOPIC_LABELS)


@bp.route("/achievements")
@login_required
def achievements():
    svc = _svc()
    ctx = _base(svc)
    summary = svc.summary()
    return render_template("pages/achievements.html", **ctx, summary=summary, all=ACHIEVEMENTS)


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    svc = _svc()
    errors = {}
    if request.method == "POST":
        full_name = " ".join((request.form.get("full_name") or "").split())
        class_name = " ".join((request.form.get("class_name") or "").split())
        if not NAME_RE.match(full_name):
            errors["full_name"] = "Nama lengkap 3–60 huruf."
        if not CLASS_RE.match(class_name):
            errors["class_name"] = "Kelas 1–20 karakter, misalnya VIII-A."
        if not errors:
            svc.update_profile(full_name, class_name)
            flash("Profil berhasil diperbarui.", "success")
            return redirect(url_for("pages.profile"))
        flash("Periksa kembali isian profil.", "error")
    ctx = _base(svc)
    summary = svc.summary()
    finals = [a for a in svc.quiz_history(200) if a["quiz_slug"] == "final-challenge"]
    return render_template("pages/profile.html", **ctx, summary=summary, errors=errors, finals_count=len(finals))


@bp.route("/history")
@login_required
def history():
    svc = _svc()
    ctx = _base(svc)
    kind = request.args.get("type", "")
    logs = svc.activity(150)
    types = sorted({row["activity_type"] for row in logs})
    if kind:
        logs = [row for row in logs if row["activity_type"] == kind]
    return render_template("pages/history.html", **ctx, logs=logs, types=types, kind=kind,
                           quizzes=svc.quiz_history(30), games=svc.game_history(30), lesson_names={s: LESSON_BY_SLUG[s]["region"] for s in LESSON_ORDER},
                           game_names={k: m.INFO["title"] for k, m in GAME_BY_SLUG.items()})
