"""Evidence Agent for ThreadLine Lab 4."""
from narrator import narrator_tools


def _failure(thread_id, message):
    return {
        "agent": "EvidenceAgent", "ok": False,
        "thread_id": thread_id, "error": message,
        "signals": [], "signal_count": 0, "decision": "stop",
    }


def run(thread_id: str) -> dict:
    """Retrieve and strictly validate evidence before analysis."""
    if not isinstance(thread_id, str) or not narrator_tools.THREAD_ID_RE.fullmatch(thread_id):
        return _failure(thread_id, "Invalid thread ID")

    try:
        result = narrator_tools.get_thread_signals(thread_id)
    except Exception as exc:
        return _failure(thread_id, f"{type(exc).__name__}: {exc}")

    if not isinstance(result, dict):
        return _failure(thread_id, "Unexpected evidence response format")
    if result.get("error"):
        return _failure(thread_id, str(result["error"]))
    if result.get("thread_id") != thread_id:
        return _failure(thread_id, "Evidence response thread ID mismatch")

    found = result.get("found")
    records = result.get("signals")
    count = result.get("signal_count")

    if not isinstance(found, bool):
        return _failure(thread_id, "'found' must be Boolean")
    if not isinstance(records, list):
        return _failure(thread_id, "'signals' must be a list")
    if isinstance(count, bool) or not isinstance(count, int):
        return _failure(thread_id, "'signal_count' must be an integer")
    if count != len(records):
        return _failure(thread_id, "Signal count does not match records")
    if found != bool(records):
        return _failure(thread_id, "'found' does not match signals")

    required = set(narrator_tools.SIGNAL_FIELDS)
    seen = set()

    for i, record in enumerate(records):
        label = f"Signal at index {i}"
        if not isinstance(record, dict):
            return _failure(thread_id, f"{label} is not an object")
        if set(record) != required:
            return _failure(thread_id, f"{label} has missing or extra fields")

        sid = record["signal_id"]
        if not isinstance(sid, str) or not sid.strip():
            return _failure(thread_id, f"{label} has invalid signal_id")
        if sid in seen:
            return _failure(thread_id, f"Duplicate signal_id: {sid}")
        seen.add(sid)

        for field in ("source", "service", "content"):
            if not isinstance(record[field], str):
                return _failure(thread_id, f"{label}: {field} must be a string")

        if record["thread_id"] != thread_id:
            return _failure(thread_id, f"{label} belongs to another thread")

        ts = record["timestamp"]
        if ts not in (None, "") and (
            not isinstance(ts, str) or not narrator_tools.TIME_RE.fullmatch(ts)
        ):
            return _failure(thread_id, f"{label} has invalid timestamp")

    return {
        "agent": "EvidenceAgent",
        "ok": True,
        "thread_id": thread_id,
        "signals": records,
        "signal_count": count,
        "decision": "ready_for_analysis" if records else "insufficient_evidence",
    }
