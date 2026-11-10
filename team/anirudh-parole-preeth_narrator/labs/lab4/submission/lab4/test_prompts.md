# Lab 4 — Multi-Agent System Test Prompts

## Test 1: Valid checkout incident
Prompt: Analyze incident thread THR-001 and produce an evidence-grounded summary.
Expected: EvidenceAgent retrieves the signals, the Orchestrator invokes AnalysisAgent, and a validated summary is returned.
Observed: Live end-to-end run completed; six signals retrieved; summary accepted.

## Test 2: Unknown thread
Prompt: Analyze thread THR-999.
Expected: EvidenceAgent reports no signals; the Orchestrator returns insufficient_evidence without invoking AnalysisAgent.
Observed: Covered by automated orchestration tests.

## Test 3: Invalid thread identifier
Prompt: Analyze thread INVALID.
Expected: EvidenceAgent rejects the invalid identifier and the Orchestrator stops safely.
Observed: Covered by automated orchestration tests.

## Test 4: Analysis failure
Prompt: Analyze THR-001 when the AnalysisAgent fails.
Expected: The Orchestrator reports analysis_failed and preserves the evidence result rather than reporting success.
Observed: Covered by a controlled automated test using a simulated Analysis Agent failure.

## Test 5: Valid login incident
Prompt: Analyze incident thread THR-002 (login) and produce an evidence-grounded summary.
Expected: EvidenceAgent retrieves only that thread's signals and AnalysisAgent attempts to produce a validated summary.
Observed: Live end-to-end run completed; two signals retrieved; summary accepted.
