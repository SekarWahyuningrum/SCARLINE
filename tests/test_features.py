"""Pengujian fitur v2: pre/post-test, perbandingan, Mistake Notebook, Diary, preferensi, bookmark,
Secret Mission, Real-Life Challenge, tutor, sertifikat, peta 12 perhentian, dan degradasi tanpa migrasi 002."""
import io

import pytest

from scarline.content import LESSON_ORDER, POSTTEST, PRETEST, REAL_CASES, SECRET_MISSIONS
from scarline.services import _V2_CACHE
from tests.conftest import api, register
from tests.test_app import complete_mission, key_for, play_quiz

NEW_PAGES = ["/pretest", "/posttest", "/progress", "/diary", "/mistakes", "/visual", "/real-life", "/real-life/ojek-daring",
             "/secret", "/secret/menara-koordinat", "/tutor", "/settings", "/certificate", "/playground/line-detective",
             "/playground/parallel-perpendicular", "/map", "/dashboard", "/profile", "/achievements", "/history", "/"]


@pytest.fixture(autouse=True)
def _clear_cache():
    _V2_CACHE.clear()
    yield
    _V2_CACHE.clear()


def exam(client, kind, answers):
    data = api(client, "/api/runs", {"kind": kind}).get_json()
    assert all("answer" not in q for q in data["items"])
    return api(client, f"/api/runs/{data['run_id']}/finish", {"answers": answers}).get_json()


def all_right(qs):
    return {str(i): q["answer"] for i, q in enumerate(qs)}


def test_landing_has_creator_identity_and_pretest(client):
    html = client.get("/").get_data(as_text=True)
    for text in ("SCARLINE", "A Mathematics Learning Experience", "Sekar Wahyuningrum", "Universitas Sultan Ageng Tirtayasa"):
        assert text in html
    assert "Sekar Wahyuningrum Adi" not in html and "Developed By" not in html and "Created By" not in html
    assert html.rindex("Universitas Sultan Ageng Tirtayasa") > html.rindex("Sekar Wahyuningrum") > html.rindex("Pre-Test")
    assert "Halo, Petualang Matematika! Aku SCAR." in html


@pytest.mark.parametrize("path", NEW_PAGES)
def test_new_pages_render(logged, path):
    resp = logged.get(path)
    assert resp.status_code in (200, 302), path


def test_pretest_saved_not_gating(logged, db):
    wrong = {str(i): (q["answer"] + 1) % 4 for i, q in enumerate(PRETEST)}
    res = exam(logged, "pretest", wrong)
    assert res["score"] == 0 and res["correct"] == 0 and res["total"] == 10
    assert res["xp_awarded"] == 30 and len(res["review"]) == 10
    assert all(r["explain"] and r["answer_display"] for r in res["review"])
    assert db.tables["assessment_attempts"][0]["kind"] == "pretest"
    # nilai rendah tidak mengunci petualangan
    assert logged.get("/mission/coordinate-city").status_code == 200
    # mengulang tidak memberi XP lagi
    assert exam(logged, "pretest", wrong)["xp_awarded"] == 0
    # kesalahan masuk Mistake Notebook
    assert len(db.tables["mistakes"]) == 10


def test_posttest_locked_until_journey_done(logged):
    assert api(logged, "/api/runs", {"kind": "posttest"}).status_code == 403
    assert "Post-test terbuka setelah" in logged.get("/posttest").get_data(as_text=True)


def _finish_journey(client):
    for slug in LESSON_ORDER:
        complete_mission(client, slug)
    data = api(client, "/api/runs", {"kind": "final", "count": 10}).get_json()
    api(client, f"/api/runs/{data['run_id']}/finish", {"answers": {}})


