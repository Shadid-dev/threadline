import copy
import unittest

from .run import run_scenarios
from .scenarios import FaultBackend, signal
from .system import GroundingValidator, OfflineBackend, Orchestrator, ThreadStore


class SystemTests(unittest.TestCase):
    def test_all_scenario_correlation_results_and_no_execution(self):
        for mode in ("static", "dynamic"):
            for run in run_scenarios(mode):
                with self.subTest(mode=mode, scenario=run["scenario"]):
                    self.assertEqual(run["result"]["correlation"]["decision"], run["expected_decision"])
                    self.assertEqual(run["result"]["executed_actions"], [])

    def test_static_missing_service_runs_drafter_dynamic_skips_it(self):
        static = run_scenarios("static", selected=["missing_service"])[0]
        dynamic = run_scenarios("dynamic", selected=["missing_service"])[0]
        self.assertEqual(static["result"]["action"]["kind"], "request_service")
        self.assertIsNone(dynamic["result"]["action"])
        self.assertEqual(dynamic["result"]["status"], "needs_human_review")
        self.assertIsNone(dynamic["final_store"][0]["service"])

    def test_dynamic_retry_repairs_and_static_escalates(self):
        for mode, status, calls in [("static", "needs_human_review", 1), ("dynamic", "awaiting_approval", 2)]:
            system = Orchestrator(mode, FaultBackend())
            output = system.run(signal())
            self.assertEqual(output["result"]["status"], status)
            self.assertEqual(system.narrator.state.calls, calls)

    def test_repeated_rejection_is_bounded_and_untrusted_draft_not_published(self):
        system = Orchestrator(backend=FaultBackend(fault="always"))
        output = system.run(signal())
        self.assertEqual(system.narrator.state.calls, 2)
        self.assertIsNone(output["result"]["summary"])
        self.assertIsNone(output["result"]["action"])

    def test_injection_cannot_select_login_thread(self):
        run = run_scenarios(selected=["injection"])[0]
        self.assertEqual(run["result"]["correlation"]["thread_id"], "THR-001")
        self.assertEqual(run["final_store"][1]["service"], "login")
        self.assertNotIn("SIG-005", run["final_store"][1]["signals"])

    def test_duplicate_id_is_idempotent_and_conflicting_reuse_rejected(self):
        system = Orchestrator()
        system.run(signal())
        state = copy.deepcopy(system.store.threads)
        out = system.run(signal())
        self.assertEqual(out["result"]["status"], "duplicate_ignored")
        self.assertEqual(system.store.threads, state)
        with self.assertRaises(ValueError):
            system.run(signal(content="Different payload for same ID"))
        self.assertEqual(system.store.threads, state)

    def test_window_boundaries_and_dated_timestamps(self):
        store = ThreadStore()
        store.commit(signal(time="14:01"))
        self.assertTrue(store.candidates("checkout", signal(time="14:31")["timestamp"]))
        self.assertFalse(store.candidates("checkout", signal(time="14:32")["timestamp"]))
        self.assertFalse(store.candidates("checkout", signal(time="14:00")["timestamp"]))
        self.assertFalse(store.candidates(None, signal()["timestamp"]))
        self.assertFalse(store.candidates("login", signal()["timestamp"]))
        store.threads[0]["status"] = "closed"
        self.assertFalse(store.candidates("checkout", signal()["timestamp"]))

    def test_midnight_and_time_zone_offsets(self):
        store = ThreadStore()
        first = signal()
        first["timestamp"] = "2026-10-25T23:55:00-04:00"
        store.commit(first)
        self.assertTrue(store.candidates("checkout", "2026-10-26T00:05:00-04:00"))
        self.assertTrue(store.candidates("checkout", "2026-10-26T04:05:00+00:00"))

    def test_attach_tool_independently_rejects_wrong_service_and_closed_thread(self):
        store = ThreadStore()
        store.commit(signal())
        with self.assertRaises(ValueError):
            store.commit(signal("SIG-002", "login"), "THR-001")
        store.threads[0]["status"] = "closed"
        with self.assertRaises(ValueError):
            store.commit(signal("SIG-002"), "THR-001")

    def test_validator_rejects_unknown_citations_extra_fields_and_fabrication(self):
        validator = GroundingValidator()
        for draft in [{"observations": []},
                      {"observations": [{"signal_id": "SIG-999", "quote": "x"}]},
                      {"observations": [{"signal_id": "SIG-001", "quote": "Invented"}]},
                      {"observations": [{"signal_id": "SIG-001", "quote": "x", "extra": 1}]}]:
            self.assertFalse(validator.decide(draft, [signal()])["approved"])

    def test_invalid_input_never_mutates_store(self):
        for bad in [signal(time="99:01"), signal(service=""), {**signal(), "extra": True}]:
            system = Orchestrator()
            with self.assertRaises(ValueError):
                system.run(bad)
            self.assertEqual(system.store.threads, [])

    def test_provider_error_is_logged_without_fallback_or_action(self):
        class Broken(OfflineBackend):
            def generate(self, *args):
                raise RuntimeError("provider unavailable")
        output = Orchestrator(backend=Broken()).run(signal())
        self.assertEqual(output["result"]["status"], "needs_human_review")
        self.assertTrue(any(e["event"] == "error" for e in output["trace"]))
        self.assertIsNone(output["result"]["summary"])

    def test_invalid_action_cannot_bypass_approval(self):
        class Unsafe(OfflineBackend):
            def generate(self, role, instructions, payload, schema):
                value = super().generate(role, instructions, payload, schema)
                if role == "Action Drafter":
                    value["requires_human_approval"] = False
                return value
        output = Orchestrator(backend=Unsafe()).run(signal())
        self.assertIsNone(output["result"]["action"])
        self.assertEqual(output["result"]["status"], "needs_human_review")


if __name__ == "__main__":
    unittest.main()
