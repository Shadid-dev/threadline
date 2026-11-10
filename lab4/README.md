# ThreadLine Lab 4 - Multi-agent incident assistant

Shadid Alam Al Huda (40334643). Submission date: **27 October 2026**. This extends the Lab 3 Correlator with three additional role agents: Narrator, Grounding Validator, and Action Drafter. The agents cooperate through a central manager and an in-memory incident thread store.

## Run in VS Code

Open the `threadline` repository folder (the one that contains `README.md` and the `lab4` folder). Use Terminal > New Terminal. Run from that repository root, not from inside `lab4`.

```sh
python3 -m lab4.run --mode dynamic --output lab4/traces/my_dynamic.json
python3 -m lab4.run --mode static --output lab4/traces/my_static.json
python3 -m unittest lab4.test_system lab4.test_concordia -v
```

The default is an actual executable **rule-based** multi-agent prototype. It uses no API key, installed packages, or model calls. Its Narrator includes exact evidence quotations, not a generated causal explanation. The traces identify the backend as `offline-rules`.

## Optional live Gemini agents

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r lab4/requirements.txt
```

Create `.env` at the repository root with `GEMINI_API_KEY=your_key`. Keep it private. Then run:

```sh
python -m lab4.run --backend gemini --model gemini-3.5-flash-lite --mode dynamic --scenario attach --scenario missing_service --scenario injection --output lab4/traces/my_live.json
```

In Gemini mode, the model defaults to `gemini-flash-latest`; override with `--model MODEL_ID` if needed. Availability, quota, and latency depend on the provider. Only Narrator and Action Drafter invoke Gemini; Correlator and Validator remain deterministic. Each successful ordinary scenario typically uses two requests. Errors return `needs_human_review` and an error type in the trace, without silently substituting offline output. After an API failure, inspect the trace before retrying to avoid unnecessary quota use.

## Optional Concordia local LLM

This uses the supplied course guide's campus endpoint and `qwen3-8b` model. It calls the service directly from Python; installing Continue is optional for chatting in VS Code and does not connect the prototype automatically.

1. In a separate terminal, establish the campus tunnel and keep that terminal open:

   ```sh
   ssh -N -L 4000:aise-01.encs.concordia.ca:4000 YOUR_ENCS_USERNAME@login.encs.concordia.ca
   ```

   Replace `YOUR_ENCS_USERNAME` with your own login. Enter your ENCS password only in the terminal when SSH prompts for it.

2. In your private `.env` at the repository root, add:

   ```text
   CONCORDIA_API_KEY=your_personal_campus_key
   CONCORDIA_BASE_URL=http://localhost:4000/v1
   ```

   Use the key provided by the course administrator, not your Gemini key. `lab4/concordia.env.example` contains placeholders only.

3. In the project terminal, activate your virtual environment, install `lab4/requirements.txt` if needed, and run:

   ```sh
   python -m lab4.run --backend concordia --mode dynamic --scenario attach --scenario missing_service --scenario injection --output lab4/traces/my_concordia_live.json
   ```

   With no `--model` override, Concordia mode selects `qwen3-8b`. Requests have a 60-second timeout and no application retry for transport failures. A failed request produces a review result and an error type in the trace. Schema instructions do not guarantee valid model output; the existing validators still check every returned proposal.

The included campus adapter tests use mocked HTTP. They do not prove live campus connectivity. No Concordia live trace is included or claimed. A campus run needs your tunnel and personal campus key; the included successful Gemini traces remain valid evidence of the implemented live multi-agent path.

## What to read and submit

- `REPORT.md` / `REPORT.pdf`: six required sections, design choices, agent attributes, decision schemes and coordination.
- `system.py`: agent implementation, tool-backed state, output validation, and manager.
- `scenarios.py`, `test_prompts.json`: nine independent prompts and their starting state.
- `run.py`: CLI for both orchestration modes and a custom signal file.
- `test_system.py`, `test_concordia.py`: 18 system and mocked campus-adapter checks.
- `agent_schemas.json`: model response contracts.
- `traces/static.json`, `traces/dynamic.json`: actual offline executions, including labelled fault injection for retry tests.
- `traces/gemini_live.json`: successful live attach/injection runs and the intended missing-service review route using `gemini-3.5-flash-lite`. Earlier provider server errors are preserved separately in `traces/gemini_server_errors.json`.

No production integrations, outbound messaging, automatic remediation, or approval executor exist. Every draft requires approval; this is a status and output constraint rather than a working approval UI. Synthetic signal content can contain hostile instructions, which may be quoted as evidence but are never treated as trusted commands.

## Static versus dynamic

Static: Correlator -> Narrator -> Validator -> Action Drafter, once each, with a safety stop if validation fails.

Dynamic: the same core, but skip specialists for duplicate replay; request human review without drafting for missing service; return rejection feedback to Narrator once; escalate after two failures. Dynamic routing is controlled by code using runtime outcomes, not by an LLM manager. Agents communicate through typed-purpose JSON payloads; they do not share private model chats.

The new store uses full dated timestamps with numeric UTC offsets. It never edits Lab 3's `lab3_correlator/fixtures/threads.json`; each scenario is isolated. An older arrival starts another thread under this prototype's explicit no-backdating policy. That prevents timestamp regression but may split an incident; this tradeoff needs future evaluation.

## Your branch and team workflow

Your Lab 4 branch is `codex/shadid-lab4-multiagent`. It contains your individual lab, including a narrow implementation of roles needed for integration. It does not assign or replace teammates' individual deliverables. Each teammate should start their own branch from the team's agreed base and implement their own agent there. Review and merge compatible changes through pull requests; do not push everyone directly to `main`.

The existing repository is `Shadid-dev/threadline`. The separate `Shadid-dev/691_ThreadLine` repository was empty when checked, so this work preserves the repository with your Lab 3 history. Nothing is pushed to `main` by this lab task.
