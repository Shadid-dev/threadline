# ThreadLine - Lab 4: Multi-agent coordination and orchestration

Name: Shadid Alam Al Huda
Student ID: 40334643
Course: INSE 691 - Foundations of AI Agent Systems
Submission date: 27 October 2026

## 1. Summary of system functionality

ThreadLine is an incident assistant for situations where operational evidence is scattered across monitoring alerts, error reports, deployment events, and team messages. A checkout failure, for example, may appear as an error-rate alert, a stack trace, and a customer complaint. Responders need a shared record of the observations before deciding what to investigate. This prototype uses synthetic signals representing such sources; it does not connect to production accounts or take corrective action.

Lab 3 implemented a single Correlator that attached a signal to an incident thread or opened a new thread. This lab retains that responsibility and adds three cooperating agents. A Narrator selects observations from the thread with signal citations. A Grounding Validator independently checks those observations against stored evidence. An Action Drafter proposes a limited next step for human approval. A central manager controls information exchange, schedules agents, handles rejected outputs, and produces a result with a full execution trace.

The prototype supports two coordination modes. Static mode follows a predefined sequence. Dynamic mode changes its route using runtime results: duplicate signals skip repeated work, missing service data triggers human review, and a rejected narration gets one revision before escalation. The offline implementation uses explicit rule-based decisions and can be reproduced without API credentials. Optional Gemini or Concordia Qwen execution gives the Narrator and Action Drafter separate model calls and instructions while retaining deterministic correlation and validation. The result is a bounded, testable starting point for the group project, with a clear distinction between observed evidence, proposed actions, and human decisions.

## 2. System structure and agent decomposition

The system uses functional decomposition rather than agents representing physical entities. Agents cooperate toward the same objective: prepare an incident record supported by available observations. Responsibilities are separated because correlation, evidence selection, independent checking, and action proposal require different decision rules and permissions. Independent checking prevents an agent from approving its own prose merely because it sounds plausible.

The architecture is centralized and hierarchical. A code manager owns scheduling, but it is not counted as an additional LLM agent. The four agents exchange explicit JSON messages through that manager and a shared thread snapshot. Correlator can write incident state through guarded tools; the other agents receive copies and cannot modify it. Private model conversation state is not shared.

### Correlator

Function: attach a signal or create a thread. Static attributes: role name, same-service constraint, 30-minute inclusive window, latest-activity tie break, and guarded store tools. Dynamic attributes: call count, latest decision, selected thread ID, and review flag. Behavior: validate the signal, check replay, retrieve candidates, and commit exactly one mutation or an idempotent replay. Missing service remains null and starts a review thread. Signal content cannot control routing because the deterministic policy does not interpret its instructions.

### Narrator

Function: select incident observations with evidence references. Static attributes: role instructions, read-only access, summary schema, and prohibition on unsupported causal claims. Dynamic attributes: call count, selected quotations, latest proposal, and revision feedback supplied by the manager. Offline behavior quotes all available observations. Live model behavior selects observations through a separate JSON-output request. Gemini uses a response schema; Concordia receives the schema in its instructions and is checked locally. It must preserve each quoted content field exactly; it does not write a free-form root-cause conclusion.

### Grounding Validator

Function: accept or reject Narrator output. Static attributes: exact-quote policy, allowed output fields, requirement for nonempty evidence, and citation uniqueness. Dynamic attributes: call count, latest verdict, and rejection messages. Behavior: compare every quote and citation with the stored snapshot, reject altered quotations or unknown IDs, and return structured feedback. This validates attribution, not whether a source observation is true, relevant, complete, or causally explanatory.

### Action Drafter

Function: propose a next step. Static attributes: read-only access; only `inspect_evidence` and `request_service` are allowed; all proposals require human approval. Dynamic attributes: call count, proposed kind, cited IDs, and latest output. Behavior: recommend service identification for null service or evidence inspection otherwise. The application validates action kind, citations, and approval flag independently. No remediation executor, outbound message sender, or approval interface is implemented.

This is an individual integration prototype. The additional roles are deliberately narrow so teammates can later replace them with their own implementations without treating this lab as their submitted work.

## 3. Agent decision-making schemes

### Correlation decisions

Input is a strict signal object with `signal_id`, `source`, nullable `service`, full dated `timestamp` with numeric UTC offset, and `content`. First check whether the ID already exists. An identical replay is a no-op; a conflicting reuse raises an error before mutation. Candidates must be open, have the same non-null service, and satisfy `0 <= incoming_time - last_activity <= 30 minutes`. Select the most recent eligible thread, breaking exact ties by thread ID; otherwise create a new thread. Guarded writes recheck eligibility independently of agent proposals.

