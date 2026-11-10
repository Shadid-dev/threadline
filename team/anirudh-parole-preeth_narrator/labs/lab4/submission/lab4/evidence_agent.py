"""Evidence Agent for ThreadLine Lab 4.

Retrieves evidence for one incident thread and checks whether
the result is safe to pass to the Analysis Agent.
"""

from narrator import narrator_tools


def run(thread_id: str) -> dict:
    """Retrieve evidence and decide whether analysis can proceed."""
    try:
        result = narrator_tools.get_thread_signals(thread_id)
    except Exception as exc:
        return {
            "agent": "EvidenceAgent",
            "ok": False,
            "thread_id": thread_id,
            "error": f"{type(exc).__name__}: {exc}",
            "signals": [],
            "signal_count": 0,
            "decision": "stop",
        }

    if not isinstance(result, dict):
        return {
            "agent": "EvidenceAgent",
            "ok": False,
            "thread_id": thread_id,
            "error": "Unexpected evidence response format",
            "signals": [],
            "signal_count": 0,
            "decision": "stop",
        }

    # Invalid IDs, blocked access, and fixture errors must stop the workflow.
    if result.get("error"):
        return {
            "agent": "EvidenceAgent",
            "ok": False,
            "thread_id": thread_id,
            "error": result["error"],
            "signals": [],
            "signal_count": 0,
            "decision": "stop",
        }

    if result.get("thread_id") != thread_id:
        return {
            "agent": "EvidenceAgent",
            "ok": False,
            "thread_id": thread_id,
            "error": "Evidence response thread ID mismatch",
            "signals": [],
            "signal_count": 0,
            "decision": "stop",
        }

    if not result.get("found", False):
        return {
            "agent": "EvidenceAgent",
            "ok": True,
            "thread_id": thread_id,
            "signals": [],
            "signal_count": 0,
            "decision": "insufficient_evidence",
        }

    records = result.get("signals")
    if not isinstance(records, list):
        return {
            "agent": "EvidenceAgent",
            "ok": False,
            "thread_id": thread_id,
            "error": "Signals field is not a list",
            "signals": [],
            "signal_count": 0,
            "decision": "stop",
        }

    return {
        "agent": "EvidenceAgent",
        "ok": True,
        "thread_id": thread_id,
        "signals": records,
        "signal_count": len(records),
        "decision": (
            "insufficient_evidence" if len(records) == 0
            else "ready_for_analysis"
        ),
    }
