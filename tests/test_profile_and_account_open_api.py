import unittest
from decimal import Decimal
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.tokens import create_access_token


client = TestClient(app)


class TestProfileAndAccountOpenAPI(unittest.TestCase):

    def token(self, role="Customer", user_id=1024):
        return create_access_token(
            user_id=user_id,
            username="priya_sharma",
            role=role,
        )

    def headers(self, role="Customer"):
        return {"Authorization": f"Bearer {self.token(role=role)}"}

    @patch("backend.app.auth.get_postgres_connection")
    def test_get_current_user_profile(self, mock_db):
        manager = MagicMock()
        connection = manager.__enter__.return_value
        cursor = MagicMock()
        cursor.fetchone.return_value = (
            1024, "priya_sharma", "priya@securebank.com", "+919876543210", "Customer", "2026-11-16T12:00:00Z"
        )
        connection.execute.return_value = cursor
        mock_db.return_value = manager

        res = client.get("/auth/me", headers=self.headers())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["username"], "priya_sharma")
        self.assertEqual(res.json()["email"], "priya@securebank.com")

    @patch("backend.app.accounts.get_postgres_connection")
    def test_open_new_account(self, mock_db):
        manager = MagicMock()
        connection = manager.__enter__.return_value
        cursor = MagicMock()
        cursor.fetchone.return_value = (
            55, 1024, "SBIN9999888811", "Checking", Decimal("15000.00"), "INR", "Active"
        )
        connection.execute.return_value = cursor
        mock_db.return_value = manager

        res = client.post(
            "/accounts/open",
            json={"account_type": "Checking", "initial_balance": 15000.0, "currency": "INR"},
            headers=self.headers()
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()["account"]["account_type"], "Checking")
        self.assertEqual(res.json()["account"]["balance"], "15000.00")

    @patch("backend.app.accounts.get_postgres_connection")
    def test_admin_freeze_account(self, mock_db):
        manager = MagicMock()
        connection = manager.__enter__.return_value
        mock_db.return_value = manager

        res = client.patch(
            "/accounts/55/status",
            json={"status": "Frozen"},
            headers=self.headers(role="Admin")
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "Frozen")


if __name__ == "__main__":
    unittest.main()
