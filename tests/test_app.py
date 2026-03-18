import pytest
import os
import tempfile
from app import create_app
from models import db


@pytest.fixture
def app():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")

        app = create_app("testing")
        app.config["DATABASE"] = db_path
        app.config["TESTING"] = True

        db.db_path = db_path
        db.initialize()

        yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class TestConfig:
    def test_config_loading(self, app):
        assert app.config["TESTING"] is True

    def test_database_initialized(self, app):
        with app.app_context():
            from models import db

            with db.get_connection() as conn:
                tables = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
                table_names = [t[0] for t in tables]

                assert "players" in table_names
                assert "matches" in table_names
                assert "users" in table_names


class TestAuthRoutes:
    def test_login_page(self, client):
        response = client.get("/auth/login")
        assert response.status_code == 200

    def test_register_page(self, client):
        response = client.get("/auth/register")
        assert response.status_code == 200

    def test_register_user(self, client):
        response = client.post(
            "/auth/register",
            data={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
                "confirm_password": "password123",
            },
            follow_redirects=True,
        )
        assert (
            b"Registration successful" in response.data or b"logged in" in response.data
        )


class TestMainRoutes:
    def test_dashboard_redirects(self, client):
        response = client.get("/")
        assert response.status_code == 302

    def test_dashboard_requires_login(self, client):
        response = client.get("/dashboard", follow_redirects=True)
        assert b"login" in response.data.lower()

    def test_players_page(self, client):
        response = client.get("/players")
        assert response.status_code == 200

    def test_team_page(self, client):
        response = client.get("/team")
        assert response.status_code == 200

    def test_predict_page(self, client):
        response = client.get("/predict")
        assert response.status_code == 200


class TestAPIEndpoints:
    API_KEY = "sportvision-api-key-2024"

    def test_api_players(self, client):
        response = client.get("/api/players", headers={"X-API-Key": self.API_KEY})
        assert response.status_code == 200
        assert response.is_json

    def test_api_matches(self, client):
        response = client.get("/api/matches", headers={"X-API-Key": self.API_KEY})
        assert response.status_code == 200
        assert response.is_json

    def test_api_team_performance(self, client):
        response = client.get(
            "/api/team_performance", headers={"X-API-Key": self.API_KEY}
        )
        assert response.status_code == 200
        assert response.is_json

    def test_create_player_api(self, client):
        response = client.post(
            "/api/players",
            json={"name": "Test Player", "position": "Forward"},
            headers={"X-API-Key": self.API_KEY},
        )
        assert response.status_code == 201

    def test_create_match_api(self, client):
        response = client.post(
            "/api/matches",
            json={
                "match_date": "2024-01-01",
                "opponent": "Team A",
                "venue": "Home",
                "team_goals": 2,
                "opponent_goals": 1,
            },
            headers={"X-API-Key": self.API_KEY},
        )
        assert response.status_code == 201


class TestUpload:
    def test_upload_page_requires_login(self, client):
        response = client.get("/upload", follow_redirects=True)
        assert b"login" in response.data.lower()


class TestAdmin:
    def test_admin_requires_admin(self, client):
        response = client.get("/admin", follow_redirects=True)
        assert b"login" in response.data.lower()
