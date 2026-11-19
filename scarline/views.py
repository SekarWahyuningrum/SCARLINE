"""Halaman SCARLINE (landing + halaman privat)."""
from __future__ import annotations

from flask import Blueprint, Response, abort, current_app, flash, g, jsonify, redirect, render_template, request, url_for

from .auth import CLASS_RE, NAME_RE
from .content import (
    ACHIEVEMENTS,
    POSTTEST,
    PRETEST,
    QUESTION_BY_ID,
    REAL_BY_SLUG,
    REAL_CASES,
    SECRET_BY_SLUG,
    SECRET_MISSIONS,
    SECRET_PASS,
    TOPIC_LESSON,
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
from .games import DIFFICULTIES, GAME_BY_SLUG, GAMES, V2_GAMES
from .runs import daily_questions, today_jakarta
from .security import current_auth, get_db, login_required
from .services import AVATARS, FINAL_PASS_SCORE, LESSON_PASS_SCORE, MASTERY_SCORE, SOURCE_LABELS, LearningService

bp = Blueprint("pages", __name__)


def _svc() -> LearningService:
    return LearningService(get_db(), g.user_id, g.token)


def _base(svc: LearningService) -> dict:
    profile = svc.profile() or {"full_name": "Line Explorer", "username": "explorer", "class_name": "-", "email": g.email}
    stats = svc.stats()
    g.v2 = svc.v2_ready()
    g.prefs = svc.prefs()
    g.header = {"profile": profile, "level": level_for_xp(stats.get("total_xp", 0)), "prefs": g.prefs}
    return {"profile": profile, "stats": stats, "v2": g.v2, "prefs": g.prefs}


@bp.route("/")
def landing():
    stats = {"missions": len(LESSONS), "games": len(GAMES), "questions": len(QUESTION_BY_ID), "badges": len(ACHIEVEMENTS)}
    auth = current_auth()
    ctx, pre = {}, None
    if auth:
        from .security import _load_identity
        from .supabase_client import SupabaseError

        _load_identity(auth)
        try:
            svc = _svc()
            ctx = _base(svc)
            pre = svc.first_assessment("pretest") if ctx["v2"] else None
        except SupabaseError:
            ctx = {}  # landing tetap tampil walau database sedang bermasalah
    return render_template("pages/landing.html", **ctx, lessons=LESSONS, games=GAMES, logged_in=bool(auth), site_stats=stats,
                           pretest_count=len(PRETEST), pretest_done=pre, topic_labels=TOPIC_LABELS,
                           pretest_topics=_topics(PRETEST))


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
        greeting=say("welcome"), recs=svc.recommendations(summary), streak=svc.streak(), games_total=len(GAMES),
        journey=_journey(svc, summary, ctx["v2"]),
    )


@bp.route("/map")
@login_required
def adventure_map():
    svc = _svc()
    ctx = _base(svc)
    summary = svc.summary()
    return render_template("pages/map.html", **ctx, summary=summary, lessons=LESSONS, journey=_journey(svc, summary, ctx["v2"]))


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
        "pages/mission.html", **ctx, lesson=lesson, bookmarked=slug in (ctx["prefs"].get("bookmarks") or []),
        favorite=slug in (ctx["prefs"].get("favorites") or []), completed=slug in completed, quiz_best=best,
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
    return render_template("pages/playground.html", **ctx, games=GAMES, best=summary["best_by_game"], v2_games=V2_GAMES)


@bp.route("/playground/<slug>")
@login_required
def game(slug):
    module = GAME_BY_SLUG.get(slug)
    if not module:
        abort(404)
    svc = _svc()
    ctx = _base(svc)
    if slug in V2_GAMES and not ctx["v2"]:
        flash("Game ini aktif setelah admin menjalankan migrasi database 002 (lihat README).", "info")
        return redirect(url_for("pages.playground"))
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
    return render_template("pages/profile.html", **ctx, summary=summary, errors=errors, finals_count=len(finals),
                           streak=svc.streak(), pre=svc.first_assessment("pretest"), post=svc.latest_assessment("posttest"),
                           comparison=svc.comparison(), games_hist=svc.game_history(8), avatars=AVATARS,
                           missions=[(LESSON_BY_SLUG[s], summary["progress"][s]) for s in LESSON_ORDER if s in summary["progress"]],
                           game_names={k: m.INFO["title"] for k, m in GAME_BY_SLUG.items()}, certificate=svc.certificate(summary),
                           games_total=len(GAMES))


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


