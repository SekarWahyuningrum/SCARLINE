"""Pengujian alur aplikasi: autentikasi, proteksi halaman, misi, latihan, game, evaluasi, XP, lencana."""
from fractions import Fraction

import pytest

from scarline.content import LESSON_ORDER, LESSON_QUIZZES, TRAINING_BANK
from scarline.games import GAME_BY_SLUG
from tests.conftest import PASSWORD, api, csrf_from, register

PRIVATE = ["/dashboard", "/map", "/mission/coordinate-city", "/lab", "/training", "/training/1", "/daily",
           "/playground", "/playground/coordinate-hunter", "/final", "/achievements", "/profile", "/history"]


# ------------------------------------------------------------------ auth
def test_public_pages_render(client):
    for path in ("/", "/login", "/register", "/forgot-password", "/reset-password"):
        assert client.get(path).status_code == 200, path
    html = client.get("/").get_data(as_text=True)
    assert "UNLOCK THE MYSTERY OF" in html and "MULAI PETUALANGAN" in html


@pytest.mark.parametrize("path", PRIVATE)
def test_private_pages_require_login(client, path):
    resp = client.get(path)
    assert resp.status_code == 302 and "/login" in resp.headers["Location"]


def test_api_requires_login(client):
    token = csrf_from(client)
    resp = client.post("/api/lab/calc", json={"method": "origin", "m": 2}, headers={"X-CSRF-Token": token})
    assert resp.status_code == 401


def test_registration_validation(client):
    token = csrf_from(client, "/register")
    resp = client.post("/register", data={"csrf_token": token, "full_name": "", "username": "AB", "email": "salah", "class_name": "",
                                         "password": "pendek", "confirm_password": "beda"})
    html = resp.get_data(as_text=True)
    assert resp.status_code == 200
    for msg in ("Nama lengkap wajib diisi", "Username 3–20 karakter", "Format email tidak valid", "Kelas wajib diisi",
                "Password harus memiliki", "Konfirmasi password tidak sama"):
        assert msg in html


def test_register_creates_profile_and_logs_in(client, db):
    resp = register(client)
    assert resp.status_code == 302 and resp.headers["Location"].endswith("/dashboard")
    assert db.tables["profiles"][0]["username"] == "rina_garis"
    assert "Halo, Rina" in client.get("/dashboard").get_data(as_text=True)


def test_username_must_be_unique(client, app):
    register(client)
    other = app.test_client()
    resp = register(other, email="lain@sekolah.id")
    assert "Username sudah dipakai" in resp.get_data(as_text=True)


def test_login_wrong_password_and_success(client, app):
    register(client)
    c2 = app.test_client()
    token = csrf_from(c2)
    bad = c2.post("/login", data={"csrf_token": token, "email": "rina@sekolah.id", "password": "Salah123"})
    assert "Email atau password salah" in bad.get_data(as_text=True)
    empty = c2.post("/login", data={"csrf_token": token, "email": "", "password": ""})
    assert "wajib diisi" in empty.get_data(as_text=True)
    ok = c2.post("/login?next=/lab", data={"csrf_token": token, "email": "rina@sekolah.id", "password": PASSWORD})
    assert ok.status_code == 302 and ok.headers["Location"].endswith("/lab")


def test_open_redirect_blocked(client, app):
    register(client)
    c2 = app.test_client()
    token = csrf_from(c2)
    resp = c2.post("/login?next=https://evil.example", data={"csrf_token": token, "email": "rina@sekolah.id", "password": PASSWORD})
    assert resp.headers["Location"].endswith("/dashboard")


def test_csrf_required(client):
    resp = client.post("/login", data={"email": "a@b.co", "password": "x"})
    assert resp.status_code == 400


def test_forgot_password_does_not_leak(client, db):
    token = csrf_from(client, "/forgot-password")
    resp = client.post("/forgot-password", data={"csrf_token": token, "email": "siapa@saja.id"})
    assert "Jika email" in resp.get_data(as_text=True)
    assert db.recover_calls and db.recover_calls[0][1].endswith("/reset-password")


def test_logout_keeps_progress(logged, app, db):
    token = csrf_from(logged, "/dashboard")
    resp = logged.post("/logout", data={"csrf_token": token})
    assert resp.status_code == 302
    assert logged.get("/dashboard").status_code == 302
    assert db.tables["user_stats"], "data progres tetap ada setelah logout"


