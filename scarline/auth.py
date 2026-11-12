"""Registrasi, login, lupa password, reset password, dan logout (Supabase Auth)."""
from __future__ import annotations

import re

from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, url_for

from .security import api_login_required, clear_auth, current_auth, get_db, safe_next, set_auth_session
from .services import LearningService
from .supabase_client import SupabaseError

bp = Blueprint("auth", __name__)

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
USERNAME_RE = re.compile(r"^[a-z0-9_]{3,20}$")
NAME_RE = re.compile(r"^[A-Za-zÀ-ÿ' .\-]{3,60}$")
CLASS_RE = re.compile(r"^[A-Za-z0-9 .\-]{1,20}$")


def password_problems(pw: str) -> list:
    problems = []
    if len(pw) < 8:
        problems.append("minimal 8 karakter")
    if not re.search(r"[a-z]", pw):
        problems.append("huruf kecil")
    if not re.search(r"[A-Z]", pw):
        problems.append("huruf besar")
    if not re.search(r"\d", pw):
        problems.append("angka")
    return problems


def validate_registration(form) -> tuple:
    data = {
        "full_name": " ".join((form.get("full_name") or "").split()),
        "username": (form.get("username") or "").strip().lower(),
        "email": (form.get("email") or "").strip().lower(),
        "class_name": " ".join((form.get("class_name") or "").split()),
        "password": form.get("password") or "",
        "confirm": form.get("confirm_password") or "",
    }
    errors = {}
    if not data["full_name"]:
        errors["full_name"] = "Nama lengkap wajib diisi."
    elif not NAME_RE.match(data["full_name"]):
        errors["full_name"] = "Nama lengkap 3–60 huruf (boleh spasi, titik, tanda petik)."
    if not data["username"]:
        errors["username"] = "Username wajib diisi."
    elif not USERNAME_RE.match(data["username"]):
        errors["username"] = "Username 3–20 karakter: huruf kecil, angka, atau garis bawah (_)."
    if not data["email"]:
        errors["email"] = "Email wajib diisi."
    elif not EMAIL_RE.match(data["email"]):
        errors["email"] = "Format email tidak valid. Contoh: nama@sekolah.sch.id"
    if not data["class_name"]:
        errors["class_name"] = "Kelas wajib diisi."
    elif not CLASS_RE.match(data["class_name"]):
        errors["class_name"] = "Kelas maksimal 20 karakter, misalnya VIII-A."
    if not data["password"]:
        errors["password"] = "Password wajib diisi."
    else:
        probs = password_problems(data["password"])
        if probs:
            errors["password"] = "Password harus memiliki " + ", ".join(probs) + "."
    if not data["confirm"]:
        errors["confirm_password"] = "Konfirmasi password wajib diisi."
    elif data["confirm"] != data["password"]:
        errors["confirm_password"] = "Konfirmasi password tidak sama dengan password."
    return data, errors


