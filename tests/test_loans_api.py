import unittest
from decimal import Decimal
from datetime import date
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.tokens import create_access_token


client = TestClient(app)


class TestLoansAPI(unittest.TestCase):

    def token(self, role="Customer", user_id=1024):
        return create_access_token(
            user_id=user_id,
            username="priya_sharma",
            role=role,
        )

    def headers(self, role="Customer"):
        return {"Authorization": f"Bearer {self.token(role=role)}"}

    def test_unauthenticated_loan_access_denied(self):
        res = client.get("/loans/me")
        self.assertEqual(res.status_code, 401)

    def test_loan_calculator_endpoint(self):
        res = client.post(
            "/loans/calculator",
            json={"principal": 100000, "annual_rate": 10.0, "tenure_months": 12}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("monthly_emi", data)
        self.assertIn("total_payable", data)
        self.assertGreater(data["total_payable"], 100000)

    @patch("backend.app.loans.get_postgres_connection")
    def test_customer_view_own_loans(self, mock_db):
        manager = MagicMock()
        connection = manager.__enter__.return_value
        cursor = MagicMock()
        cursor.fetchall.return_value = [
            (1, 1024, Decimal("500000.00"), Decimal("9.50"), "Active", date(2025, 1, 1), date(2027, 1, 1))
        ]
        connection.execute.return_value = cursor
        mock_db.return_value = manager

        res = client.get("/loans/me", headers=self.headers())
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["loans"][0]["status"], "Active")

    @patch("backend.app.loans.get_postgres_connection")
    def test_customer_apply_loan(self, mock_db):
        manager = MagicMock()
        connection = manager.__enter__.return_value
        cursor = MagicMock()
        cursor.fetchone.return_value = (
            2, 1024, Decimal("250000.00"), Decimal("8.50"), "Pending", date(2026, 1, 1), date(2028, 1, 1)
        )
        connection.execute.return_value = cursor
        mock_db.return_value = manager

        res = client.post(
            "/loans/apply",
            json={"loan_amount": 250000.0, "interest_rate": 8.5, "tenure_months": 24},
            headers=self.headers()
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()["loan"]["status"], "Pending")

    @patch("backend.app.loans.get_postgres_connection")
    def test_admin_update_loan_status(self, mock_db):
        manager = MagicMock()
        connection = manager.__enter__.return_value
        mock_db.return_value = manager

        res = client.patch(
            "/loans/2/status",
            json={"status": "Approved"},
            headers=self.headers(role="Admin")
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "Approved")


if __name__ == "__main__":
    unittest.main()
