"""Local integration checks; fake responses are not live model traces."""

import io
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import Mock, patch

from builtin_audit import audit_store


class AuditTests(unittest.TestCase):
    def test_registers_native_tool_and_logs_provider_code_and_result(self):
        steps = []
        for kind in ("code_execution_call", "code_execution_result", "model_output"):
            steps.append(SimpleNamespace(
                type=kind,
                model_dump=lambda **kwargs: {"type": "FAKE_TEST_STEP"},
            ))
        client = SimpleNamespace(interactions=SimpleNamespace(
            create=Mock(return_value=SimpleNamespace(steps=steps))))
        snapshot = [{"thread_id": "THR-TEST", "signals": ["SIG-X", "SIG-X"]}]
        output = io.StringIO()
        with patch("builtin_audit.tools.list_open_threads", return_value=snapshot), redirect_stdout(output):
            audit_store(model="test-model", client=client)
        args = client.interactions.create.call_args.kwargs
        self.assertEqual(args["tools"], [{"type": "code_execution"}])
        self.assertIn('"SIG-X", "SIG-X"', args["input"])
        self.assertIn("FAKE_TEST_STEP", output.getvalue())

    def test_text_only_response_is_rejected_as_missing_execution(self):
        client = SimpleNamespace(interactions=SimpleNamespace(
            create=Mock(return_value=SimpleNamespace(steps=[]))))
        with patch("builtin_audit.tools.list_open_threads", return_value=[]), redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, "No completed"):
                audit_store(model="test-model", client=client)


if __name__ == "__main__":
    unittest.main()
