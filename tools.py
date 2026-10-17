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


def list_open_threads() -> list:
    """Return every thread that is currently open."""
    return [t for t in _load() if t["status"] == "open"]


def minutes_between(earlier: str, later: str) -> int:
    """Return the gap in minutes between two HH:MM timestamps."""
    h1, m1 = earlier.split(":")
    h2, m2 = later.split(":")
    return (int(h2) * 60 + int(m2)) - (int(h1) * 60 + int(m1))


def find_candidate_threads(service: str, timestamp: str, window_minutes: int = 30) -> list:
    """Return open threads matching the service and within the window."""
    out = []
    for t in list_open_threads():
        if t["service"] != service:
            continue
        if minutes_between(t["last_activity"], timestamp) <= window_minutes:
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


def create_thread(service: str, signal_id: str, timestamp: str) -> dict:
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