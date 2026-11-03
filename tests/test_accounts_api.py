import unittest
from decimal import Decimal
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.tokens import create_access_token


client = TestClient(app)


class TestAccountsAPI(unittest.TestCase):

    def token(self, role="Customer", user_id=1010):
        return create_access_token(
            user_id=user_id,
            username="test_user",
            role=role,
        )

    def mock_connection(self, rows=None, single_row=None, total=0):
        manager = MagicMock()
        connection = manager.__enter__.return_value

        cursor = MagicMock()
        cursor.fetchall.return_value = rows or []
        cursor.fetchone.return_value = single_row
        connection.execute.return_value = cursor

        return manager, connection

    def test_missing_token_returns_401(self):
        response = client.get("/accounts/me")
        self.assertEqual(response.status_code, 401)

    @patch("backend.app.accounts.get_postgres_connection")
    def test_customer_sees_only_own_accounts(self, mock_db):
        row = (
            1,
            "1234567890123456",
            "Savings",
            Decimal("15000.5000"),
            "INR",
            "Active",
        )

        manager, connection = self.mock_connection(rows=[row])
        mock_db.return_value = manager

        response = client.get(
            "/accounts/me",
            headers={"Authorization": f"Bearer {self.token()}"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(
            response.json()["accounts"][0]["account_number"],
            "************3456",
        )
        self.assertEqual(
            response.json()["accounts"][0]["balance"],
            "15000.5000",
        )

        query, params = connection.execute.call_args.args
        self.assertIn("WHERE user_id = %s", query)
        self.assertEqual(params, (1010,))

    @patch("backend.app.accounts.get_postgres_connection")
    def test_customer_can_view_own_account(self, mock_db):
        row = (
            1,
            "1234567890123456",
            "Savings",
            Decimal("5000.0000"),
            "INR",
            "Active",
        )

        manager, connection = self.mock_connection(single_row=row)
        mock_db.return_value = manager

        response = client.get(
            "/accounts/1",
            headers={"Authorization": f"Bearer {self.token()}"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["account"]["account_id"], 1)

        query, params = connection.execute.call_args.args
        self.assertIn("account_id = %s AND user_id = %s", query)
        self.assertEqual(params, (1, 1010))

    @patch("backend.app.accounts.get_postgres_connection")
    def test_customer_cannot_view_another_users_account(self, mock_db):
        manager, connection = self.mock_connection(single_row=None)
        mock_db.return_value = manager

        response = client.get(
            "/accounts/99",
            headers={"Authorization": f"Bearer {self.token()}"},
        )

        self.assertEqual(response.status_code, 404)

    @patch("backend.app.accounts.get_postgres_connection")
    def test_customer_cannot_access_admin_accounts(self, mock_db):
        response = client.get(
            "/accounts/admin/all",
            headers={"Authorization": f"Bearer {self.token(role='Customer')}"},
        )

        self.assertEqual(response.status_code, 403)
        mock_db.assert_not_called()

    @patch("backend.app.accounts.get_postgres_connection")
    def test_admin_can_list_all_accounts(self, mock_db):
        row = (
            2,
            "9876543210987654",
            "Current",
            Decimal("25000.0000"),
            "INR",
            "Active",
        )

        manager, connection = self.mock_connection(rows=[row])
        count_cursor = MagicMock()
        count_cursor.fetchone.return_value = (1,)
        connection.execute.side_effect = [
            connection.execute.return_value,
            count_cursor,
        ]
        mock_db.return_value = manager

        response = client.get(
            "/accounts/admin/all",
            headers={"Authorization": f"Bearer {self.token(role='Admin')}"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(response.json()["count"], 1)


if __name__ == "__main__":
    unittest.main()
