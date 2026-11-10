# Narrator Tool-Using Agent: Design Document

## 1. Goal
Extend the Lab 2 Narrator so it fetches its own evidence, checks its own output
and computes time arithmetic exactly, while keeping every Lab 2 contract rule.

## 2. Architecture

    request ("Summarize THR-001")
        |
        v
    agent loop (narrator_agent.run) ---- sends instruction + tool list ----> Gemini
        ^                                                                     |
        |  function results                       function_call / text       |
        |                                          code execution (built-in, |
        |                                          runs on Google's servers) |
        +-- execute_tool: check args against schema, enforce thread lock <---+
        |     get_thread_signals -> fixtures/signals.json (read-only)
        |     validate_summary   -> Lab 2 schema + rules
        v
    final gate: validate_summary again (code, not model) -> accept / correct (max 2) / reject

The model chooses which tool to call and when. The loop only executes, bounds and records.

## 3. Tools

| Tool | Type | Why not the LLM alone |
|---|---|---|
| get_thread_signals(thread_id) | custom | The model cannot see project data; asked about THR-001 it can only guess. |
| validate_summary(thread_id, summary_json) | custom | Set equality, ordering and counting must be exact and repeatable; a model checking itself tends to confirm what it wrote. |
| code_execution | built-in (Gemini) | Minute gaps between timestamps and count comparisons; models make confident arithmetic slips. |

Rejected: Google Search and URL context (the contract forbids outside knowledge);
File Search (overlaps the team's retrieval component and could return other threads).

## 4. Decisions
- **Thread grouping.** `get_thread_signals` reproduces the Correlator's algorithm with a
  30-minute window (Team Starter Guide, the Correlator agent's instructions and
  `tools.find_candidate_threads`). `correlator.py` currently has `WINDOW_MINUTES = 5`,
  which splits checkout into five threads with the current timestamps; reported to the team.
  If signals already carry `thread_id`s, those assignments are used unchanged.
- **threads.json not used.** It is the Correlator agent's mutable test store: it holds
  duplicate IDs (SIG-002 three times in THR-001) and IDs from `test_prompts.py` whose
  content differs from `signals.json`.
- **Duplicates.** A fixture with duplicate `signal_id`s is refused (`fixture_error`), not
  deduplicated: two records with one ID make every citation of it ambiguous.
- **Thread lock.** Each run is locked to one thread by code. Other IDs return
  `thread_not_allowed`, enforcing "never use signals from another thread" even if the model tries.
- **Unknown thread.** Returned as `found: false` with zero signals, which maps onto the
  contract's existing insufficient_evidence rule (rules 6-8). No new status was invented.
- **Fail closed.** If validation cannot run, the answer is rejected, never released.
- **Fixture timestamps changed since Lab 2** (SIG-003 to SIG-006 now 14:11, 14:18, 14:28,
  14:39). Lab 3 uses the current repository data.

## 4b. Schema transport
Schemas are sent in `parametersJsonSchema` (standard JSON Schema). If the API refuses a keyword
(`pattern`, `minLength`, `additionalProperties`), the client retries once with a sanitized copy and
records a `client_note` in the trace. Arguments are always validated locally against the full schema.

## 5. Validation (three layers)
1. Strict tool schemas: malformed arguments are rejected before any tool runs.
2. validate_summary as a tool: the model can check and fix its own draft mid-loop.
3. Final gate in code: every final answer is validated whether or not the model called the tool.

What code checks: JSON-only output, the full Lab 2 schema (seven fields, no extras, enums,
minItems), rules 1-8, and the deterministic part of rule 10 (a high-confidence claim stating
a clock time that its untimed evidence does not have). Warnings (not errors): untimed signals
missing from unplaced_signals (Item 2 instruction), causal or recommendation wording.
Not checked by code: rule 9 (contradiction is a meaning judgment), the rest of rule 10
(whether a missing field is "relevant"), and whether a claim's text is truly supported by its
citations. A passing validation therefore proves structure, not truth.

## 6. Bounds and error handling
Maximum 10 model calls and 2 correction rounds per run. Transient API errors (429, 500, 503) are
retried at most 3 times (10s, 30s, 60s), recorded as client notes in the trace. Handled: malformed arguments, unknown
tools, tool exceptions, unknown threads, cross-thread requests, malformed fixtures, invalid
final output, API errors. Tools are read-only.

## 7. Limitations
- Built-in + custom tool combination is a Gemini Preview feature (Gemini 3+ models).
- The validator cannot judge meaning; rule 9 relies on the model and later on the team's
  Grounding Validator.
- Data is replayed fixtures, not live tools.