def _not_ready():
    return not get_db().configured


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_auth():
        return redirect(url_for("pages.dashboard"))
    values, errors = {}, {}
    if request.method == "POST":
        values, errors = validate_registration(request.form)
        db = get_db()
        if _not_ready():
            flash("Supabase belum dikonfigurasi. Isi SUPABASE_URL dan SUPABASE_ANON_KEY di file .env (lihat README).", "error")
        elif not errors:
            try:
                if db.can_write:
                    taken = db.select("profiles", token=None, filters={"username": values["username"]}, columns="id", limit=1)
                    if taken:
                        errors["username"] = "Username sudah dipakai. Coba username lain."
                if not errors:
                    meta = {"full_name": values["full_name"], "username": values["username"], "class_name": values["class_name"]}
                    if db.can_write and not current_app.config.get("REQUIRE_EMAIL_CONFIRMATION"):
                        db.admin_create_user(values["email"], values["password"], meta)
                        res = db.sign_in(values["email"], values["password"])
                    else:
                        res = db.sign_up(values["email"], values["password"], meta,
                                         redirect_to=f"{current_app.config['SITE_URL']}/login?confirmed=1")
                    if res.get("access_token"):
                        set_auth_session(res)
                        user = res.get("user") or {}
                        if db.can_write:
                            LearningService(db, user["id"]).ensure_profile(user)
                        flash(f"Akun berhasil dibuat. Selamat datang, {values['full_name']}!", "success")
                        return redirect(url_for("pages.dashboard"))
                    identities = (res.get("identities") if "identities" in res else (res.get("user") or {}).get("identities"))
                    if identities == []:
                        errors["email"] = "Email ini sudah terdaftar. Silakan masuk."
                    else:
                        return render_template("auth/check_email.html", email=values["email"])
            except SupabaseError as exc:
                msg = exc.friendly
                if "username" in msg.lower():
                    errors["username"] = msg
                elif "email" in msg.lower():
                    errors["email"] = msg
                else:
                    flash(msg, "error")
        if errors:
            flash("Periksa kembali isian yang ditandai, ya.", "error")
    values.pop("password", None)
    values.pop("confirm", None)
    return render_template("auth/register.html", values=values, errors=errors)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_auth():
        return redirect(url_for("pages.dashboard"))
    email = ""
    error = None
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        if not email or not password:
            error = "Email dan password wajib diisi."
        elif not EMAIL_RE.match(email):
            error = "Format email tidak valid."
        elif _not_ready():
            error = "Supabase belum dikonfigurasi. Isi SUPABASE_URL dan SUPABASE_ANON_KEY di file .env (lihat README)."
        else:
            db = get_db()
            try:
                res = db.sign_in(email, password)
                set_auth_session(res)
                if db.can_write:
                    LearningService(db, res["user"]["id"]).ensure_profile(res["user"])
                flash("Selamat datang kembali, Line Explorer!", "success")
                return redirect(safe_next(request.args.get("next") or request.form.get("next")))
            except SupabaseError as exc:
                error = exc.friendly
    return render_template("auth/login.html", email=email, error=error, next=request.args.get("next", ""))


@bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    sent = False
    error = None
    email = ""
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        if not EMAIL_RE.match(email):
            error = "Masukkan email yang valid."
        elif _not_ready():
            error = "Supabase belum dikonfigurasi."
        else:
            try:
                get_db().recover(email, redirect_to=f"{current_app.config['SITE_URL']}/reset-password")
                sent = True
            except SupabaseError as exc:
                if exc.status in (0, 429) or exc.status >= 500:
                    error = exc.friendly
                else:
                    sent = True  # jangan bocorkan apakah email terdaftar
    return render_template("auth/forgot.html", sent=sent, error=error, email=email)


@bp.route("/reset-password", methods=["GET"])
def reset_password():
    return render_template("auth/reset.html")


@bp.route("/reset-password", methods=["POST"])
def reset_password_submit():
    data = request.get_json(silent=True) or {}
    token = (data.get("access_token") or "").strip()
    pw = data.get("password") or ""
    confirm = data.get("confirm_password") or ""
    if not token:
        return jsonify({"error": "Tautan reset tidak valid. Minta tautan baru dari halaman Lupa Password."}), 400
    probs = password_problems(pw)
    if probs:
        return jsonify({"error": "Password harus memiliki " + ", ".join(probs) + "."}), 400
    if pw != confirm:
        return jsonify({"error": "Konfirmasi password tidak sama."}), 400
    try:
        get_db().update_password(token, pw)
        get_db().sign_out(token)
    except SupabaseError as exc:
        return jsonify({"error": exc.friendly}), 400
    clear_auth()
    flash("Password berhasil diganti. Silakan masuk dengan password baru.", "success")
    return jsonify({"ok": True, "redirect": url_for("auth.login")})


@bp.route("/logout", methods=["POST"])
def logout():
    auth = current_auth()
    if auth:
        get_db().sign_out(auth["access_token"])
    clear_auth()
    flash("Kamu sudah keluar. Progresmu tersimpan aman — sampai jumpa lagi!", "success")
    return redirect(url_for("pages.landing"))


@bp.route("/api/session", methods=["GET"])
@api_login_required
def session_check():
    return jsonify({"ok": True})
