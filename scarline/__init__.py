"""SCARLINE — Discover the Line, Master the Equation!

Platform pembelajaran Persamaan Garis Lurus untuk SMP kelas VIII.
Backend: Python (Flask) + Supabase (Auth, PostgreSQL, RLS).
Frontend: JavaScript (SVG koordinat, simulasi, dan game).
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from flask import Flask, g, render_template, request

from .config import Config
from .supabase_client import SupabaseClient, SupabaseError

WIB = timezone(timedelta(hours=7))
MONTHS = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]


def _datefmt(value, with_time: bool = True) -> str:
    if not value:
        return "—"
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return str(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(WIB)
    text = f"{dt.day} {MONTHS[dt.month - 1]} {dt.year}"
    return f"{text}, {dt:%H:%M} WIB" if with_time else text


def create_app(overrides: dict | None = None, db=None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    if overrides:
        app.config.update(overrides)

    app.extensions["scarline_db"] = db or SupabaseClient(
        app.config["SUPABASE_URL"], app.config["SUPABASE_ANON_KEY"], app.config["SUPABASE_SERVICE_ROLE_KEY"]
    )
    if app.config.get("SECRET_KEY_IS_RANDOM") and not app.config.get("TESTING"):
        app.logger.warning("FLASK_SECRET_KEY belum diatur: sesi login akan hilang saat server restart.")

    from . import api, auth, views
    from .content.lessons import LESSONS
    from .security import init_security

    init_security(app)
    app.register_blueprint(views.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(api.bp)

    def _macro(template: str, name: str):
        def call(*args, **kwargs):
            return getattr(app.jinja_env.get_template(template).module, name)(*args, **kwargs)
        return call

    for tpl, names in (("partials/scar.html", ("scar", "bubble", "avatar")), ("partials/icons.html", ("icon",)),
                       ("partials/forms.html", ("pw_field",))):
        for name in names:
            app.jinja_env.globals[name] = _macro(tpl, name)

    app.jinja_env.filters["datefmt"] = _datefmt
    app.jinja_env.filters["tojson_attr"] = lambda v: json.dumps(v, ensure_ascii=False)

    @app.context_processor
    def globals_():
        db_ = app.extensions["scarline_db"]
        return {
            "supabase_ready": db_.configured,
            "supabase_write_ready": db_.can_write,
            "nav_lessons": LESSONS,
            "header": getattr(g, "header", None),
            "current_path": request.path,
        }

    @app.errorhandler(404)
    def not_found(_e):
        return render_template("pages/error.html", code=404, title="Wilayah tidak ditemukan",
                               message="SCAR sudah mencari ke seluruh kuadran, tapi halaman ini tidak ada."), 404

    @app.errorhandler(400)
    def bad_request(e):
        return render_template("pages/error.html", code=400, title="Permintaan tidak valid",
                               message=getattr(e, "description", "Coba muat ulang halaman.")), 400

    @app.errorhandler(SupabaseError)
    def supabase_down(e):
        app.logger.warning("Supabase error: %s", e)
        return render_template("pages/error.html", code=503, title="Koneksi ke markas terputus",
                               message=e.friendly), 503

    @app.errorhandler(500)
    def server_error(_e):
        return render_template("pages/error.html", code=500, title="Ada yang tidak beres",
                               message="Terjadi kesalahan di server. Coba lagi sebentar lagi."), 500

    return app
