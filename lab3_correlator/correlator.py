import json
from pathlib import Path

HERE = Path(__file__).parent
WINDOW_MINUTES = 30


def to_minutes(t):
    hours, minutes = t.split(":")
    return int(hours) * 60 + int(minutes)


def signal_time(s):
    return to_minutes(s["timestamp"])


with open(HERE / "fixtures" / "signals.json") as f:
    signals = json.load(f)

signals.sort(key=signal_time)

threads = []

for s in signals:
    placed = False

    for t in threads:
        same_service = t["service"] == s["service"]
        gap = signal_time(s) - t["last_activity"]

        if same_service and gap <= WINDOW_MINUTES:
            t["signals"].append(s["signal_id"])
            t["last_activity"] = signal_time(s)
            s["thread_id"] = t["thread_id"]
            placed = True
            break

    if not placed:
        new_thread = {
            "thread_id": "THR-" + str(len(threads) + 1).zfill(3),
            "service": s["service"],
            "last_activity": signal_time(s),
            "signals": [s["signal_id"]],
        }
        threads.append(new_thread)
        s["thread_id"] = new_thread["thread_id"]

print("Found", len(threads), "threads")
print()

for t in threads:
    print(t["thread_id"], "|", t["service"], "|", len(t["signals"]), "signals")
    for sid in t["signals"]:
        print("     ", sid)
    print()