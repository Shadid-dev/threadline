"""Run from the repository root:  python3 -m unittest service.test_app"""
import os
import tempfile
import unittest

os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(tempfile.mkdtemp(), "test.db")   # never touch the real database

from fastapi.testclient import TestClient

from service import app as service
from service.storage import Database, DbApprovalQueue, DbThreadStore

SIGNAL = {"signal_id": "SIG-001", "source": "monitor", "service": "checkout",
          "timestamp": "2026-11-17T14:01:00-05:00", "content": "Checkout error rate 18 percent"}


class ServiceTests(unittest.TestCase):
    def setUp(self):
        service.STORE.threads.clear()
        service.DB.put("threads", [])
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


    def test_threads_and_approvals_survive_a_restart(self):
        approval_id = self.client.post("/signals", json=dict(SIGNAL, signal_id="SIG-003")).json()["approval_id"]
        self.client.post(f"/approvals/{approval_id}", json={"decision": "reject", "by": "Shadid", "reason": "test"})
        # A "restart": brand-new objects that only share the database file.
        db = Database(os.environ["DATABASE_URL"])
        self.assertEqual([t["thread_id"] for t in DbThreadStore(db).threads], ["THR-001"])
        proposal = next(p for p in DbApprovalQueue(db)._load() if p["proposal_id"] == approval_id)
        self.assertEqual(proposal["status"], "rejected")
        events = [e["event"] for e in db.audit_entries() if e["proposal_id"] == approval_id]
        self.assertEqual(events, ["submitted", "rejected"])   # H3: both steps, in order


if __name__ == "__main__":
    unittest.main()
