# INSE 691 - Lab 4: Multi-Agent Systems Orchestration (ThreadLine)

Name: Anirudh Parole Preeth
Concordia Student ID: 40351389
Subject: INSE 691 - Foundations of AI Agent Systems

## 1. Background and justification

ThreadLine Lab 4 extends the Lab 3 evidence-grounded Narrator by adding a multi-agent architecture. The goal is to separate evidence retrieval, incident analysis, and workflow coordination into distinct components. This makes the system easier to test and gives the orchestration layer explicit control over whether analysis should proceed.

Given a thread ID, the Evidence Agent uses the existing Lab 3 retrieval tool to obtain signals associated with that thread. The Orchestrator checks the retrieval result. If the identifier or retrieval operation is invalid, it stops the workflow. If the thread has no signals, it returns an insufficient-evidence result without spending a model call. If signals are available, it invokes the Analysis Agent, which reuses the existing Gemini-powered Narrator and its summary-validation process.

The design deliberately reuses Lab 3 rather than implementing another summarizer. The Lab 4 addition is the coordination layer and agent separation, not a replacement for the existing evidence and validation contract.

## 2. Agent decomposition: functionality, attributes and behaviour

### Evidence Agent

**Functionality.** Retrieve evidence for one requested incident thread.

**Attributes.** Requested thread ID, retrieval result, signal list, signal count, decision, and error information.

**Behaviour.** It calls the existing `get_thread_signals` tool. A successful retrieval with signals returns `ready_for_analysis`. A valid thread with no signals returns `insufficient_evidence`. Invalid identifiers, retrieval errors, unexpected result shapes, or thread mismatches return a stop/error result.

### Analysis Agent

**Functionality.** Generate an evidence-grounded incident summary using the existing Lab 3 Narrator.

**Attributes.** Thread ID, accepted flag, structured output, validation result, stop reason, and execution trace.

**Behaviour.** It loads environment configuration, constructs the existing Gemini client, calls the Narrator, and returns the output and validation information. It reports success only when the Narrator's result is accepted; exceptions and rejected summaries are reported as failures.

### Orchestrator

**Functionality.** Coordinate the agents and return one workflow result.

**Attributes.** Thread ID, evidence result, analysis result, overall status, and reason.

**Behaviour.** It calls Evidence Agent first. It stops on evidence errors, skips analysis if no signals exist, and invokes Analysis Agent only when evidence is available. It returns `completed` only if the analysis result is accepted; otherwise it returns `analysis_failed`.

The decomposition assigns retrieval, summarization, and coordination to separate modules. This separation supports focused unit tests and avoids duplicating the Lab 3 summarization and validation logic.

## 3. Agent decision-making scheme

The system combines deterministic, rule-based routing with LLM-based analysis.

The Evidence Agent classifies retrieval outcomes:
- Retrieval error or invalid input: stop.
- Valid thread with no signals: insufficient evidence.
- Valid thread with signals: ready for analysis.

The Orchestrator applies the following policy:
1. Request evidence for the thread.
2. Stop if evidence retrieval fails.
3. Return `insufficient_evidence` if no signals are available.
4. Call the Analysis Agent when signals are available.
5. Return `completed` if the summary is accepted; otherwise return `analysis_failed`.

The Analysis Agent delegates summary generation to the Lab 3 Gemini-powered Narrator. That existing component applies its own evidence restrictions and validation gate. The orchestration decisions are deterministic; the summary content is produced by the language model under the existing contract.

## 4. Agent coordination and orchestration

**Static coordination.** Agent roles and the initial execution order are predefined. Evidence retrieval occurs before analysis, and the Orchestrator is the central coordinator. Agents communicate through Python function calls and structured dictionaries.

**Dynamic coordination.** The next action depends on runtime results. A missing-evidence result skips analysis, a retrieval error stops the workflow, and an unsuccessful analysis is returned as a failure. This avoids unnecessary model calls when there is no evidence to analyze.

The prototype uses sequential, centrally controlled orchestration. It is not a distributed multi-agent system in which agents independently negotiate or communicate. The Evidence Agent's result is used for routing; the existing Narrator retrieves its own evidence again during analysis. Reducing that duplicate retrieval is a possible improvement.

## 5. Test prompts and observed results

1. **Valid checkout incident:** Analyze THR-001 and produce an evidence-grounded summary.
   **Expected:** Retrieve signals and return an accepted summary.
   **Observed:** Live run completed; six signals retrieved; summary accepted.

2. **Unknown thread:** Analyze THR-999.
   **Expected:** Return insufficient evidence without invoking Analysis Agent.
   **Observed:** Covered by automated orchestration tests.

3. **Invalid identifier:** Analyze INVALID.
   **Expected:** Stop safely without invoking Analysis Agent.
   **Observed:** Covered by automated orchestration tests.

4. **Analysis failure:** Analyze THR-001 while simulating an Analysis Agent failure.
   **Expected:** Report analysis failure and preserve the evidence result.
   **Observed:** Covered by a controlled automated test.

5. **Valid login incident:** Analyze THR-002 and produce an evidence-grounded summary.
   **Expected:** Retrieve login signals and return an accepted summary.
   **Observed:** Live run completed; two signals retrieved; summary accepted.

**Automated testing.** The combined command `python -m pytest narrator/tests lab4/test_lab4.py -q` passed 57 tests: 49 Lab 3 regression tests and 8 Lab 4 tests. Python compilation checks for the three Lab 4 implementation modules also passed.

## 6. Prototype files and execution

Lab 4 files:
- `lab4/evidence_agent.py` — evidence retrieval and classification.
- `lab4/analysis_agent.py` — adapter around the existing Lab 3 Narrator.
- `lab4/orchestrator.py` — workflow coordination.
- `lab4/test_lab4.py` — automated orchestration tests.
- `lab4/test_prompts.md` — five test prompts and expected behaviour.
- `lab4/results/` — sanitized records of the two successful live demonstrations.

Run from the root of the existing ThreadLine repository with the virtual environment activated and the required `.env` configuration already present:

```bash
python -m pytest narrator/tests lab4/test_lab4.py -q
python -m lab4.orchestrator
```

The first command runs the tests. The second is illustrative only if a command-line entry point is added; the current prototype exposes `run(thread_id)` as a Python function, so the live workflow can be demonstrated with:

```python
from lab4 import orchestrator
result = orchestrator.run("THR-001")
print(result)
```

## 7. Limitations and reflection

The prototype uses a fixed sequential orchestration policy. It demonstrates multiple distinct agent components and runtime-dependent routing, but it does not implement autonomous peer-to-peer planning or distributed execution. The Analysis Agent reuses the Lab 3 Narrator, which retrieves its own evidence; the orchestrator does not directly pass the Evidence Agent's signal list to the summarizer. Live model runs were demonstrated for THR-001 and THR-002, while the other scenarios were checked with automated tests, including a controlled analysis-failure test. More tests across additional fixtures and a shared evidence handoff would improve the prototype.
