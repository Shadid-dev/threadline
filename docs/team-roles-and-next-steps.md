# Team roles, current status and next steps

*Last updated: 9 November 2026 (week 8 of the 11-week plan in our proposal).*
The task lists below are **suggestions based on the proposal and the design specification**. Agree on them at the next team meeting and edit this file.

---

## 1. Who owns what

| Member | Agent | Work package from the proposal | Your folder |
|---|---|---|---|
| Ahmed Hantoor | Change Attributor | Data and tooling: test data, source adapters, thread store, MCP server | `team/ahmed-hantoor_change-attributor/` |
| Anirudh Parole Preeth | Narrator | Architecture and integration: Supervisor routing, failure handling | `team/anirudh-parole-preeth_narrator/` |
| Afsana Tasnim Nishat | Grounding Validator | Interface and documentation: approval dashboard, documents, demo script | `team/afsana-tasnim-nishat_grounding-validator/` |
| Kameshwar Arora | Action Drafter | Safety and evaluation: guardrails, injection tests, evaluation harness | `team/kameshwar-arora_action-drafter/` |
| Shadid Alam Al Huda | Correlator | Agent development and integration of the prototype | `team/shadid-alam-al-huda_correlator/` |

---

## 2. What is already built

The working prototype is in `lab4/`. It runs offline (no API key) and, optionally, with Gemini or Concordia's Qwen model.

- **Correlator**: groups each signal into a thread (same service, at most 30 minutes after the thread's last activity). Rules only, no AI.
- **Narrator**: picks the important signals and quotes them exactly, with their IDs. Uses AI in live mode.
- **Grounding Validator**: rejects any quote that doesn't exactly match a stored signal. Rules only.
- **Action Drafter**: proposes one next step, which always needs human approval. Uses AI in live mode.
- **Supervisor**: runs the agents in a fixed order (static mode) or decides the next step from the results (dynamic mode).
- **Tests**: 9 scenarios (including a prompt-injection attack) and 18 automatic tests, all passing. There are also 3 runs with the real Gemini model.

The current Narrator, Validator and Drafter are simple versions Shadid wrote to make the whole pipeline run. **Each owner should compare them with their own Lab 2 design** and improve or replace them (see section 4).

---

## 3. Milestones from the proposal: honest status

| ID | Planned week | Goal | Status |
|---|---|---|---|
| M1 | W3 | Signals flow into threads using rules; every model call logged | **Partly done**: rules work on test data. Missing: real source adapters, token/cost logging. |
| M2 | W5 | Correlator, Change Attributor and Narrator as separate agents under a supervisor | **Partly done**: 4 agents + supervisor work. Missing: Change Attributor. |
| M3 | W7 | Threads saved across sessions; summaries within a fixed size; similar past incidents found | **Not started (behind schedule)** |
| M4 | W8 | Ungrounded claims rejected; injection cases tested; no message sent without approval | **Mostly done** in the prototype. Missing: approval screen and audit log. |
| M5 | W9 | Metrics over repeated runs on labelled data | **Not started** |
| M6 | W11 | Live end-to-end demo | **Not started** (plan: CartNow demo shop) |

---

## 4. Next steps

### Everyone: this week, before the design specification is submitted

1. Open `docs/design-spec/` and read the section about **your** agent: 4.2 Correlator, 4.3 Change Attributor, 4.4 Narrator, 4.5 Grounding Validator, 4.6 Action Drafter.
2. Compare it with your own Lab 2 design. Send Shadid any corrections in the group chat. **This is a group submission, so it must match what each of us designed.**
3. Upload your Lab 2, Lab 3 and Lab 4 work to `team/<your-folder>/labs/` (see `docs/how-to-use-github-desktop.md`).

### Ahmed: Change Attributor + data
- Write your agent's input/output contract in the same JSON style as the others (example in design spec Section 4.3).
- Add the third test incident from the Starter Guide (service `search`, around 16:20) to `lab3_correlator/fixtures/signals.json`.
- Grow the labelled test set toward ~80 signals across 8 incidents, with the correct thread written down for each signal.
- Then: the thread store (SQLite) and the source adapters / MCP server.

### Anirudh: Narrator + Supervisor
- Compare your Narrator contract with `lab4/system.py` (class `Narrator`) and list the differences.
- Add the "running summary" that stays within a fixed size (design spec Section 4.4: when a thread has more than 20 signals, keep the latest 10 plus earlier approved observations).
- Then: connect the Change Attributor into the Supervisor once Ahmed's version exists.

### Afsana: Grounding Validator + dashboard
- Compare your Validator contract with `lab4/system.py` (class `GroundingValidator`).
- Build the single-page approval dashboard in Streamlit (wireframe in design spec Section 5.3: thread list, evidence timeline, summary, Approve / Reject / Edit).
- Review this README and the guides in `docs/` for anything unclear.

### Kameshwar: Action Drafter + safety and evaluation
- Compare your Drafter contract with `lab4/system.py` (class `ActionDrafter`).
- Add the two planned draft types: team update and customer update (drafts only, never sent).
- Build the evaluation script: pairwise precision/recall for thread grouping and the window-size test from design spec Section 4.2.
- Plan the live test runs: 6 scenarios × 5 repeats × 2 models = 60 runs (about 110 model calls).
- Finish the CartNow demo plan (the checkout breaks when no discount code is entered).

### Shadid: Correlator + integration
- Write `docs/correctness.md`: when two signals are the same incident, the 30-minute rule and its reason, split vs. merge errors.
- Add the `injection_detected` flag to the Correlator output (design spec Section 4.2).
- Merge each teammate's agent into the prototype as it becomes ready, and keep `main` working.

---

## 5. Where the important things are

| Thing | Location |
|---|---|
| Group design specification | `docs/design-spec/` |
| Project proposal | `docs/proposal/` |
| Starter guide (setup, glossary, first tasks) | `docs/ThreadLine_Team_Starter_Guide.pdf` |
| Current prototype code | `lab4/system.py` (all agents), `lab4/run.py` (runs the scenarios) |
| Test scenarios | `lab4/test_prompts.json` |
| Run records (traces) | `lab4/traces/` |
| Test data (signals) | `lab3_correlator/fixtures/signals.json` |