# ====================================================================== fitur v2 (migrasi 002)
FORMULAS = {
    "koordinat": "Titik P(x, y): x = absis (mendatar), y = ordinat (tegak). Kuadran I (+, +), II (−, +), III (−, −), IV (+, −).",
    "titik-garis": "Titik (a, b) terletak pada garis y = mx + c jika b = m·a + c (substitusikan lalu cocokkan).",
    "gradien": "m = (y₂ − y₁) / (x₂ − x₁). Mendatar: m = 0. Tegak: tidak terdefinisi. Dari ax + by + c = 0: m = −a/b.",
    "persamaan": "y = mx + c (m = gradien, c = titik potong sumbu Y) atau bentuk umum ax + by + c = 0.",
    "grafik": "Potong sumbu Y: x = 0 → (0, c). Potong sumbu X: y = 0 → selesaikan nilai x.",
    "menentukan": "Gradien + titik: y − y₁ = m(x − x₁). Dua titik: hitung m dulu, lalu pakai rumus yang sama.",
    "hubungan": "Sejajar: m₁ = m₂. Tegak lurus: m₁ × m₂ = −1 (m₂ = −1/m₁).",
    "kehidupan": "Model linear: nilai awal = c, perubahan per satuan = m. Contoh: Biaya = tarif × jarak + biaya awal.",
}


def _journey(svc: LearningService, summary: dict, v2: bool) -> dict:
    pre = svc.first_assessment("pretest") if v2 else None
    post = svc.latest_assessment("posttest") if v2 else None
    cert = svc.certificate(summary) if v2 else {"eligible": False}
    return {"v2": v2, "pretest_done": bool(pre), "pretest_score": pre["score"] if pre else None,
            "posttest_unlocked": svc.posttest_unlocked(summary), "posttest_done": bool(post),
            "posttest_score": post["score"] if post else None, "champion": cert.get("eligible", False),
            "final_done": int(summary["stats"].get("finals_taken") or 0) > 0}


def _v2_or_notice(ctx: dict, title: str):
    if ctx["v2"]:
        return None
    return render_template("pages/v2_notice.html", **ctx, feature=title)


def _topics(questions):
    order = list(TOPIC_LABELS)
    return sorted({q["topic"] for q in questions}, key=order.index)


@bp.route("/pretest")
@login_required
def pretest():
    svc = _svc()
    ctx = _base(svc)
    if (resp := _v2_or_notice(ctx, "Pre-Test")):
        return resp
    return render_template("pages/assessment.html", **ctx, kind="pretest", count=len(PRETEST), history=svc.assessments("pretest"),
                           locked=False, comparison=None, topics=_topics(PRETEST), topic_labels=TOPIC_LABELS)


@bp.route("/posttest")
@login_required
def posttest():
    svc = _svc()
    ctx = _base(svc)
    if (resp := _v2_or_notice(ctx, "Post-Test")):
        return resp
    summary = svc.summary()
    return render_template("pages/assessment.html", **ctx, kind="posttest", count=len(POSTTEST), history=svc.assessments("posttest"),
                           locked=not svc.posttest_unlocked(summary), summary=summary, comparison=svc.comparison(),
                           topics=_topics(POSTTEST), topic_labels=TOPIC_LABELS)


@bp.route("/progress")
@login_required
def progress():
    svc = _svc()
    ctx = _base(svc)
    if (resp := _v2_or_notice(ctx, "Grafik Perkembangan")):
        return resp
    summary = svc.summary()
    acc = svc.topic_accuracy()
    return render_template("pages/progress.html", **ctx, summary=summary, comparison=svc.comparison(), streak=svc.streak(),
                           pre_hist=svc.assessments("pretest"), post_hist=svc.assessments("posttest"),
                           accuracy=[{"key": k, "label": v, **acc[k]} for k, v in TOPIC_LABELS.items() if k in acc],
                           recs=svc.recommendations(summary), mastery=MASTERY_SCORE, journey=_journey(svc, summary, True))


