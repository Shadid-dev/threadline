# INSE 691 — Lab 4: Multi-Agent Systems Orchestration
## Revision 2 — ThreadLine

**Author:** Anirudh Parole Preeth
**Concordia Student ID:** 40351389
**Course:** INSE 691 — Foundations of AI Agent Systems

## 1. Purpose of Revision 2

Revision 2 strengthens the original Lab 4 multi-agent prototype in response
to peer feedback. The original implementation demonstrated agent separation
and sequential orchestration, but had limitations in reproducibility,
evidence handling, response validation, and test reporting.

This revision addresses those limitations while preserving the original
submission and keeping the revised implementation isolated from the shared
team-level prototype.

## 2. Improvements implemented

### 2.1 Standalone reproducibility

The Revision 2 directory contains the Lab 3 Narrator implementation,
its fixtures, tests, and dependencies, together with the Lab 4 agents.

A standalone requirements.txt and README.md document installation,
configuration, and test execution. The complete test suite can be run
from the Revision 2 directory without a manually configured PYTHONPATH.

### 2.2 Detailed test evidence

The revision includes:
- test_run.log — complete verbose pytest output.
- test-results.xml — machine-readable JUnit test report.

The combined Narrator and Lab 4 test suite passes all 68 tests.

### 2.3 Stricter response and evidence validation

The Evidence Agent now validates:
- Thread identifier format.
- Retrieval response structure and thread identity.
- Boolean type and consistency of the found flag.
- Signal list structure and signal count.
- Exact required signal fields.
- Signal identifier type, uniqueness, and non-empty values.
- Signal field types and thread ownership.
- Timestamp format.

The Narrator Validator also supports externally supplied evidence and
checks for malformed records, duplicate identifiers, and cross-thread
records before validating the generated summary.

Invalid evidence is rejected rather than passed to analysis.

### 2.4 Single evidence retrieval and handoff

The original implementation allowed the Evidence Agent and Narrator
to retrieve the same thread's signals independently.

Revision 2 changes this workflow:

1. Evidence Agent retrieves the thread signals.
2. Evidence Agent validates the retrieved response.
3. Orchestrator passes the validated signal list to Analysis Agent.
4. Analysis Agent passes the same evidence records to the Narrator.
5. Narrator reuses those records for its evidence tool and final validation.

This avoids duplicate retrieval during the workflow and ensures that
analysis and validation use the same evidence records.

Signal content is treated as untrusted data, not as instructions.

## 3. Revised architecture

The system retains a sequential, centrally controlled architecture.

- Evidence Agent: retrieves and validates evidence.
- Orchestrator: controls execution and passes the evidence between agents.
- Analysis Agent: adapts the existing Narrator for the Lab 4 workflow.
- Narrator: generates the structured incident summary.
- Validator: checks the summary against the existing contract using
  the supplied evidence.

The revision improves evidence consistency without replacing the
original Lab 3 summarization contract.

## 4. Testing and results

The combined automated suite includes the original Narrator regression
tests and the Lab 4 orchestration tests, together with new tests for
evidence injection, validation, and evidence handoff.

**Latest recorded result: 68 passed.**

The test suite was also executed from the Revision 2 directory with
PYTHONPATH unset, confirming that the documented local test command
works with the standalone package layout.

Test command:

    python -m pytest narrator/tests lab4/test_lab4.py -v

Detailed results are included in `lab4/results/test_run.log` and
`lab4/results/test-results.xml`.

## 5. Limitations

The system remains a sequential, centrally orchestrated multi-agent
prototype. It does not implement distributed peer-to-peer agent
coordination or autonomous negotiation.

Live model execution requires a configured Gemini API key.
The automated regression suite runs offline and does not require
that key.

## 6. Revision 2 package contents

- narrator/ — included Lab 3 Narrator implementation and tests.
- lab4/evidence_agent.py — strict evidence retrieval and validation.
- lab4/analysis_agent.py — Narrator integration with supplied evidence.
- lab4/orchestrator.py — sequential workflow coordination.
- lab4/test_lab4.py — Lab 4 regression and validation tests.
- fixtures/signals.json — signal fixture data.
- requirements.txt — standalone dependencies.
- README.md — setup and execution instructions.
- lab4/results/ — demonstration outputs and test reports.

## 7. Conclusion

Revision 2 addresses all four identified improvement areas:
standalone reproducibility, detailed test evidence, stricter validation,
and single-retrieval evidence sharing.

The original Lab 4 submission remains preserved separately.
