"""Offline tests for the Lab 4 multi-agent workflow."""

from unittest.mock import patch

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
    fake_analysis.assert_called_once_with("THR-001")


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