The dated format fixes the earlier HH:MM-only arithmetic limitation. This prototype deliberately does not backdate existing threads: out-of-order arrivals start separate records. That prevents activity regression but can split one incident, so it is an explicit policy tradeoff rather than a claim of optimal correlation. Thirty minutes remains a starting parameter requiring labelled evaluation.

### Narration, validation, and action decisions

Narrator receives thread evidence and optional rejection feedback. It returns an `observations` array, each item containing only `signal_id` and an exact `quote`. Validator rejects wrong keys, empty observations, unknown citations, changed quotations, or repeated citations. An approved proposal can proceed to action drafting. Action Drafter returns a schema-constrained action kind, evidence citations, and `requires_human_approval: true`. Its output is independently checked before inclusion in the final result.

The offline agents use rule-based local reasoning. In optional live mode, Narrator and Action Drafter use Gemini or Concordia Qwen with separate role instructions and JSON output contracts; the system does not claim every agent is an LLM. There is no silent model-to-rules fallback. A model exception is traced by error type and produces human review. Correlation state already committed before such an exception is retained, while unvalidated prose is withheld.

## 4. Coordination and orchestration: static and dynamic

Coordination is cooperative and rule-governed, with a central manager as communication hub. There is no auction, negotiation, adversarial debate, or decentralized resource allocation because these agents have complementary functions and no conflicting incentives. The environment is an artificial incident store with synthetic observations.

### Static sequence

The predefined path is Correlator -> Narrator -> Grounding Validator -> Action Drafter. Narrator runs once; a rejected summary stops the path for safety and requests human review. Static mode does not adaptively retry. For a missing service, it still runs the Drafter, which proposes `request_service`. For an identical replay, it still runs the presentation stages, although the store remains unchanged.

### Dynamic routing

The manager decides the next role from runtime outputs. An identical replay skips the remaining agents. For ordinary signals it dispatches Narrator and Validator. If Validator rejects the proposal, it sends error messages back to Narrator for one revision; if the second proposal fails, it escalates. After an approved summary, missing service causes the manager to skip action drafting and require human identification. Otherwise Action Drafter runs. API errors and invalid actions also result in review.

Dynamic scheduling here is code-directed, using runtime information; it is not LLM-directed planning. Maximum work per dynamic input is one correlation invocation, two Narrator invocations, two Validator invocations, and one Action Drafter invocation. This bounds feedback loops and model costs. Live requests have a 60-second timeout and SDK attempts are explicitly limited to one. There is no automatic provider-error retry; the one revision concerns rejected content, not transport failures.

### Shared state and messages

Agents receive evidence copies, proposal objects, verdicts, or revision feedback. Each agent retains its own call count and latest output. Trace events record sequence number, sender, event type, and payload, including tool arguments/results, proposals, validation verdicts, routing decisions, errors, and final result. Every scenario begins with its own store, so its expected behavior does not depend on earlier tests. Trace files include the initial seed and final store for reproducibility. The incident store is in memory for this lab; saving a trace is not a database or a production persistence layer.

## 5. Test prompts and validation

The complete machine-readable prompts, input signals, seeds, and expected correlation decisions are in `test_prompts.json`. All timestamps refer to the same synthetic date with explicit offsets. Nine prompts cover the required minimum of five scenarios.

1. New incident: process a checkout alert at 14:01 with no open threads. Expected: create a thread, publish validated observations, and propose evidence inspection for approval.
2. Attach: process a checkout error at 14:03 after a checkout alert at 14:01. Expected: attach to THR-001 and cite its evidence.
3. Different service: process a login slowdown while a checkout thread is open. Expected: create a separate login record.
4. Missing service: process an alert with null service. Expected: preserve null, request review; dynamic mode skips action drafting while static mode drafts a service-identification request.
5. Prompt injection: process checkout content saying to attach to login THR-002. Expected: correlate to checkout THR-001; hostile content remains a quoted observation, not an instruction.
6. Duplicate: replay the identical signal. Expected: no state change; dynamic mode skips specialist work.
7. Out-of-order arrival: submit a 14:01 checkout signal after a 14:10 record. Expected: create a separate thread under the explicit no-backdating policy.
8. Repair: inject one unsupported Narrator quotation. Expected: static mode requests review; dynamic mode rejects it, returns feedback, and succeeds on one repaired proposal.
9. Repeated failure: inject unsupported Narrator quotations on every attempt. Expected: dynamic mode stops after two attempts and escalates without publishing the rejected summary or an action.

