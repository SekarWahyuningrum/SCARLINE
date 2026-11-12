import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scarline import create_app  # noqa: E402
from tests.fakes import FakeSupabase  # noqa: E402

PASSWORD = "Garis123"


@pytest.fixture
def db():
    return FakeSupabase()


@pytest.fixture
def app(db):
    return create_app({"TESTING": True, "SECRET_KEY": "test-secret", "SITE_URL": "http://localhost"}, db=db)


@pytest.fixture
def client(app):
    return app.test_client()


def csrf_from(client, path="/login"):
    html = client.get(path).get_data(as_text=True)
    m = re.search(r'name="csrf-token" content="([^"]+)"', html)
    return m.group(1)


def register(client, username="rina_garis", email="rina@sekolah.id", password=PASSWORD):
    token = csrf_from(client, "/register")
    return client.post("/register", data={
        "csrf_token": token, "full_name": "Rina Kartika", "username": username, "email": email,
        "class_name": "VIII-A", "password": password, "confirm_password": password,
    })


@pytest.fixture
def logged(client):
    resp = register(client)
    assert resp.status_code == 302, resp.get_data(as_text=True)[:500]
    return client


def api(client, url, payload=None):
    token = csrf_from(client, "/dashboard")
    return client.post(url, json=payload or {}, headers={"X-CSRF-Token": token})