def test_not_configured_shows_notice():
    from scarline import create_app
    from tests.fakes import FakeSupabase
    app = create_app({"TESTING": True, "SECRET_KEY": "x"}, db=FakeSupabase(configured=False, can_write=False))
    html = app.test_client().get("/login").get_data(as_text=True)
    assert "Supabase belum dikonfigurasi" in html


def test_all_private_pages_render(logged):
    for path in PRIVATE:
        resp = logged.get(path)
        assert resp.status_code in (200, 302), path
    assert logged.get("/mission/gradient-mountain").status_code == 302  # masih terkunci
    assert logged.get("/mission/tidak-ada").status_code == 404


# ------------------------------------------------------------------ helpers
def play_quiz(client, kind, ref, answer_fn):
    start = api(client, "/api/runs", {"kind": kind, "ref": ref})
    assert start.status_code == 200, start.get_json()
    data = start.get_json()
    assert all("answer" not in item for item in data["items"]), "kunci tidak boleh dikirim ke browser"
    for i, item in enumerate(data["items"]):
        r = api(client, f"/api/runs/{data['run_id']}/answer", {"index": i, "answer": answer_fn(item)})
        assert r.status_code == 200, r.get_json()
    return api(client, f"/api/runs/{data['run_id']}/finish").get_json()


def key_for(item):
    from scarline.content import QUESTION_BY_ID
    return QUESTION_BY_ID[item["id"]]["answer"]


def complete_mission(client, slug):
    res = play_quiz(client, "lesson", slug, key_for)
    assert res["passed"]
    return api(client, f"/api/lessons/{slug}/complete").get_json()


# ------------------------------------------------------------------ missions & XP
def test_mission_completion_requires_quiz_and_awards_xp_once(logged, db):
    early = api(logged, "/api/lessons/coordinate-city/complete")
    assert early.status_code == 403
    res = complete_mission(logged, "coordinate-city")
    assert res["xp_awarded"] == 100
    assert any(a["slug"] == "first-step" for a in res["new_achievements"])
    again = api(logged, "/api/lessons/coordinate-city/complete").get_json()
    assert again["already"] and again["xp_awarded"] == 0
    stats = db.tables["user_stats"][0]
    assert stats["total_xp"] == 100 + 30  # misi + bonus lencana First Step
    assert stats["missions_completed"] == 1


def test_locked_mission_cannot_be_started(logged):
    assert api(logged, "/api/runs", {"kind": "lesson", "ref": "gradient-mountain"}).status_code == 403
    assert api(logged, "/api/lessons/gradient-mountain/complete").status_code == 403


def test_failed_lesson_quiz_does_not_unlock(logged):
    res = play_quiz(logged, "lesson", "coordinate-city", lambda item: 0 if item["type"] == "mc" else ([9, 9] if item["type"] == "point" else True))
    assert not res["passed"] and res["xp_awarded"] == 0
    assert api(logged, "/api/lessons/coordinate-city/complete").status_code == 403


def test_answer_cannot_be_resubmitted(logged):
    data = api(logged, "/api/runs", {"kind": "training", "ref": "1"}).get_json()
    item = data["items"][0]
    api(logged, f"/api/runs/{data['run_id']}/answer", {"index": 0, "answer": key_for(item)})
    again = api(logged, f"/api/runs/{data['run_id']}/answer", {"index": 0, "answer": key_for(item)})
    assert again.status_code == 400


def test_invalid_input_does_not_consume_attempt(logged):
    data = api(logged, "/api/runs", {"kind": "training", "ref": "2"}).get_json()
    idx = next(i for i, it in enumerate(data["items"]) if it["type"] == "num")
    bad = api(logged, f"/api/runs/{data['run_id']}/answer", {"index": idx, "answer": "dua"})
    assert bad.status_code == 422
    ok = api(logged, f"/api/runs/{data['run_id']}/answer", {"index": idx, "answer": key_for(data["items"][idx])})
    assert ok.get_json()["correct"]


def test_training_xp_only_for_improvement(logged):
    first = play_quiz(logged, "training", "1", key_for)
    assert first["score"] == 100 and first["xp_awarded"] == 10 * len(TRAINING_BANK[1])
    second = play_quiz(logged, "training", "1", key_for)
    assert second["xp_awarded"] == 0