def test_posttest_comparison_is_honest(logged):
    half = {str(i): (q["answer"] if i < 5 else (q["answer"] + 1) % 4) for i, q in enumerate(PRETEST)}
    exam(logged, "pretest", half)  # 50
    _finish_journey(logged)
    res = exam(logged, "posttest", all_right(POSTTEST))
    cmp = res["comparison"]
    assert cmp["pre"] == 50 and cmp["post"] == 100 and cmp["diff"] == 50 and cmp["percent_change"] == 100.0
    assert cmp["improved"] and "naik 50 poin" in cmp["verdict"]
    assert any(a["slug"] == "rising-line" for a in res["new_achievements"])
    # post-test lebih rendah → tidak diklaim naik
    low = exam(logged, "posttest", {str(i): (q["answer"] + 1) % 4 for i, q in enumerate(POSTTEST)})
    assert low["comparison"]["diff"] < 0 and not low["comparison"]["improved"] and "lebih rendah" in low["comparison"]["verdict"]
    assert low["comparison"]["needs"]


def test_percent_change_none_when_pretest_zero(logged):
    exam(logged, "pretest", {})
    _finish_journey(logged)
    cmp = exam(logged, "posttest", all_right(POSTTEST))["comparison"]
    assert cmp["pre"] == 0 and cmp["percent_change"] is None


def test_certificate_pdf(logged):
    assert logged.get("/certificate.pdf").status_code == 302  # belum memenuhi syarat
    exam(logged, "pretest", {})
    _finish_journey(logged)
    exam(logged, "posttest", all_right(POSTTEST))
    resp = logged.get("/certificate.pdf")
    assert resp.status_code == 200 and resp.mimetype == "application/pdf"
    import pypdf

    text = pypdf.PdfReader(io.BytesIO(resp.data)).pages[0].extract_text()
    assert "Rina Kartika" in text and "100 / 100" in text and "Persamaan Garis Lurus" in text
    assert "Unduh PDF" in logged.get("/certificate").get_data(as_text=True)


def test_mistake_recorded_and_mastered(logged, db):
    play_quiz(logged, "lesson", "coordinate-city", lambda item: 0 if item["type"] == "mc" else ([9, 9] if item["type"] == "point" else True))
    rows = db.tables["mistakes"]
    assert {r["question_id"] for r in rows} == {"M1-1", "M1-2", "M1-3"}
    assert rows[0]["your_answer"] and rows[0]["correct_answer"]
    assert "M1-1" in logged.get("/mistakes").get_data(as_text=True)
    data = api(logged, "/api/runs", {"kind": "mistake", "ref": "M1-1"}).get_json()
    assert data["items"][0]["id"] != "M1-1" and data["items"][0]["topic"] == "koordinat" and "hint" in data["items"][0]
    from scarline.content import QUESTION_BY_ID

    res = api(logged, f"/api/runs/{data['run_id']}/answer", {"index": 0, "answer": QUESTION_BY_ID[data["items"][0]["id"]]["answer"]}).get_json()
    assert res["correct"] and res["mastered"]
    assert next(r for r in db.tables["mistakes"] if r["question_id"] == "M1-1")["status"] == "dikuasai"
    assert api(logged, "/api/runs", {"kind": "mistake", "ref": "NOPE"}).status_code == 404


def test_diary_crud(logged, db):
    assert api(logged, "/api/diary", {"title": ""}).status_code == 400
    note = api(logged, "/api/diary", {"title": "Gradien", "body": "m = Δy/Δx", "lesson_slug": "gradient-mountain"}).get_json()["note"]
    assert "Gradien" in logged.get("/diary").get_data(as_text=True)
    upd = api(logged, "/api/diary", {"id": note["id"], "title": "Gradien!", "body": "baru"}).get_json()
    assert upd["note"]["title"] == "Gradien!"
    assert api(logged, "/api/diary", {"id": note["id"], "delete": True}).get_json()["deleted"]
    assert db.tables["diary_notes"] == []
    assert api(logged, "/api/diary", {"id": "x", "delete": True}).status_code == 404


