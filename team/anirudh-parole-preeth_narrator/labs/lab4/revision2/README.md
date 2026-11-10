# ThreadLine Lab 4 — Revision 2

## Overview

Revision 2 improves the Lab 4 multi-agent workflow by adding strict evidence
validation, single-retrieval evidence sharing, regression tests, and reproducible
test reports.

The original Lab 3 Narrator implementation is included in `narrator/`.
The Lab 4 workflow is in `lab4/`.

## Architecture

1. **Evidence Agent** retrieves signals for one thread and validates the response.
2. **Orchestrator** controls the workflow and stops when evidence is invalid
   or insufficient.
3. **Analysis Agent** passes the validated evidence to the Narrator.
4. **Narrator** generates a structured incident summary.
5. **Validator** checks the summary against the Lab 2 contract using the same
   evidence records.

Evidence is retrieved once by the Evidence Agent. The exact records are passed
through the Orchestrator and Analysis Agent to the Narrator and Validator.
Signal content is treated as data, never as instructions.

## Project structure

- `narrator/` — Narrator agent, tools, contract, prompts, and tests.
- `lab4/` — Evidence Agent, Analysis Agent, Orchestrator, and Lab 4 tests.
- `fixtures/signals.json` — signal fixture data.
- `requirements.txt` — standalone Python dependencies.
- `lab4/results/` — demo outputs and test reports.

## Requirements

- Python 3.10 or newer
- pip
- A Gemini API key only for live model execution

## Fresh-clone setup

From the repository root, enter this directory:

    cd team/anirudh-parole-preeth_narrator/labs/lab4/revision2

Create and activate a virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

Install dependencies:

    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt

## Gemini configuration

Live model execution requires a Gemini API key.

Create a `.env` file in the repository root (not inside this directory):

    GEMINI_API_KEY=your-key-here

Optional model override:

    GEMINI_MODEL=your-supported-model

The default model is `gemini-3.5-flash-lite`.

Never commit `.env` or expose API keys in logs, source files, or reports.

The automated test suite uses offline tests and does not require a Gemini API key.

## Run tests

Run the complete Narrator and Lab 4 test suite from this directory:

    python -m pytest narrator/tests lab4/test_lab4.py -v

The suite covers agent-loop behaviour, tool execution, parsing, evidence
validation, summary validation, orchestration, and evidence handoff.

## Test reports

Generated reports are stored in `lab4/results/`:

- `test_run.log` — complete verbose pytest output.
- `test-results.xml` — JUnit-compatible test report.

Regenerate both reports:

    set -o pipefail
    python -m pytest narrator/tests lab4/test_lab4.py -v \
        --junitxml=lab4/results/test-results.xml \
        2>&1 | tee lab4/results/test_run.log

## Evidence validation

The Evidence Agent rejects:

- Invalid thread identifiers.
- Malformed response objects.
- Missing or extra signal fields.
- Incorrect signal counts or inconsistent `found` flags.
- Duplicate signal identifiers.
- Signals belonging to another thread.
- Invalid timestamps and field types.

The Validator also checks supplied evidence for duplicate IDs, malformed
records, and cross-thread records.

## Scope

This is an isolated Revision 2 package. It does not overwrite the shared
team-level `lab4/` prototype or the original submitted Lab 4 package.