@bp.route("/diary")
@login_required
def diary():
    svc = _svc()
    ctx = _base(svc)
    if (resp := _v2_or_notice(ctx, "SCAR's Diary")):
        return resp
    summary = svc.summary()
    prefs = ctx["prefs"]
    formulas = [(l, f) for l in LESSONS if l["slug"] in summary["done"] for f in l.get("formulas", [])]
    return render_template("pages/diary.html", **ctx, summary=summary, notes=svc.notes(), lessons=LESSONS,
                           done_lessons=[LESSON_BY_SLUG[s] for s in summary["done"]], formulas=formulas,
                           bookmarks=[LESSON_BY_SLUG[s] for s in prefs.get("bookmarks") or [] if s in LESSON_BY_SLUG],
                           favorites=[LESSON_BY_SLUG[s] for s in prefs.get("favorites") or [] if s in LESSON_BY_SLUG],
                           lesson_names={l["slug"]: l["region"] for l in LESSONS})


@bp.route("/mistakes")
@login_required
def mistakes():
    svc = _svc()
    ctx = _base(svc)
    if (resp := _v2_or_notice(ctx, "Mistake Notebook")):
        return resp
    rows = svc.mistakes()
    status = request.args.get("status", "")
    if status not in ("", "perlu-latihan", "dikuasai"):
        status = ""
    shown = [r for r in rows if not status or r["status"] == status]
    return render_template("pages/mistakes.html", **ctx, rows=shown, all_count=len(rows), status=status,
                           open_count=sum(1 for r in rows if r["status"] != "dikuasai"), topic_labels=TOPIC_LABELS,
                           source_labels=SOURCE_LABELS, topic_lesson={k: LESSON_BY_SLUG.get(v) for k, v in TOPIC_LESSON.items()},
                           formulas=FORMULAS)


@bp.route("/visual")
@login_required
def visual():
    ctx = _base(_svc())
    return render_template("pages/visual.html", **ctx)


@bp.route("/real-life")
@login_required
def real_life():
    svc = _svc()
    ctx = _base(svc)
    if (resp := _v2_or_notice(ctx, "Real-Life Mathematics Challenge")):
        return resp
    cmap = svc.challenge_map()
    return render_template("pages/real_life.html", **ctx, cases=REAL_CASES,
                           progress={c["slug"]: cmap.get(("reallife", c["slug"]), {}) for c in REAL_CASES})


@bp.route("/real-life/<slug>")
@login_required
def real_case(slug):
    case = REAL_BY_SLUG.get(slug)
    if not case:
        abort(404)
    svc = _svc()
    ctx = _base(svc)
    if (resp := _v2_or_notice(ctx, "Real-Life Mathematics Challenge")):
        return resp
    prog = svc.challenge_map().get(("reallife", slug), {})
    idx = [c["slug"] for c in REAL_CASES].index(slug)
    return render_template("pages/real_case.html", **ctx, case=case, prog=prog,
                           next_case=REAL_CASES[idx + 1] if idx + 1 < len(REAL_CASES) else None)


@bp.route("/secret")
@login_required
def secret():
    svc = _svc()
    ctx = _base(svc)
    if (resp := _v2_or_notice(ctx, "SCAR's Secret Mission")):
        return resp
    cmap = svc.challenge_map()
    missions = [{**m, "prog": cmap.get(("secret", m["slug"]), {}), "unlocked": svc.secret_unlocked(m["slug"], cmap)} for m in SECRET_MISSIONS]
    return render_template("pages/secret.html", **ctx, missions=missions,
                           total_points=sum(int(m["prog"].get("points") or 0) for m in missions),
                           done_count=sum(1 for m in missions if m["prog"].get("completed")),
                           master="master-of-straight-lines" in svc.earned_achievements())