def test_wrong_answer_returns_scar_explanation(logged):
    data = api(logged, "/api/runs", {"kind": "training", "ref": "2"}).get_json()
    idx = next(i for i, it in enumerate(data["items"]) if it["id"] == "T2-02")
    res = api(logged, f"/api/runs/{data['run_id']}/answer", {"index": idx, "answer": "2"}).get_json()
    assert not res["correct"] and "terbalik" in res["feedback"] and res["explain"] and res["answer_display"] == "−2"


def test_daily_claim_once(logged):
    first = play_quiz(logged, "daily", "", key_for)
    assert first["xp_awarded"] == 30 and not first["already_claimed"]
    second = play_quiz(logged, "daily", "", key_for)
    assert second["xp_awarded"] == 0 and second["already_claimed"]


# ------------------------------------------------------------------ games
def solve_round(slug, run_id, index, client):
    """Ambil ronde dari sesi server untuk menghitung jawaban yang benar (simulasi pemain sempurna)."""
    from scarline.runs import build_items
    with client.session_transaction() as sess:
        run = sess["runs"][run_id]
    rnd = build_items(run)[index]["round"]
    if rnd.get("q"):
        return rnd["q"]["answer"]
    if rnd["kind"] == "set":
        m = Fraction(rnd["m"])
        return {"rise": m.numerator, "run": m.denominator}
    if rnd["kind"] == "pick":
        return rnd["answer"]
    inv = {v: k for k, v in rnd["tiles"].items()}
    return [inv[t] for t in rnd["solution_tokens"]]


@pytest.mark.parametrize("slug", list(GAME_BY_SLUG))
def test_each_game_playable_and_saved(logged, db, slug):
    data = api(logged, "/api/runs", {"kind": "game", "ref": slug, "difficulty": "medium"}).get_json()
    for i in range(data["total"]):
        res = api(logged, f"/api/runs/{data['run_id']}/answer", {"index": i, "answer": solve_round(slug, data["run_id"], i, logged)}).get_json()
        assert res["correct"], (slug, i, res)
    out = api(logged, f"/api/runs/{data['run_id']}/finish").get_json()
    assert out["score"] >= 100 * data["total"] and out["percent"] > 60
    assert out["xp_awarded"] > 0
    saved = [g for g in db.tables["game_attempts"] if g["game_slug"] == slug]
    assert len(saved) == 1 and saved[0]["difficulty"] == "medium"
    # mengulang dengan hasil lebih rendah tidak menambah XP
    data2 = api(logged, "/api/runs", {"kind": "game", "ref": slug, "difficulty": "easy"}).get_json()
    out2 = api(logged, f"/api/runs/{data2['run_id']}/finish").get_json()
    assert out2["xp_awarded"] == 0 and out2["score"] == 0


def test_game_wrong_answers_limit_and_hint(logged):
    data = api(logged, "/api/runs", {"kind": "game", "ref": "coordinate-hunter", "difficulty": "easy"}).get_json()
    for n in range(3):
        res = api(logged, f"/api/runs/{data['run_id']}/answer", {"index": 0, "answer": [-5, -5]}).get_json()
        assert not res["correct"] and res["feedback"]
    assert res["done"] and res["answer_display"]
    assert api(logged, f"/api/runs/{data['run_id']}/answer", {"index": 0, "answer": [-5, -5]}).status_code == 400


def test_line_rescue_hearts_game_over(logged):
    data = api(logged, "/api/runs", {"kind": "game", "ref": "line-rescue", "difficulty": "easy"}).get_json()
    assert data["hearts"] == 3
    for _ in range(3):
        res = api(logged, f"/api/runs/{data['run_id']}/answer", {"index": 0, "answer": [99, 99]}).get_json()
    assert res["game_over"] and res["hearts"] == 0


def test_game_score_cannot_be_posted_by_client(logged, db):
    data = api(logged, "/api/runs", {"kind": "game", "ref": "gradient-rush", "difficulty": "easy"}).get_json()
    out = api(logged, f"/api/runs/{data['run_id']}/finish", {"score": 999999, "percent": 100}).get_json()
    assert out["score"] == 0 and out["xp_awarded"] == 0


# ------------------------------------------------------------------ final & achievements
def test_final_locked_until_all_missions(logged):
    assert api(logged, "/api/runs", {"kind": "final", "count": 10}).status_code == 403


