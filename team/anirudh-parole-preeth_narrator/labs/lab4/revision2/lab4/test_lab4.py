"""Offline tests for the Lab 4 multi-agent workflow."""

from unittest.mock import patch
from copy import deepcopy

from narrator import narrator_tools
from lab4 import evidence_agent

from lab4 import orchestrator
from lab4.evidence_agent import run as evidence_run


def test_evidence_agent_retrieves_known_thread():
    result = evidence_run("THR-001")

    assert result["ok"] is True
    assert result["signal_count"] > 0
    assert result["decision"] == "ready_for_analysis"


def test_evidence_agent_handles_unknown_thread():
    result = evidence_run("THR-999")

    assert result["ok"] is True
    assert result["signal_count"] == 0
    assert result["decision"] == "insufficient_evidence"


def test_evidence_agent_rejects_invalid_thread():
    result = evidence_run("INVALID")

    assert result["ok"] is False
    assert result["decision"] == "stop"


def test_orchestrator_calls_analysis_for_known_thread():
    fake_result = {
        "ok": True,
        "decision": "summary_accepted",
    }

    with patch(
        "lab4.orchestrator.analysis_agent.run",
        return_value=fake_result,
    ) as fake_analysis:
        result = orchestrator.run("THR-001")

    assert result["status"] == "completed"
    fake_analysis.assert_called_once_with(
        "THR-001", result["evidence"]["signals"]
    )


def test_orchestrator_skips_analysis_without_evidence():
    with patch("lab4.orchestrator.analysis_agent.run") as fake_analysis:
        result = orchestrator.run("THR-999")

    assert result["status"] == "insufficient_evidence"
    fake_analysis.assert_not_called()


def test_orchestrator_stops_for_invalid_thread():
    with patch("lab4.orchestrator.analysis_agent.run") as fake_analysis:
        result = orchestrator.run("INVALID")

    assert result["status"] == "stopped"
    fake_analysis.assert_not_called()


def test_orchestrator_reports_analysis_failure():
    with patch(
        "lab4.orchestrator.analysis_agent.run",
        return_value={
            "ok": False,
            "decision": "analysis_failed",
        },
    ):
        result = orchestrator.run("THR-001")

    assert result["status"] == "analysis_failed"


def test_orchestrator_preserves_accepted_analysis():
    expected = {
        "ok": True,
        "decision": "summary_accepted",
        "output": {"status": "ok"},
    }

    with patch(
        "lab4.orchestrator.analysis_agent.run",
        return_value=expected,
    ):
        result = orchestrator.run("THR-001")

    assert result["analysis"] == expected
    assert result["reason"] == "summary_accepted"

def test_orchestrator_passes_exact_evidence_to_analysis():
    with patch(
        "lab4.orchestrator.analysis_agent.run",
        return_value={"ok": True, "decision": "summary_accepted"},
    ) as fake_analysis:
        result = orchestrator.run("THR-001")

    passed_thread_id, passed_signals = fake_analysis.call_args.args
    assert passed_thread_id == "THR-001"
    assert passed_signals == result["evidence"]["signals"]
    assert passed_signals is result["evidence"]["signals"]



def _mock_evidence(monkeypatch, payload):
    monkeypatch.setattr(
        evidence_agent.narrator_tools,
        "get_thread_signals",
        lambda thread_id: payload,
    )


def _valid_evidence_payload():
    return deepcopy(narrator_tools.get_thread_signals("THR-001"))


def test_evidence_agent_rejects_mismatched_signal_count(monkeypatch):
    payload = _valid_evidence_payload()
    payload["signal_count"] += 1
    _mock_evidence(monkeypatch, payload)

    result = evidence_agent.run("THR-001")
    assert result["ok"] is False
    assert result["decision"] == "stop"


def test_evidence_agent_rejects_duplicate_signal_ids(monkeypatch):
    payload = _valid_evidence_payload()
    payload["signals"].append(deepcopy(payload["signals"][0]))
    payload["signal_count"] += 1
    _mock_evidence(monkeypatch, payload)

    result = evidence_agent.run("THR-001")
    assert result["ok"] is False
    assert "Duplicate signal_id" in result["error"]


def test_evidence_agent_rejects_cross_thread_signal(monkeypatch):
    payload = _valid_evidence_payload()
    payload["signals"][0]["thread_id"] = "THR-002"
    _mock_evidence(monkeypatch, payload)

    result = evidence_agent.run("THR-001")
    assert result["ok"] is False
    assert "another thread" in result["error"]


def test_evidence_agent_rejects_missing_signal_field(monkeypatch):
    payload = _valid_evidence_payload()
    payload["signals"][0].pop("content")
    _mock_evidence(monkeypatch, payload)

    result = evidence_agent.run("THR-001")
    assert result["ok"] is False
    assert "missing or extra fields" in result["error"]


def test_evidence_agent_rejects_inconsistent_found_flag(monkeypatch):
    payload = _valid_evidence_payload()
    payload["found"] = False
    _mock_evidence(monkeypatch, payload)

    result = evidence_agent.run("THR-001")
    assert result["ok"] is False
    assert "'found' does not match signals" in result["error"]