@bp.route("/secret/<slug>")
@login_required
def secret_mission(slug):
    mission = SECRET_BY_SLUG.get(slug)
    if not mission:
        abort(404)
    svc = _svc()
    ctx = _base(svc)
    if (resp := _v2_or_notice(ctx, "SCAR's Secret Mission")):
        return resp
    cmap = svc.challenge_map()
    if not svc.secret_unlocked(slug, cmap):
        flash("Misi rahasia ini masih terkunci. Tuntaskan misi sebelumnya dulu, ya!", "info")
        return redirect(url_for("pages.secret"))
    idx = mission["no"] - 1
    return render_template("pages/secret_mission.html", **ctx, mission=mission, prog=cmap.get(("secret", slug), {}),
                           pass_count=SECRET_PASS, next_mission=SECRET_MISSIONS[idx + 1] if idx + 1 < len(SECRET_MISSIONS) else None)


@bp.route("/tutor")
@login_required
def tutor_page():
    ctx = _base(_svc())
    return render_template("pages/tutor.html", **ctx, ai_enabled=bool(current_app.config.get("ANTHROPIC_API_KEY")))


@bp.route("/settings")
@login_required
def settings():
    ctx = _base(_svc())
    return render_template("pages/settings.html", **ctx, avatars=AVATARS)


@bp.route("/certificate")
@login_required
def certificate():
    svc = _svc()
    ctx = _base(svc)
    if (resp := _v2_or_notice(ctx, "Sertifikat")):
        return resp
    summary = svc.summary()
    return render_template("pages/certificate.html", **ctx, cert=svc.certificate(summary), summary=summary)


@bp.route("/certificate.pdf")
@login_required
def certificate_pdf():
    from .certificate import build_certificate_pdf

    svc = _svc()
    ctx = _base(svc)
    if not ctx["v2"]:
        abort(404)
    cert = svc.certificate()
    if not cert["eligible"]:
        flash("Sertifikat tersedia setelah ketujuh misi selesai dan post-test dikerjakan.", "info")
        return redirect(url_for("pages.certificate"))
    pdf = build_certificate_pdf(ctx["profile"]["full_name"], cert["score"], cert["title"], cert["date"])
    filename = "Sertifikat-SCARLINE-" + "".join(ch for ch in ctx["profile"]["username"] if ch.isalnum() or ch == "_") + ".pdf"
    return Response(pdf, mimetype="application/pdf", headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@bp.route("/search-index.json")
@login_required
def search_index():
    """Indeks pencarian materi (judul, konsep, rumus) untuk kotak pencarian SCARLINE."""
    import re

    def strip(html: str) -> str:
        return re.sub(r"<[^>]+>", "", html or "")

    items = []
    for lesson in LESSONS:
        url = url_for("pages.mission", slug=lesson["slug"])
        items.append({"title": f"Mission {lesson['no']:02d} — {lesson['region']}", "sub": lesson["title"], "url": url,
                      "text": " ".join(lesson["objectives"])})
        for c in lesson.get("concepts", []):
            items.append({"title": c["heading"], "sub": lesson["region"], "url": url,
                          "text": strip(c["body"]) + " " + " ".join(c.get("bullets", []))})
        for f in lesson.get("formulas", []):
            items.append({"title": f["expr"], "sub": f"Rumus · {f['label']}", "url": url,
                          "text": " ".join(sym[1] for sym in f.get("symbols", []))})
    pages = [("Interactive Graph Laboratory", "/lab"), ("Visual Learning Mode", "/visual"), ("Training Zone", "/training"),
             ("Tantangan Harian", "/daily"), ("SCAR's Playground", "/playground"), ("Real-Life Challenge", "/real-life"),
             ("SCAR's Secret Mission", "/secret"), ("SCAR AI Tutor", "/tutor"), ("SCAR's Diary", "/diary"),
             ("Mistake Notebook", "/mistakes"), ("Pre-Test", "/pretest"), ("Post-Test", "/posttest"),
             ("Final Line Challenge", "/final"), ("Grafik Perkembangan", "/progress"), ("Sertifikat", "/certificate"),
             ("Pengaturan", "/settings")]
    items += [{"title": t, "sub": "Halaman", "url": u, "text": ""} for t, u in pages]
    resp = jsonify(items)
    resp.headers["Cache-Control"] = "private, max-age=600"
    return resp
