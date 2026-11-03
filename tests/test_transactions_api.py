import unittest
from decimal import Decimal
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.tokens import create_access_token


client = TestClient(app)


class TestTransactionsAPI(unittest.TestCase):

    def token(self, role="Customer", user_id=1010):
        return create_access_token(
            user_id=user_id,
            username="test_user",
            role=role,
        )

    def mock_connection(self, rows=None, single_row=None):
        manager = MagicMock()
        connection = manager.__enter__.return_value

        cursor = MagicMock()
        cursor.fetchall.return_value = rows or []
        cursor.fetchone.return_value = single_row
        connection.execute.return_value = cursor

        return manager, connection

    def headers(self, role="Customer"):
        return {"Authorization": f"Bearer {self.token(role=role)}"}

    def test_missing_token_returns_401(self):
        response = client.get("/transactions/me")
        self.assertEqual(response.status_code, 401)

    @patch("backend.app.transactions.get_postgres_connection")
    def test_non_customer_cannot_view_transactions(self, mock_db):
        response = client.get(
            "/transactions/me",
            headers=self.headers(role="Admin"),
        )

        self.assertEqual(response.status_code, 403)
        mock_db.assert_not_called()

    @patch("backend.app.transactions.get_postgres_connection")
    def test_customer_can_view_own_transactions(self, mock_db):
        row = (
            1,
            10,
            20,
            Decimal("500.0000"),
            "Transfer",
            "Test payment",
            "Completed",
            datetime(2026, 11, 3, tzinfo=timezone.utc),
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
            "/transactions/me",
            headers=self.headers(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(
            response.json()["transactions"][0]["amount"],
            "500.0000",
        )

        query, params = connection.execute.call_args_list[0].args
        self.assertIn("source.user_id = %s", query)
        self.assertIn("destination.user_id = %s", query)
        self.assertEqual(params, (1010, 1010, 50, 0))

    @patch("backend.app.transactions.get_postgres_connection")
    def test_customer_can_view_owned_transaction(self, mock_db):
        row = (
            1,
            10,
            20,
            Decimal("500.0000"),
            "Transfer",
            "Test payment",
            "Completed",
            datetime(2026, 11, 3, tzinfo=timezone.utc),
        )

        manager, connection = self.mock_connection(single_row=row)
        mock_db.return_value = manager

        response = client.get(
            "/transactions/1",
            headers=self.headers(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["transaction"]["transaction_id"], 1)

        query, params = connection.execute.call_args.args
        self.assertIn("t.transaction_id = %s", query)
        self.assertIn("source.user_id = %s OR destination.user_id = %s", query)
        self.assertEqual(params, (1, 1010, 1010))

    @patch("backend.app.transactions.get_postgres_connection")
    def test_customer_cannot_view_unowned_transaction(self, mock_db):
        manager, connection = self.mock_connection(single_row=None)
        mock_db.return_value = manager

        response = client.get(
            "/transactions/99",
            headers=self.headers(),
        )

        self.assertEqual(response.status_code, 404)

    @patch("backend.app.transactions.get_postgres_connection")
    def test_transfer_rejects_same_source_and_destination(self, mock_db):
        response = client.post(
            "/transactions/transfer",
            headers=self.headers(),
            json={
                "source_account_id": 10,
                "destination_account_id": 10,
                "amount": "100.0000",
                "description": "Test transfer",
            },
        )

        self.assertEqual(response.status_code, 400)
        mock_db.assert_not_called()

    @patch("backend.app.transactions.get_postgres_connection")
    def test_transfer_rejects_unowned_source_account(self, mock_db):
        manager, connection = self.mock_connection(single_row=None)
        mock_db.return_value = manager

        response = client.post(
            "/transactions/transfer",
            headers=self.headers(),
            json={
                "source_account_id": 10,
                "destination_account_id": 20,
                "amount": "100.0000",
                "description": "Test transfer",
            },
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(connection.execute.call_count, 1)

    @patch("backend.app.transactions.get_postgres_connection")
    def test_successful_transfer_calls_database_function(self, mock_db):
        manager, connection = self.mock_connection(single_row=(1,))
        connection.execute.side_effect = [
            MagicMock(fetchone=MagicMock(return_value=(10,))),
            MagicMock(fetchone=MagicMock(return_value=(501,))),
        ]
        mock_db.return_value = manager

        response = client.post(
            "/transactions/transfer",
            headers=self.headers(),
            json={
                "source_account_id": 10,
                "destination_account_id": 20,
                "amount": "100.0000",
                "description": "Test transfer",
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["transaction_id"], 501)
        self.assertEqual(response.json()["status"], "Completed")

        query, params = connection.execute.call_args_list[1].args
        self.assertIn("public.transfer_funds", query)
        self.assertEqual(params, (10, 20, Decimal("100.0000"), "Transfer", "Test transfer"))

    @patch("backend.app.transactions.get_postgres_connection")
    def test_transfer_database_error_returns_safe_response(self, mock_db):
        import psycopg

        manager = MagicMock()
        connection = manager.__enter__.return_value
        connection.execute.side_effect = psycopg.OperationalError("Simulated database error")
        mock_db.return_value = manager

        response = client.post(
            "/transactions/transfer",
            headers=self.headers(),
            json={
                "source_account_id": 10,
                "destination_account_id": 20,
                "amount": "100.0000",
            },
        )

        self.assertEqual(response.status_code, 503)
        self.assertNotIn("Simulated database error", response.text)


if __name__ == "__main__":
    unittest.main()
