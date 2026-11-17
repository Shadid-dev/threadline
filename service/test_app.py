"""Run from the repository root:  python3 -m unittest service.test_app"""
import os
import tempfile
import unittest

os.environ["THREADLINE_QUEUE_DIR"] = tempfile.mkdtemp()   # never touch the real queue in tests

from fastapi.testclient import TestClient

from service import app as service

SIGNAL = {"signal_id": "SIG-001", "source": "monitor", "service": "checkout",
          "timestamp": "2026-11-17T14:01:00-05:00", "content": "Checkout error rate 18 percent"}


class ServiceTests(unittest.TestCase):
    def setUp(self):
        service.STORE.threads.clear()
        self.client = TestClient(service.app)

    def test_health(self):
        self.assertEqual(self.client.get("/health").json()["status"], "ok")

    def test_signal_creates_a_thread_and_a_pending_proposal(self):
        result = self.client.post("/signals", json=SIGNAL).json()
        self.assertEqual(result["correlation"]["decision"], "create")
        self.assertEqual(result["status"], "awaiting_approval")
        self.assertEqual(len(self.client.get("/threads").json()), 1)
        self.assertIn(result["approval_id"], [p["proposal_id"] for p in self.client.get("/approvals").json()])

    def test_bad_signal_is_rejected_with_422_and_not_stored(self):
        bad = dict(SIGNAL, signal_id="oops")
        response = self.client.post("/signals", json=bad)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(self.client.get("/threads").json(), [])

    def test_approval_needs_a_name(self):
        approval_id = self.client.post("/signals", json=dict(SIGNAL, signal_id="SIG-002")).json()["approval_id"]
        refused = self.client.post(f"/approvals/{approval_id}", json={"decision": "approve", "by": "", "reason": "ok"})
        self.assertEqual(refused.status_code, 409)
        ok = self.client.post(f"/approvals/{approval_id}", json={"decision": "approve", "by": "Shadid", "reason": "matches"})
        self.assertEqual(ok.json()["status"], "approved")


if __name__ == "__main__":
    unittest.main()