def test_diary_isolated_between_students(app, db):
    a, b = app.test_client(), app.test_client()
    register(a)
    register(b, username="budi_garis", email="budi@sekolah.id")
    note = api(a, "/api/diary", {"title": "Rahasia A", "body": "x"}).get_json()["note"]
    assert "Rahasia A" not in b.get("/diary").get_data(as_text=True)
    assert api(b, "/api/diary", {"id": note["id"], "title": "hack"}).status_code in (404, 502, 503)
    assert api(b, "/api/diary", {"id": note["id"], "delete": True}).status_code == 404


def test_prefs_and_bookmarks(logged):
    r = api(logged, "/api/prefs", {"theme": "dark", "avatar": "pilot", "music": True, "reminder_time": "19:30"}).get_json()
    assert r["prefs"]["theme"] == "dark" and r["prefs"]["avatar"] == "pilot" and r["prefs"]["reminder_time"] == "19:30"
    assert api(logged, "/api/prefs", {"reminder_time": "25:99"}).status_code == 400
    assert 'data-pref-theme="dark"' in logged.get("/dashboard").get_data(as_text=True)
    assert api(logged, "/api/bookmark", {"slug": "gradient-mountain"}).get_json()["on"] is True
    assert api(logged, "/api/bookmark", {"slug": "gradient-mountain", "list": "favorites"}).get_json()["on"] is True
    assert api(logged, "/api/bookmark", {"slug": "gradient-mountain"}).get_json()["on"] is False
    assert api(logged, "/api/bookmark", {"slug": "nope"}).status_code == 404


def test_secret_missions_sequential_and_master(logged):
    assert api(logged, "/api/runs", {"kind": "secret", "ref": "jembatan-titik"}).status_code == 403
    assert logged.get("/secret/jembatan-titik").status_code == 302
    xp = 0
    for m in SECRET_MISSIONS:
        res = play_quiz(logged, "secret", m["slug"], key_for)
        assert res["passed"] and res["points"] == 300
        xp += res["xp_awarded"]
        last = res
    assert xp == 50 * len(SECRET_MISSIONS)
    assert any(a["slug"] == "master-of-straight-lines" for a in last["new_achievements"])
    again = play_quiz(logged, "secret", SECRET_MISSIONS[0]["slug"], key_for)
    assert again["xp_awarded"] == 0


def test_secret_items_include_hints(logged):
    data = api(logged, "/api/runs", {"kind": "secret", "ref": "menara-koordinat"}).get_json()
    assert all(q.get("hint") for q in data["items"]) and all("answer" not in q for q in data["items"])


def test_real_life_money_answers_and_badge(logged):
    case = REAL_CASES[0]
    answers = {"RL1-1": "Rp25.000", "RL1-2": 1, "RL1-3": "10"}
    res = play_quiz(logged, "reallife", case["slug"], lambda item: answers[item["id"]])
    assert res["passed"] and res["score"] == 100 and res["xp_awarded"] == 40
    for c in REAL_CASES[1:]:
        last = play_quiz(logged, "reallife", c["slug"], key_for)
    assert any(a["slug"] == "equation-solver" for a in last["new_achievements"])


def test_tutor_basic_mode(logged):
    r = api(logged, "/api/tutor", {"message": "persamaan garis melalui (1, 2) dan (3, 6)"}).get_json()
    assert r["engine"] == "basic" and "y = 2x" in r["reply"]
    assert api(logged, "/api/tutor", {"message": ""}).status_code == 400
    assert api(logged, "/api/tutor", {"message": "x" * 2000}).status_code == 400
    lat = api(logged, "/api/tutor", {"message": "latihan", "mode": "latihan"}).get_json()
    assert lat["practice"]["answer"]


def test_tutor_rate_limit(logged):
    from scarline.api import TUTOR_LIMIT

    for _ in range(TUTOR_LIMIT):
        assert api(logged, "/api/tutor", {"message": "apa itu gradien?"}).status_code == 200
    assert api(logged, "/api/tutor", {"message": "apa itu gradien?"}).status_code == 429


