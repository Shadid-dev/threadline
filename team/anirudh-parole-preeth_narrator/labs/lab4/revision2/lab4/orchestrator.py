"""Orchestrator for the ThreadLine Lab 4 multi-agent prototype."""

from lab4 import analysis_agent, evidence_agent


def run(thread_id: str) -> dict:
    """Coordinate evidence retrieval and incident analysis."""
    evidence = evidence_agent.run(thread_id)

    # Stop if evidence retrieval failed or the thread ID was invalid.
    if not evidence["ok"]:
        return {
            "orchestrator": "ThreadLineOrchestrator",
            "thread_id": thread_id,
            "status": "stopped",
            "reason": "evidence_error",
            "evidence": evidence,
            "analysis": None,
        }

    # Do not spend a model call when there is no evidence to analyze.
    if evidence["decision"] == "insufficient_evidence":
        return {
            "orchestrator": "ThreadLineOrchestrator",
            "thread_id": thread_id,
            "status": "insufficient_evidence",
            "reason": "no_signals_found",
            "evidence": evidence,
            "analysis": None,
        }

    analysis = analysis_agent.run(thread_id, evidence["signals"])

    return {
        "orchestrator": "ThreadLineOrchestrator",
        "thread_id": thread_id,
        "status": (
            "completed" if analysis["ok"] else "analysis_failed"
        ),
        "reason": analysis["decision"],
        "evidence": evidence,
        "analysis": analysis,
    }
