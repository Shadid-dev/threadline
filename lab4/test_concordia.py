"""Campus API adapter tests with mocked HTTP; not live campus execution evidence."""
import io
import json
import os
import unittest
from unittest.mock import patch

from .scenarios import signal
from .system import ConcordiaBackend, Orchestrator


def response(content):
    return io.BytesIO(json.dumps({"choices": [{"message": {"content": content}}]}).encode())


class ConcordiaTests(unittest.TestCase):
    def test_valid_campus_responses_follow_the_live_agent_path(self):
        backend = ConcordiaBackend(api_key="test-key")
        summary = {"observations": [{"signal_id": "SIG-001", "quote": signal()["content"]}]}
        action = {"kind": "inspect_evidence", "cited_signals": ["SIG-001"],
                  "requires_human_approval": True}
        with patch("urllib.request.urlopen", side_effect=[response(json.dumps(summary)),
                                                         response(json.dumps(action))]) as http:
            output = Orchestrator(backend=backend).run(signal())
        self.assertEqual(http.call_count, 2)
        self.assertEqual(output["result"]["status"], "awaiting_approval")
        self.assertEqual(output["result"]["action"], action)
        self.assertEqual(output["result"]["executed_actions"], [])

    def test_uses_guide_endpoint_and_model_without_leaking_key_in_body(self):
        backend = ConcordiaBackend(api_key="test-key")
        with patch("urllib.request.urlopen", return_value=response('{"observations": []}')) as http:
            backend.generate("Narrator", "Quote evidence", {"evidence": []}, {"type": "object"})
        request = http.call_args.args[0]
        body = json.loads(request.data)
        self.assertEqual(request.full_url, "http://localhost:4000/v1/chat/completions")
        self.assertEqual(body["model"], "qwen3-8b")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-key")
        self.assertNotIn("test-key", request.data.decode())
        self.assertEqual(http.call_args.kwargs["timeout"], 60)

    def test_reasoning_and_fenced_json_are_parsed_but_prose_is_not(self):
        backend = ConcordiaBackend(api_key="test-key")
        text = '<think>private reasoning</think>\n```json\n{"observations": []}\n```'
        with patch("urllib.request.urlopen", return_value=response(text)):
            self.assertEqual(backend.generate("Narrator", "", {}, {}), {"observations": []})
        with patch("urllib.request.urlopen", return_value=response("Definitely fine!")):
            with self.assertRaises(ValueError):
                backend.generate("Narrator", "", {}, {})

    def test_missing_tunnel_escalates_without_publishing_summary(self):
        backend = ConcordiaBackend(api_key="test-key")
        with patch("urllib.request.urlopen", side_effect=ConnectionRefusedError()):
            output = Orchestrator(backend=backend).run(signal())
        self.assertEqual(output["result"]["status"], "needs_human_review")
        self.assertIsNone(output["result"]["summary"])
        self.assertTrue(any(e["event"] == "error" for e in output["trace"]))
        self.assertNotIn("test-key", json.dumps(output))

    def test_campus_output_still_passes_through_grounding_checks(self):
        backend = ConcordiaBackend(api_key="test-key")
        bad = json.dumps({"observations": [{"signal_id": "SIG-001", "quote": "Invented cause"}]})
        with patch("urllib.request.urlopen", side_effect=lambda *a, **kw: response(bad)) as http:
            output = Orchestrator(backend=backend).run(signal())
        self.assertEqual(http.call_count, 2)
        self.assertIsNone(output["result"]["summary"])
        self.assertIsNone(output["result"]["action"])


if __name__ == "__main__":
    unittest.main()
