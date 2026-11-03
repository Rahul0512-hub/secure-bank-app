import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import psycopg
from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


class TestRegistrationAPI(unittest.TestCase):

    def setUp(self):
        self.registration_data = {
            "username": "newcustomer",
            "password": "CustomerPass@123",
            "email": "newcustomer@example.com",
            "phone": "9876543210",
        }

    @patch("backend.app.auth.get_postgres_connection")
    def test_successful_registration(self, mock_connection):
        connection = MagicMock()
        mock_connection.return_value.__enter__.return_value = connection

        connection.execute.return_value.fetchone.return_value = (
            101,
            "newcustomer",
            "newcustomer@example.com",
            "9876543210",
            "Customer",
            datetime.now(timezone.utc),
        )

        response = client.post(
            "/auth/register",
            json=self.registration_data,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json()["message"],
            "Customer registered successfully",
        )
        self.assertEqual(response.json()["user"]["role"], "Customer")
        self.assertNotIn("password", response.json()["user"])
        self.assertNotIn("password_hash", response.json()["user"])

        database_parameters = connection.execute.call_args[0][1]
        self.assertNotEqual(
            database_parameters[1],
            self.registration_data["password"],
        )
        self.assertTrue(database_parameters[1].startswith("$argon2"))

    @patch("backend.app.auth.get_postgres_connection")
    def test_duplicate_account_returns_409(self, mock_connection):
        connection = MagicMock()
        mock_connection.return_value.__enter__.return_value = connection

        connection.execute.side_effect = psycopg.errors.UniqueViolation(
            "Duplicate account"
        )

        response = client.post(
            "/auth/register",
            json=self.registration_data,
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            response.json()["detail"],
            "Username or email already exists",
        )

    def test_invalid_email_returns_422(self):
        data = self.registration_data.copy()
        data["email"] = "not-an-email"

        response = client.post("/auth/register", json=data)

        self.assertEqual(response.status_code, 422)

    def test_short_password_returns_422(self):
        data = self.registration_data.copy()
        data["password"] = "short"

        response = client.post("/auth/register", json=data)

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