Fault injection in prompts 8 and 9 is deliberately generated by a test backend and labelled in traces. Those outputs are not claimed as real Gemini hallucinations. Real offline executions in `traces/static.json` and `traces/dynamic.json` cover all nine prompts in each mode. Regression tests additionally check window boundaries, midnight and UTC offsets, malformed input, closed threads, independent write guards, fabricated citations, provider errors, and attempted bypass of human approval.

## 6. Working prototype, execution evidence, and limitations

Run `python3 -m lab4.run --mode dynamic` from the repository root. Run the static comparison with `--mode static`, and the regression suite with `python3 -m unittest lab4.test_system lab4.test_concordia -v`. Standard-library Python is sufficient for offline runs. Optional model dependencies and Gemini/Concordia configuration are documented in `README.md`. The Lab 3 entry points and original fixtures are preserved; the Lab 4 module owns isolated state and uses narrower interfaces suitable for cooperation.

The prototype is agent-based through distinct roles, local state, decision policies, and structured interaction. Its dynamic behavior is bounded adaptation inside a designed workflow. It does not autonomously discover new roles or negotiate objectives. Exact quotation validation reduces fabricated observations, but it cannot establish truth, detect every malicious meaning, or guarantee complete evidence selection. A malicious string can still be displayed as a quote. Evidence inspection is a proposed action only, and human approval is represented as a required output flag rather than an implemented UI.

The store is not concurrent or durable. There are no authenticated source connectors, incident cause attribution, customer-message delivery, or production approvals. Optional live model execution depends on provider availability, supported model names, and quota. Offline traces and fault-injection traces remain distinct from live execution evidence.

### Concordia local model option

The supplied course guide describes Qwen3-8B behind the ENCS LiteLLM service. The new `concordia` backend calls its chat-completions endpoint at `http://localhost:4000/v1` after the user establishes an SSH tunnel through `login.encs.concordia.ca` to `aise-01.encs.concordia.ca:4000`. The default campus model is `qwen3-8b`. A personal campus key belongs in a private `.env` as `CONCORDIA_API_KEY`; it is separate from the Gemini key.

This integration calls the endpoint directly from Python. Continue is optional for interactive VS Code chat and is not a dependency of the prototype. The guide does not promise server-side JSON Schema support, so the adapter requests JSON in its instructions, parses the response, and uses the same independent grounding and action checks. Missing tunnel, invalid output, and request failure lead to review rather than silent substitution. The campus adapter was tested with mocked HTTP responses; no live campus run is claimed because a configured campus tunnel and personal campus key were not available during this revision. Existing live evidence remains Gemini evidence.

### Captured execution results

Eighteen regression tests passed: thirteen system checks and five mocked campus-adapter checks. Both modes completed all nine isolated offline scenarios. Dynamic mode repaired the injected one-time narration error, while static mode requested review. Both modes escalated repeated invalid narration. The action list executed by the application remained empty in every scenario.

Three genuine live scenarios were then executed using `gemini-3.5-flash-lite`, with a separate Narrator call and, where permitted, an Action Drafter call. The attach and prompt-injection scenarios reached `awaiting_approval` with validated observations and action proposals. The missing-service scenario reached `needs_human_review`, with an approved summary and no Action Drafter invocation, as designed. These are actual model responses in `traces/gemini_live.json`, not offline substitutions. This limited sample does not establish general injection resistance or provider reliability.

An earlier smoke test using the `gemini-flash-latest` alias encountered provider `ServerError` responses. Those failed attempts are retained in `traces/gemini_server_errors.json`; no failure was counted as a successful completion. The initial failure traces predate the explicit timeout and one-attempt configuration. The default CLI alias can be overridden; the successful run explicitly selected `--model gemini-3.5-flash-lite`.

### References

- Course Module 4, Multi-Agent Coordination and Orchestration: functional decomposition; cooperative coordination; hierarchical architecture; local decision schemes; static, dynamic, and code-directed scheduling.
- Lab 3 ThreadLine prototype and captured traces: starting Correlator design and known duplicate/timestamp limitations.
- Google Gen AI SDK, structured output configuration: https://googleapis.github.io/python-genai/ . Used for the optional Gemini backend, not required for offline execution.

- Concordia AI Lab, How to Use the Concordia Local LLM in VS Code: campus model, SSH tunnel, LiteLLM endpoint, and personal-key setup supplied with this task.
