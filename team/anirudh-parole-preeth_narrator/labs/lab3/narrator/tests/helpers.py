import copy
import json


def C(text, ids, conf):
    return {"text": text, "signal_ids": ids, "confidence": conf}


THR001_VALID = {
    "thread_id": "THR-001", "status": "ok",
    "headline": C("Checkout errors were first reported two minutes after the v2.4.1 deployment and reached 400 events by 14:39.",
                  ["SIG-001", "SIG-002", "SIG-006"], "medium"),
    "claims": [
        C("At 14:01, version 2.4.1 was deployed to checkout, adding discount code logic.", ["SIG-001"], "high"),
        C("At 14:03, Sentry reported a TypeError in discount.py line 88 (12 events).", ["SIG-002"], "high"),
        C("At 14:11, the checkout error rate was 18 percent.", ["SIG-003"], "high"),
        C("At 14:18, a customer ticket reported being unable to pay for an order.", ["SIG-004"], "high"),
        C("At 14:28, a team member asked in Slack whether checkout was down.", ["SIG-005"], "high"),
        C("At 14:39, Sentry reported the TypeError in discount.py line 88 at 400 events.", ["SIG-006"], "high"),
    ],
    "unplaced_signals": [], "flagged_signals": [],
    "signals_used": ["SIG-001", "SIG-002", "SIG-003", "SIG-004", "SIG-005", "SIG-006"],
}

THR002_VALID = {
    "thread_id": "THR-002", "status": "ok",
    "headline": C("Login response time rose 60 percent at 15:40, followed by TimeoutErrors in auth.py at 15:45.",
                  ["SIG-007", "SIG-008"], "medium"),
    "claims": [
        C("At 15:40, login response time was up 60 percent.", ["SIG-007"], "high"),
        C("At 15:45, Sentry reported a TimeoutError in auth.py line 42 (30 events).", ["SIG-008"], "high"),
    ],
    "unplaced_signals": [], "flagged_signals": [], "signals_used": ["SIG-007", "SIG-008"],
}

EMPTY_VALID = {"thread_id": "THR-099", "status": "insufficient_evidence", "headline": None,
               "claims": [], "unplaced_signals": [], "flagged_signals": [], "signals_used": []}


def mod(base, fn):
    d = copy.deepcopy(base)
    fn(d)
    return json.dumps(d)


def rules(result):
    return {e["rule"] for e in result["errors"]}
