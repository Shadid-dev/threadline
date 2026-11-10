# Narrator tool-using agent (INSE 691 Lab 3, Anirudh Parole Preeth)

Adds tool use to the Narrator agent specified in Lab 2. Everything lives in this
`narrator/` folder; no existing ThreadLine file was changed.

## Setup (once)

From the repository root (`threadline/`):

    python -m venv .venv
    source .venv/bin/activate          # Windows: .venv\Scripts\activate
    pip install -r narrator/requirements.txt

Create a free Gemini key at https://aistudio.google.com/apikey and put it in a
file named `.env` in the repository root (already in .gitignore, never commit it):

    GEMINI_API_KEY=your-key-here

Optional: `GEMINI_MODEL=...` to override the default `gemini-3.5-flash-lite`
(the team's model). Combining the built-in code execution tool with custom
functions needs a Gemini 3 or newer model.

## Run the automated tests (no key needed)

    python -m pytest narrator/tests -v

## Check the live setup first (key needed, about 10 seconds)

    python -m narrator.check_setup

It makes one small request with both tool types and tells you whether the key,
the model and the built-in + custom tool combination work. If the default model
fails it tries others and prints the exact `GEMINI_MODEL=` line for `.env`.

## Run the test prompts with the real model (key needed)

    python -m narrator.test_prompts_narrator          # all prompts P1-P7
    python -m narrator.test_prompts_narrator P1 P4    # selected prompts

Valid IDs: P1 P2 P3 P4 P5 P6 P7. The runner waits 5 seconds between prompts and retries
rate-limit/server errors up to 3 times (10s, 30s, 60s); set `NARRATOR_PAUSE_SECONDS` to change the gap.

Each prompt writes `narrator/traces/<ID>.txt` (readable) and `<ID>.json` (full),
plus `narrator/traces/summary.json`. Line 2 of every `.txt` trace states whether the run was
ACCEPTED or NOT ACCEPTED and why. Traces from this script are labelled
`MODE: REAL`. Traces from the unit tests use a scripted fake model and are
labelled `SIMULATED`; they are never submission traces.

## Files

| File | Purpose |
|---|---|
| contract.py | Lab 2 output schema (exact copy) and the ten validity rules |
| narrator_tools.py | Custom tools: get_thread_signals, validate_summary |
| tool_schemas.py | Strict model-facing schemas (also used to check arguments) |
| narrator_agent.py | System instruction, Gemini client, agent loop, final gate, trace |
| make_prompt_fixtures.py | Builds the modified fixtures for P3 and P4 |
| test_prompts_narrator.py | The seven test prompts and the trace writer |
| check_setup.py | Live check of key, model and tool combination |
| tests/ | 49 automated tests (tools, validator, agent loop, response parsing, entry points) |
| DESIGN.md | Design document |
