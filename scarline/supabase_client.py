"""Klien Supabase ringan (Auth/GoTrue + PostgREST) berbasis ``requests``.

- Operasi baca halaman memakai access token siswa, sehingga Row Level Security
  (RLS) di PostgreSQL tetap berlaku.
- Operasi tulis skor/XP memakai service role key di server, karena tabel
  hasil belajar tidak boleh ditulis langsung dari browser (anti manipulasi skor).
"""
from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List, Optional, Union

import requests

FilterValue = Union[str, int, float, bool, None, tuple]

ERROR_TRANSLATIONS = {
    "invalid login credentials": "Email atau password salah. Coba periksa lagi, ya!",
    "email not confirmed": "Email kamu belum dikonfirmasi. Buka kotak masuk email dan klik tautan konfirmasi dari SCARLINE.",
    "user already registered": "Email ini sudah terdaftar. Silakan masuk atau gunakan email lain.",
    "email_exists": "Email ini sudah terdaftar. Silakan masuk atau gunakan email lain.",
    "already been registered": "Email ini sudah terdaftar. Silakan masuk atau gunakan email lain.",
    "password should be at least": "Password terlalu pendek. Gunakan minimal 8 karakter.",
    "email rate limit exceeded": "Batas pengiriman email Supabase tercapai. Tunggu beberapa saat lalu coba lagi.",
    "rate limit": "Terlalu banyak percobaan. Tunggu beberapa menit lalu coba lagi.",
    "database error saving new user": "Akun gagal dibuat. Username mungkin sudah dipakai, coba username lain.",
    "unable to validate email address": "Format email tidak valid.",
    "new password should be different": "Password baru harus berbeda dari password lama.",
    "token has expired": "Tautan sudah kedaluwarsa. Minta tautan reset password yang baru.",
    "invalid jwt": "Sesi tidak valid atau sudah berakhir. Silakan masuk kembali.",
    "jwt expired": "Sesi sudah berakhir. Silakan masuk kembali.",
    "service_role_key belum diatur": "Server belum dikonfigurasi lengkap: SUPABASE_SERVICE_ROLE_KEY belum diatur (lihat README).",
}


class SupabaseError(Exception):
    def __init__(self, message: str, status: int = 0, raw: Any = None):
        super().__init__(message)
        self.status = status
        self.raw = raw

    @property
    def friendly(self) -> str:
        text = str(self).lower()
        for key, msg in ERROR_TRANSLATIONS.items():
            if key in text:
                return msg
        if self.status == 0:
            return "Tidak dapat terhubung ke server Supabase. Periksa koneksi internet dan konfigurasi SUPABASE_URL."
        if self.status >= 500:
            return "Server sedang bermasalah. Coba lagi sebentar lagi."
        return "Terjadi kesalahan. Coba lagi, ya."


