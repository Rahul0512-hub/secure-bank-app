import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.app.auth import router
from backend.app.main import app
from backend.app.security import hash_password
from backend.app.tokens import decode_access_token


client = TestClient(app)


class TestLoginAPI(unittest.TestCase):

    def test_unknown_user_returns_401(self):
        connection = MagicMock()
        connection.__enter__.return_value.execute.return_value.fetchone.return_value = None

        with patch("backend.app.auth.get_postgres_connection", return_value=connection):
            response = client.post(
                "/auth/login",
                json={
                    "username": "unknown_user",
                    "password": "WrongPassword@123",
                },
            )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json()["detail"],
            "Invalid username or password",
        )

    def test_wrong_password_returns_401(self):
        password_hash = hash_password("CorrectPassword@123")

        connection = MagicMock()
        connection.__enter__.return_value.execute.return_value.fetchone.return_value = (
            1,
            "testuser",
            password_hash,
            "Customer",
        )

        with patch("backend.app.auth.get_postgres_connection", return_value=connection):
            response = client.post(
                "/auth/login",
                json={
                    "username": "testuser",
                    "password": "WrongPassword@123",
                },
            )

        self.assertEqual(response.status_code, 401)

    def test_correct_credentials_return_jwt(self):
        password_hash = hash_password("CorrectPassword@123")

        connection = MagicMock()
        connection.__enter__.return_value.execute.return_value.fetchone.return_value = (
            1,
            "testuser",
            password_hash,
            "Customer",
        )

        with patch("backend.app.auth.get_postgres_connection", return_value=connection):
            response = client.post(
                "/auth/login",
                json={
                    "username": "testuser",
                    "password": "CorrectPassword@123",
                },
            )

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["token_type"], "bearer")
        self.assertEqual(data["expires_in"], 1800)

        payload = decode_access_token(data["access_token"])
        self.assertEqual(payload["sub"], "1")
        self.assertEqual(payload["username"], "testuser")
        self.assertEqual(payload["role"], "Customer")


if __name__ == "__main__":
    unittest.main()
