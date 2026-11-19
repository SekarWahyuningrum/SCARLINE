"""Konfigurasi SCARLINE dari environment variable (.env)."""
import os
import secrets
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)
    SECRET_KEY_IS_RANDOM = not bool(os.environ.get("FLASK_SECRET_KEY"))

    SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
    SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "").strip()
    # Service role key HANYA dipakai di server (Python) untuk menulis skor/XP.
    # Jangan pernah dikirim ke browser.
    SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()

    SITE_URL = os.environ.get("SITE_URL", "http://localhost:5000").strip().rstrip("/")
    # Default: akun langsung aktif (dibuat lewat Admin API di server) sehingga tidak
    # terkena batas kirim email bawaan Supabase. Set 1 untuk mewajibkan konfirmasi email.
    REQUIRE_EMAIL_CONFIRMATION = _bool("REQUIRE_EMAIL_CONFIRMATION", False)

    # SCAR AI Tutor (opsional). Kunci HANYA dipakai server; tanpa kunci, tutor dasar lokal yang aktif.
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    TUTOR_MODEL = os.environ.get("TUTOR_MODEL", "claude-opus-5-5").strip() or "claude-opus-5-5"

    SESSION_COOKIE_NAME = "scarline_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _bool("SESSION_COOKIE_SECURE", SITE_URL.startswith("https://"))
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    FINAL_QUESTION_OPTIONS = (10, 15, 20, 25)
    TESTING = False
