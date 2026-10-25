import sqlite3
import time
import pytest
from fastapi.testclient import TestClient
from api.auth import create_user
from api.config import settings
from api.main import app

APPLICANT = {"customer_age": 45, "customer_income": 50000, "home_ownership": "RENT", "employment_duration": 20, "loan_intent": "EDUCATION", "loan_grade": "B", "loan_amnt": 20000, "loan_int_rate": 4, "term_years": 1, "cred_hist_length": 9}

@pytest.fixture()
def client(tmp_path):
    original = settings.database_path
    object.__setattr__(settings, "database_path", tmp_path / "auth.sqlite3")
    with TestClient(app) as test_client:
        create_user("analyst@example.test", "CorrectHorse1", "Test Analyst")
        yield test_client
    object.__setattr__(settings, "database_path", original)

def sign_in(client):
    response = client.post("/auth/login", json={"username": "analyst@example.test", "password": "CorrectHorse1"})
    assert response.status_code == 200
    return response

def csrf(client):
    response = client.get("/auth/csrf")
    assert response.status_code == 200
    return response.json()["csrf_token"]

def test_predict_requires_session(client): assert client.post("/predict", json=APPLICANT).status_code == 401
def test_login_and_me(client):
    response = sign_in(client); assert response.json()["display_name"] == "Test Analyst"
    assert "httponly" in response.headers["set-cookie"].lower(); assert "samesite=lax" in response.headers["set-cookie"].lower()
    assert client.get("/auth/me").status_code == 200
def test_invalid_and_unknown_logins_are_indistinguishable(client):
    wrong = client.post("/auth/login", json={"username": "analyst@example.test", "password": "WrongPassword1"})
    unknown = client.post("/auth/login", json={"username": "nobody@example.test", "password": "WrongPassword1"})
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json()["detail"] == unknown.json()["detail"]
def test_csrf_required_and_valid_token_allows_prediction(client):
    sign_in(client)
    assert client.post("/predict", json=APPLICANT).status_code == 403
    assert client.post("/predict", json=APPLICANT, headers={"X-CSRF-Token": "invalid"}).status_code == 403
    response = client.post("/predict", json=APPLICANT, headers={"X-CSRF-Token": csrf(client)})
    assert response.status_code == 200; assert "default_probability" in response.json()
def test_logout_revokes_session(client):
    sign_in(client); token = csrf(client)
    assert client.post("/auth/logout", headers={"X-CSRF-Token": token}).status_code == 204
    assert client.get("/auth/me").status_code == 401
    assert client.post("/predict", json=APPLICANT, headers={"X-CSRF-Token": token}).status_code == 401
def test_expired_and_malformed_session_are_rejected(client):
    sign_in(client)
    with sqlite3.connect(settings.database_path) as db: db.execute("UPDATE sessions SET idle_expires_at=?", (int(time.time()) - 1,))
    assert client.get("/auth/me").status_code == 401
    client.cookies.set(settings.cookie_name, "not a valid session")
    assert client.get("/auth/me").status_code == 401
def test_rate_limit_and_cors(client):
    for _ in range(settings.login_limit): client.post("/auth/login", json={"username": "nobody", "password": "WrongPassword1"})
    assert client.post("/auth/login", json={"username": "nobody", "password": "WrongPassword1"}).status_code == 429
    response = client.options("/auth/me", headers={"Origin": "https://untrusted.example", "Access-Control-Request-Method": "GET"})
    assert "access-control-allow-origin" not in response.headers
