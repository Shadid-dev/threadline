# ThreadLine

An incident-management course prototype using synthetic evidence and rules-first agent coordination.

## Lab 4 - multi-agent system

See [the Lab 4 guide](lab4/README.md) for setup and [the report](lab4/REPORT.md) for the six required deliverables. The readable [PDF report](lab4/REPORT.pdf) is included.

Run from this repository root:

```sh
python3 -m lab4.run --mode dynamic
python3 -m lab4.run --mode static
python3 -m unittest lab4.test_system -v
```

The default backend is offline rules, not an LLM simulation. An optional Gemini backend runs the Narrator and Action Drafter as separate model agents. See the guide for genuine live traces and configuration.

## Earlier prototype

Root-level `correlator.py`, `agent.py`, `tools.py`, and `fixtures/` contain the original single-agent prototype. Lab 4 preserves those files and isolates its state and tests. Legacy timestamp and duplicate-handling limitations are documented in the Lab 4 report.

Never commit `.env`, API keys, virtual environments, or private incident data. All committed incident fixtures in this lab are synthetic.