def test_full_journey_to_champion(logged, db):
    for slug in LESSON_ORDER:
        res = complete_mission(logged, slug)
        assert res["ok"], slug
    bad_count = api(logged, "/api/runs", {"kind": "final", "count": 7})
    assert bad_count.status_code == 400
    data = api(logged, "/api/runs", {"kind": "final", "count": 15, "timer": True}).get_json()
    assert data["total"] == 15 and data["timer"] == 15 * 90
    topics = {it["topic"] for it in data["items"]}
    assert len(topics) == 8, "evaluasi mencakup semua topik"
    assert api(logged, f"/api/runs/{data['run_id']}/answer", {"index": 0, "answer": 1}).status_code == 400
    answers = {str(i): key_for(it) for i, it in enumerate(data["items"])}
    answers["0"] = "jawaban-ngawur"
    out = api(logged, f"/api/runs/{data['run_id']}/finish", {"answers": answers}).get_json()
    assert out["correct"] == 14 and out["score"] == 93 and out["passed"]
    assert len(out["review"]) == 15 and all(r["explain"] for r in out["review"])
    slugs = {a["achievement_slug"] for a in db.tables["user_achievements"]}
    assert {"first-step", "gradient-master", "line-creator", "parallel-detective", "scarline-champion"} <= slugs
    stats = db.tables["user_stats"][0]
    assert stats["missions_completed"] == 7 and stats["best_final_score"] == 93 and stats["level"] >= 4
    html = logged.get("/history").get_data(as_text=True)
    assert "Final Line Challenge" in html
    assert "SCARLINE Champion" in logged.get("/achievements").get_data(as_text=True)


def test_rls_reads_only_own_rows(app, db):
    a = app.test_client(); register(a)
    b = app.test_client(); register(b, username="budi_x", email="budi@sekolah.id")
    complete_mission(a, "coordinate-city")
    html = b.get("/history").get_data(as_text=True)
    assert "Coordinate City" not in html


# ------------------------------------------------------------------ lab & profile
@pytest.mark.parametrize("payload,expected", [
    ({"method": "two-points", "x1": 1, "y1": 2, "x2": 3, "y2": 6}, "y = 2x"),
    ({"method": "point-slope", "m": "3", "x1": 2, "y1": 5}, "y = 3x − 1"),
    ({"method": "slope-intercept", "m": "-2", "c": "4"}, "y = −2x + 4"),
    ({"method": "gradient", "x1": "-2", "y1": 4, "x2": 2, "y2": -4}, "y = −2x"),
    ({"method": "origin", "m": "3/2"}, "y = (3/2)x"),
    ({"method": "two-points", "x1": 2, "y1": 1, "x2": 2, "y2": 5}, "x = 2"),
])
def test_lab_calculator(logged, payload, expected):
    res = api(logged, "/api/lab/calc", payload)
    assert res.status_code == 200 and res.get_json()["equation"] == expected
    assert res.get_json()["steps"]


def test_lab_calculator_rejects_invalid(logged):
    assert api(logged, "/api/lab/calc", {"method": "point-slope", "m": "abc", "x1": 1, "y1": 1}).status_code == 422
    assert api(logged, "/api/lab/calc", {"method": "two-points", "x1": 1, "y1": 1, "x2": 1, "y2": 1}).status_code == 422


def test_profile_update(logged, db):
    token = csrf_from(logged, "/profile")
    resp = logged.post("/profile", data={"csrf_token": token, "full_name": "Rina K. Putri", "class_name": "VIII-B"})
    assert resp.status_code == 302
    assert db.tables["profiles"][0]["class_name"] == "VIII-B"
    bad = logged.post("/profile", data={"csrf_token": token, "full_name": "R", "class_name": ""})
    assert "Periksa kembali" in bad.get_data(as_text=True)


def test_lesson_quiz_count():
    assert all(len(v) == 3 for v in LESSON_QUIZZES.values())


def test_register_uses_admin_api_without_email(client, db):
    resp = register(client, username="tanpa_email", email="tanpa@sekolah.id")
    assert resp.status_code == 302 and resp.headers["Location"].endswith("/dashboard")
    assert db.admin_created == ["tanpa@sekolah.id"]


def test_register_duplicate_email_admin_path(client, app):
    register(client)
    resp = register(app.test_client(), username="nama_lain")
    assert "sudah terdaftar" in resp.get_data(as_text=True)


def test_supabase_url_normalized():
    from scarline.supabase_client import SupabaseClient
    assert SupabaseClient("https://abc.supabase.co/rest/v1/", "k").url == "https://abc.supabase.co"
    assert SupabaseClient(" https://abc.supabase.co/auth/v1 ", "k").url == "https://abc.supabase.co"
