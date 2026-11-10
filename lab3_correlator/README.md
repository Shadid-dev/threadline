# Lab 3: Correlator with tools (earlier single-agent version)

This is the Correlator on its own, before the multi-agent prototype in `lab4/`. Kept for reference and for the course record.

| File | What it does |
|---|---|
| `correlator.py` | The core rule, no AI: groups the 8 test signals into threads. Run `python3 lab3_correlator/correlator.py` and you get `Found 2 threads`. |
| `agent.py` | Gemini agent that calls the tools below to correlate a signal (needs `GEMINI_API_KEY` in `.env`). |
| `tools.py` | The 5 custom tools: list open threads, minutes between, find candidate threads, attach signal, create thread. |
| `builtin_audit.py` | Uses Gemini's built-in code execution to audit the thread store (read-only). |
| `tool_schemas.json` | Input/output definitions of the tools. |
| `test_prompts.py`, `test_builtin_audit.py` | Test runs. |
| `fixtures/` | Invented test data: `signals.json` (8 signals, 2 incidents), `threads.json`, `audit_snapshot.json`. |
| `traces/` | Saved run records. |
| `practice/` | Small practice scripts from learning Python. |
| `REPORT.md` / `REPORT.pdf` | The Lab 3 report. |