class SupabaseClient:
    def __init__(self, url: str, anon_key: str, service_key: str = "", timeout: float = 12.0):
        self.url = self.normalize_url(url)
        self.anon_key = anon_key or ""
        self.service_key = service_key or ""
        self.timeout = timeout
        self._http = requests.Session()

    # ------------------------------------------------------------------ util
    @staticmethod
    def normalize_url(url: Optional[str]) -> str:
        """Terima juga URL yang tersalin dengan akhiran /rest/v1 atau /auth/v1."""
        url = (url or "").strip().rstrip("/")
        for suffix in ("/rest/v1", "/auth/v1"):
            if url.lower().endswith(suffix):
                url = url[: -len(suffix)].rstrip("/")
        return url

    @property
    def configured(self) -> bool:
        return bool(self.url and self.anon_key)

    @property
    def can_write(self) -> bool:
        return bool(self.configured and self.service_key)

    def _headers(self, token: Optional[str] = None, *, service: bool = False, extra: Optional[dict] = None) -> dict:
        if service:
            if not self.service_key:
                raise SupabaseError("SUPABASE_SERVICE_ROLE_KEY belum diatur di server.", 500)
            key, bearer = self.service_key, self.service_key
        else:
            key, bearer = self.anon_key, token or self.anon_key
        headers = {"apikey": key, "Authorization": f"Bearer {bearer}", "Content-Type": "application/json"}
        if extra:
            headers.update(extra)
        return headers

    def _request(self, method: str, path: str, *, headers: dict, params=None, payload=None) -> Any:
        if not self.configured:
            raise SupabaseError("Supabase belum dikonfigurasi.", 503)
        try:
            resp = self._http.request(
                method,
                f"{self.url}{path}",
                headers=headers,
                params=params,
                data=json.dumps(payload) if payload is not None else None,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:  # jaringan putus, DNS, dll.
            raise SupabaseError(f"Network error: {exc}", 0) from exc
        if resp.status_code >= 400:
            try:
                body = resp.json()
            except ValueError:
                body = {"message": resp.text}
            msg = (
                body.get("error_description")
                or body.get("msg")
                or body.get("message")
                or body.get("error")
                or resp.text
            ) if isinstance(body, dict) else resp.text
            raise SupabaseError(str(msg), resp.status_code, body)
        if resp.status_code == 204 or not resp.content:
            return None
        try:
            return resp.json()
        except ValueError:
            return None

    # ------------------------------------------------------------------ auth
    def sign_up(self, email: str, password: str, metadata: dict, redirect_to: str = "") -> dict:
        params = {"redirect_to": redirect_to} if redirect_to else None
        return self._request(
            "POST", "/auth/v1/signup", headers=self._headers(), params=params,
            payload={"email": email, "password": password, "data": metadata},
        ) or {}

    def admin_create_user(self, email: str, password: str, metadata: dict) -> dict:
        """Buat akun yang langsung terkonfirmasi (khusus server, memakai service role key)."""
        return self._request(
            "POST", "/auth/v1/admin/users", headers=self._headers(service=True),
            payload={"email": email, "password": password, "email_confirm": True, "user_metadata": metadata},
        ) or {}

    def sign_in(self, email: str, password: str) -> dict:
        return self._request(
            "POST", "/auth/v1/token", headers=self._headers(), params={"grant_type": "password"},
            payload={"email": email, "password": password},
        )

    def refresh(self, refresh_token: str) -> dict:
        return self._request(
            "POST", "/auth/v1/token", headers=self._headers(), params={"grant_type": "refresh_token"},
            payload={"refresh_token": refresh_token},
        )

    def get_user(self, access_token: str) -> dict:
        return self._request("GET", "/auth/v1/user", headers=self._headers(access_token))

    def sign_out(self, access_token: str) -> None:
        try:
            self._request("POST", "/auth/v1/logout", headers=self._headers(access_token))
        except SupabaseError:
            pass  # token sudah kedaluwarsa: sesi lokal tetap dihapus.

    def recover(self, email: str, redirect_to: str) -> None:
        self._request(
            "POST", "/auth/v1/recover", headers=self._headers(), params={"redirect_to": redirect_to},
            payload={"email": email},
        )

    def update_password(self, access_token: str, password: str) -> dict:
        return self._request(
            "PUT", "/auth/v1/user", headers=self._headers(access_token), payload={"password": password}
        )

    # ------------------------------------------------------------------ data
    @staticmethod
    def _filters(filters: Optional[Dict[str, FilterValue]]) -> dict:
        params = {}
        for col, value in (filters or {}).items():
            if isinstance(value, tuple):
                op, val = value
                if op == "in":
                    val = "(" + ",".join(str(v) for v in val) + ")"
                params[col] = f"{op}.{val}"
            elif value is None:
                params[col] = "is.null"
            elif isinstance(value, bool):
                params[col] = f"eq.{str(value).lower()}"
            else:
                params[col] = f"eq.{value}"
        return params

    def select(
        self,
        table: str,
        *,
        token: Optional[str] = None,
        filters: Optional[Dict[str, FilterValue]] = None,
        columns: str = "*",
        order: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[dict]:
        params = {"select": columns, **self._filters(filters)}
        if order:
            params["order"] = order
        if limit:
            params["limit"] = str(limit)
        service = token is None
        return self._request("GET", f"/rest/v1/{table}", headers=self._headers(token, service=service), params=params) or []

    def insert(self, table: str, rows: Union[dict, Iterable[dict]]) -> List[dict]:
        payload = rows if isinstance(rows, list) else [rows] if isinstance(rows, dict) else list(rows)
        return self._request(
            "POST", f"/rest/v1/{table}",
            headers=self._headers(service=True, extra={"Prefer": "return=representation"}),
            payload=payload,
        ) or []

    def upsert(self, table: str, rows: Union[dict, List[dict]], on_conflict: str, ignore_duplicates: bool = False) -> List[dict]:
        payload = rows if isinstance(rows, list) else [rows]
        resolution = "ignore-duplicates" if ignore_duplicates else "merge-duplicates"
        return self._request(
            "POST", f"/rest/v1/{table}",
            headers=self._headers(service=True, extra={"Prefer": f"return=representation,resolution={resolution}"}),
            params={"on_conflict": on_conflict},
            payload=payload,
        ) or []

    def update(self, table: str, filters: Dict[str, FilterValue], values: dict, *, token: Optional[str] = None) -> List[dict]:
        if not filters:
            raise SupabaseError("Update tanpa filter ditolak demi keamanan.", 400)
        service = token is None
        return self._request(
            "PATCH", f"/rest/v1/{table}",
            headers=self._headers(token, service=service, extra={"Prefer": "return=representation"}),
            params=self._filters(filters),
            payload=values,
        ) or []
