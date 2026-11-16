import unittest
from unittest.mock import MagicMock, patch
from bson.decimal128 import Decimal128
from decimal import Decimal
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.analytics import text_to_embedding

client = TestClient(app)


class TestAnalyticsAndDashboardAPI(unittest.TestCase):

    def test_root_endpoint(self):
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "running")
        self.assertIn("dashboard_url", data)

    def test_health_endpoint(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    def test_dashboard_endpoint_returns_html(self):
        response = client.get("/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        self.assertIn("SecureBank Intelligence Center", response.text)

    def test_text_to_embedding(self):
        food_vec = text_to_embedding("Swiggy dinner and Starbucks coffee")
        self.assertEqual(food_vec, "[0.95, 0.05, 0.05, 0.02]")

        travel_vec = text_to_embedding("Uber cab to airport terminal")
        self.assertEqual(travel_vec, "[0.05, 0.96, 0.04, 0.02]")

        bill_vec = text_to_embedding("Electricity utility bill payment")
        self.assertEqual(bill_vec, "[0.02, 0.03, 0.95, 0.10]")

        other_vec = text_to_embedding("General banking question")
        self.assertEqual(other_vec, "[0.02, 0.02, 0.08, 0.97]")

    @patch("backend.app.analytics.get_mongo_client")
    def test_spending_analytics_success(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_audit = MagicMock()
        mock_audit.aggregate.return_value = [
            {"_id": "TRANSFER_COMPLETED", "total_amount": Decimal128(Decimal("1500.00")), "transaction_count": 2}
        ]

        mock_fraud = MagicMock()
        mock_fraud.find.return_value.sort.return_value.limit.return_value = [
            {
                "_id": "673200000000000000000001",
                "user_id": 1,
                "amount": 85000.0,
                "category": "International Wire",
                "reason": "High-value transfer",
                "severity": "HIGH",
                "status": "OPEN",
                "created_at": datetime.now(timezone.utc),
            }
        ]

        mock_logins = MagicMock()
        mock_logins.find.return_value.sort.return_value.limit.return_value = [
            {
                "email": "customer@securebank.com",
                "ip_address": "127.0.0.1",
                "status": "SUCCESS",
                "occurred_at": datetime.now(timezone.utc),
            }
        ]

        with patch("backend.app.analytics.get_audit_collection", return_value=mock_audit), \
             patch("backend.app.analytics.get_fraud_alerts_collection", return_value=mock_fraud), \
             patch("backend.app.analytics.get_login_events_collection", return_value=mock_logins):
            response = client.get("/api/person-b/analytics/spending")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["spendingByCategory"]), 1)
        self.assertEqual(data["spendingByCategory"][0]["totalSpent"], 1500.0)
        self.assertEqual(len(data["fraudAlerts"]), 1)
        self.assertEqual(len(data["loginEvents"]), 1)

    @patch("backend.app.analytics.get_mongo_client")
    def test_fraud_evaluate_triggers_alert(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_audit = MagicMock()
        mock_fraud = MagicMock()

        with patch("backend.app.analytics.get_audit_collection", return_value=mock_audit), \
             patch("backend.app.analytics.get_fraud_alerts_collection", return_value=mock_fraud):
            response = client.post(
                "/api/person-b/fraud/evaluate",
                json={
                    "user_id": 1,
                    "amount": 95000.0,
                    "category": "International Wire",
                    "description": "High value wire transfer",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["fraud_triggered"])
        self.assertEqual(data["severity"], "HIGH")
        self.assertTrue(mock_fraud.insert_one.called)

    @patch("backend.app.analytics.get_mongo_client")
    def test_login_event_recording(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_logins = MagicMock()
        mock_logins.count_documents.return_value = 1

        with patch("backend.app.analytics.get_login_events_collection", return_value=mock_logins):
            response = client.post(
                "/api/person-b/login-events",
                json={
                    "user_id": 1,
                    "email": "test@securebank.com",
                    "ip_address": "192.168.1.1",
                    "status": "SUCCESS",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "logged")
        self.assertTrue(mock_logins.insert_one.called)

    @patch("backend.app.analytics.get_postgres_connection")
    def test_semantic_search_with_mocked_results(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cur

        mock_cur.fetchall.return_value = [
            (101, "TRANSACTION", "Food & Dining", "Starbucks Coffee", "Morning coffee", Decimal("450.00"), Decimal("0.9850"))
        ]
        mock_get_conn.return_value = mock_conn

        response = client.get("/api/person-b/semantic-search?q=coffee")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["query"], "coffee")
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["title"], "Starbucks Coffee")
        self.assertEqual(data["results"][0]["similarity"], 0.985)


if __name__ == "__main__":
    unittest.main()