def test_tutor_requires_login(client):
    from tests.conftest import csrf_from

    token = csrf_from(client)
    assert client.post("/api/tutor", json={"message": "hai"}, headers={"X-CSRF-Token": token}).status_code == 401


def test_tutor_ai_failure_falls_back(logged, app, monkeypatch):
    import anthropic

    from scarline import tutor

    app.config["ANTHROPIC_API_KEY"] = "sk-test"

    def boom(*a, **k):
        raise anthropic.APIConnectionError(request=__import__("httpx2").Request("POST", "https://example.invalid"))

    monkeypatch.setattr(tutor, "ask_claude", boom)
    r = api(logged, "/api/tutor", {"message": "apa itu gradien?"}).get_json()
    assert r["engine"] == "basic" and r["notice"] and "Gradien" in r["reply"]


def test_new_games_playable(logged, db):
    from tests.test_app import solve_round

    for slug in ("line-detective", "parallel-perpendicular"):
        data = api(logged, "/api/runs", {"kind": "game", "ref": slug, "difficulty": "hard"}).get_json()
        for i in range(data["total"]):
            res = api(logged, f"/api/runs/{data['run_id']}/answer", {"index": i, "answer": solve_round(slug, data["run_id"], i, logged)}).get_json()
            assert res["correct"]
        fin = api(logged, f"/api/runs/{data['run_id']}/finish").get_json()
        assert fin["percent"] >= 95
    assert len(db.tables["game_attempts"]) == 2


def test_line_detective_wrong_reveals_suspect(logged):
    from tests.test_app import solve_round

    data = api(logged, "/api/runs", {"kind": "game", "ref": "line-detective", "difficulty": "easy"}).get_json()
    right = solve_round("line-detective", data["run_id"], 0, logged)
    wrong = (right + 1) % len(data["items"][0]["lines"])
    res = api(logged, f"/api/runs/{data['run_id']}/answer", {"index": 0, "answer": wrong}).get_json()
    assert not res["correct"] and res["reveal"]["index"] == wrong and res["tries_left"] == 1


def test_streak_and_recommendations(logged):
    complete_mission(logged, "coordinate-city")
    html = logged.get("/dashboard").get_data(as_text=True)
    assert "Learning Streak" in html and "1</b> hari berturut-turut" in html
    assert "Kerjakan Pre-Test dulu" in html


def test_map_has_twelve_stops(logged):
    html = logged.get("/map").get_data(as_text=True)
    assert html.count('role="listitem" class="region') == 12
    for name in ("Welcome to SCARLINE", "Pre-Test", "Coordinate City", "Real Life Line Adventure", "Final Line Challenge", "Post-Test", "SCARLINE Champion"):
        assert name in html


def test_search_index(logged):
    items = logged.get("/search-index.json").get_json()
    assert any("Gradien" in i["title"] or "gradien" in i["text"].lower() for i in items)
    assert any(i["url"] == "/tutor" for i in items)


def test_without_migration_v2_features_degrade(app, db):
    db.missing_tables = {"assessment_attempts", "mistakes", "diary_notes", "user_preferences", "challenge_progress"}
    c = app.test_client()
    assert register(c).status_code == 302
    for path in ("/dashboard", "/map", "/profile", "/mission/coordinate-city", "/playground", "/visual", "/tutor", "/settings", "/"):
        assert c.get(path).status_code == 200, path
    assert "belum aktif" in c.get("/pretest").get_data(as_text=True)
    assert c.get("/playground/line-detective").status_code == 302
    assert api(c, "/api/runs", {"kind": "pretest"}).status_code == 503
    # fitur lama tetap jalan dan kesalahan tidak membuat error
    res = play_quiz(c, "lesson", "coordinate-city", key_for)
    assert res["passed"]
    assert api(c, "/api/lessons/coordinate-city/complete").get_json()["ok"]
