"""Run from repository root: python3 -m lab4.run --mode dynamic --output lab4/traces/dynamic.json"""
import argparse
import json
from pathlib import Path

from .scenarios import SCENARIOS, FaultBackend
from .system import GeminiBackend, OfflineBackend, Orchestrator, ThreadStore, save_json


def run_scenarios(mode="dynamic", backend=None, selected=None):
    outputs = []
    for scenario in SCENARIOS:
        if selected and scenario["name"] not in selected:
            continue
        store = ThreadStore()
        for seed in scenario["seed"]:
            choices = store.candidates(seed["service"], seed["timestamp"])
            store.commit(seed, choices[0]["thread_id"] if choices else None)
        active = backend or OfflineBackend()
        if scenario.get("fault"):
            active = FaultBackend(active, scenario["fault"])
        system = Orchestrator(mode, active, store)
        output = system.run(scenario["signal"])
        outputs.append({"scenario": scenario["name"], "prompt": scenario["prompt"],
                        "seed": scenario["seed"], "expected_decision": scenario["decision"],
                        **output, "final_store": store.threads})
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["static", "dynamic"], default="dynamic")
    parser.add_argument("--backend", choices=["offline", "gemini"], default="offline")
    parser.add_argument("--model", default="gemini-flash-latest")
    parser.add_argument("--scenario", choices=[s["name"] for s in SCENARIOS], action="append")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--signal-file", type=Path,
                        help="Process one JSON signal against a fresh run-local store")
    args = parser.parse_args()
    backend = GeminiBackend(args.model) if args.backend == "gemini" else OfflineBackend()
    if args.signal_file:
        outputs = [Orchestrator(args.mode, backend).run(json.loads(args.signal_file.read_text()))]
    else:
        outputs = run_scenarios(args.mode, backend, args.scenario)
    if args.output:
        save_json(args.output, outputs)
        print(f"Saved {len(outputs)} run(s) to {args.output}")
    for run in outputs:
        result = run["result"]
        print(run.get("scenario", "custom"), result["correlation"]["decision"], result["status"])


if __name__ == "__main__":
    main()
