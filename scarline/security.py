"""Sesi login, proteksi halaman privat, dan CSRF."""
from __future__ import annotations

import hmac
import secrets
import time
from functools import wraps
from urllib.parse import urlparse

from flask import abort, current_app, flash, g, jsonify, make_response, redirect, request, session, url_for

from .supabase_client import SupabaseError

REFRESH_MARGIN = 60  # detik sebelum token kedaluwarsa


def get_db():
    return current_app.extensions["scarline_db"]


# ------------------------------------------------------------------ CSRF
def csrf_token() -> str:
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]


def _check_csrf() -> None:
    if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
        return
    sent = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token") or ""
    expected = session.get("csrf", "")
    if not expected or not hmac.compare_digest(sent, expected):
        if request.path.startswith("/api/") or request.is_json:
            abort(make_response(jsonify({"error": "Sesi formulir kedaluwarsa. Muat ulang halaman lalu coba lagi."}), 400))
        abort(400, description="Token formulir tidak valid. Muat ulang halaman lalu coba lagi.")


# ------------------------------------------------------------------ auth session
def set_auth_session(data: dict) -> None:
    user = data.get("user") or {}
    expires_at = data.get("expires_at") or (int(time.time()) + int(data.get("expires_in") or 3600))
    session.permanent = True
    session["auth"] = {
        "access_token": data["access_token"],
        "refresh_token": data.get("refresh_token", ""),
        "expires_at": int(expires_at),
        "user_id": user.get("id"),
        "email": user.get("email"),
    }
    session.pop("runs", None)


def clear_auth() -> None:
    session.pop("auth", None)
    session.pop("runs", None)


def current_auth():
    """Ambil sesi aktif; perbarui token jika hampir kedaluwarsa. None jika tidak login."""
    auth = session.get("auth")
    if not auth or not auth.get("access_token") or not auth.get("user_id"):
        return None
    if auth.get("expires_at", 0) - REFRESH_MARGIN < time.time():
        try:
            fresh = get_db().refresh(auth.get("refresh_token", ""))
        except SupabaseError:
            clear_auth()
            return None
        set_auth_session(fresh)
        auth = session["auth"]
    return auth


def _load_identity(auth: dict) -> None:
    g.user_id = auth["user_id"]
    g.token = auth["access_token"]
    g.email = auth.get("email")


def safe_next(target: str) -> str:
    if not target:
        return url_for("pages.dashboard")
    parsed = urlparse(target)
    if parsed.scheme or parsed.netloc or not target.startswith("/") or target.startswith("//"):
        return url_for("pages.dashboard")
    return target


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        auth = current_auth()
        if not auth:
            flash("Silakan masuk terlebih dahulu untuk melanjutkan petualanganmu.", "info")
            return redirect(url_for("auth.login", next=request.full_path.rstrip("?")))
        _load_identity(auth)
        return view(*args, **kwargs)

    return wrapper


def api_login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        auth = current_auth()
        if not auth:
            return jsonify({"error": "Sesi login berakhir. Silakan masuk kembali.", "login": url_for("auth.login")}), 401
        _load_identity(auth)
        return view(*args, **kwargs)

    return wrapper


def init_security(app) -> None:
    app.before_request(_check_csrf)

    @app.context_processor
    def inject_csrf():
        return {"csrf_token": csrf_token}

    @app.after_request
    def security_headers(resp):
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        if session.get("auth"):
            resp.headers.setdefault("Cache-Control", "no-store")
        return resp
