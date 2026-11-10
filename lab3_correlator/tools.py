import json
from pathlib import Path

HERE = Path(__file__).parent
STORE = HERE / "fixtures" / "threads.json"


def _load():
    if STORE.exists():
        with open(STORE) as f:
            return json.load(f)
    return []


def _save(threads):
    with open(STORE, "w") as f:
        json.dump(threads, f, indent=2)


def _parse_time(value: str) -> int:
    if value is None:
        raise ValueError("timestamp cannot be None")
    hours, minutes = value.split(":")
    return int(hours) * 60 + int(minutes)


def list_open_threads() -> list:
    """Return every thread that is currently open."""
    return [t for t in _load() if t["status"] == "open"]


def minutes_between(earlier: str, later: str) -> int:
    """Return the signed gap in minutes between two HH:MM timestamps."""
    return _parse_time(later) - _parse_time(earlier)


def find_candidate_threads(service: str | None, timestamp: str, window_minutes: int = 30) -> list:
    """Return open threads matching the service and within the window."""
    if service is None:
        return []
    out = []
    for t in list_open_threads():
        if t.get("service") != service:
            continue
        gap = abs(minutes_between(t["last_activity"], timestamp))
        if gap <= window_minutes:
            out.append(t)
    return out


def attach_signal(thread_id: str, signal_id: str, timestamp: str) -> dict:
    """Attach a signal to an existing thread and update its last activity."""
    threads = _load()
    for t in threads:
        if t["thread_id"] == thread_id:
            t["signals"].append(signal_id)
            t["last_activity"] = timestamp
            _save(threads)
            return {"ok": True, "thread_id": thread_id}
    return {"ok": False, "error": "thread not found"}


def create_thread(service: str | None, signal_id: str, timestamp: str) -> dict:
    """Open a new thread for a signal and return its id."""
    threads = _load()
    new_id = "THR-" + str(len(threads) + 1).zfill(3)
    threads.append({
        "thread_id": new_id,
        "service": service,
        "status": "open",
        "last_activity": timestamp,
        "signals": [signal_id],
    })
    _save(threads)
    return {"ok": True, "thread_id": new_id}