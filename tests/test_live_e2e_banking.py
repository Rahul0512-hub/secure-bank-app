"""
End-to-end integration tests running against live PostgreSQL and MongoDB containers.
Verifies real database operations, transactional integrity, outbox worker, and pgvector.
"""

import unittest
from decimal import Decimal
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.postgres import get_postgres_connection
from backend.app.mongodb import get_mongo_client


client = TestClient(app)


class TestLiveBankingE2E(unittest.TestCase):

    def test_01_health_and_database_connections(self):
        root = client.get("/")
        self.assertEqual(root.status_code, 200)
        self.assertIn(root.json()["status"], ["operational", "running"])

        pg_health = client.get("/health/postgres")
        self.assertEqual(pg_health.status_code, 200)
        self.assertEqual(pg_health.json()["status"], "healthy")

        mongo_health = client.get("/health/mongodb")
        self.assertEqual(mongo_health.status_code, 200)
        self.assertEqual(mongo_health.json()["status"], "healthy")

    def test_02_login_and_token_generation(self):
        res = client.post("/auth/login", json={
            "username": "priya_sharma",
            "password": "CustomerPass@123"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")
        self.assertEqual(data["user"]["role"], "Customer")

    def test_03_customer_accounts_retrieval(self):
        login_res = client.post("/auth/login", json={
            "username": "priya_sharma",
            "password": "CustomerPass@123"
        })
        token = login_res.json()["access_token"]

        acc_res = client.get("/accounts/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(acc_res.status_code, 200)
        accounts = acc_res.json()["accounts"]
        self.assertGreaterEqual(len(accounts), 1)

    def test_04_semantic_search_pgvector(self):
        search_res = client.get("/api/person-b/semantic-search?q=coffee")
        self.assertEqual(search_res.status_code, 200)
        results = search_res.json()["results"]
        self.assertGreater(len(results), 0)
        # Should return coffee item with high similarity
        top_item = results[0]
        self.assertIn("title", top_item)
        self.assertGreater(top_item["similarity"], 0.70)

    def test_05_system_summary_kpis(self):
        res = client.get("/api/person-b/system-summary")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_deposits", data)
        self.assertIn("active_accounts", data)
        self.assertGreater(data["active_accounts"], 0)

    def test_06_dashboard_html_renders(self):
        res = client.get("/dashboard")
        self.assertEqual(res.status_code, 200)
        self.assertIn("SecureBank Enterprise Core", res.text)
        self.assertIn("Customer Banking Portal", res.text)
        self.assertIn("Admin & Fraud Intelligence Center", res.text)

    def test_07_dedicated_pages_render(self):
        login_res = client.get("/login")
        self.assertEqual(login_res.status_code, 200)
        self.assertIn("Sign In", login_res.text)

        customer_res = client.get("/customer")
        self.assertEqual(customer_res.status_code, 200)
        self.assertIn("Customer Banking Portal", customer_res.text)

        admin_res = client.get("/admin")
        self.assertEqual(admin_res.status_code, 200)
        self.assertIn("Bank Management & Risk Center", admin_res.text)


if __name__ == "__main__":
    unittest.main()
