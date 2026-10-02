import json
from pathlib import Path

HERE = Path(__file__).parent

with open(HERE / "fixtures" / "signals.json") as f:
    signals = json.load(f)

print("Loaded", len(signals), "signals")
print()

for s in signals:
    print(s["timestamp"], "|", s["source"], "|", s["content"])