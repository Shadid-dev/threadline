"""Agent-loop tests with a SCRIPTED fake model. These test our loop code,
not Gemini; nothing here is a real model trace."""
import json

from narrator import narrator_agent as ag
from narrator import narrator_tools as nt
from .helpers import THR001_VALID, mod

FC = lambda name, args, i="c1": {"type": "function_call", "id": i, "name": name, "args": args}
TXT = lambda s: [{"type": "text", "text": s}]
GOOD = json.dumps(THR001_VALID)


def run(replies, **kw):
    client = ag.ScriptedClient(replies)
    return ag.run("THR-001", client=client, verbose=False, **kw), client


def kinds(res):
    return [s["type"] for s in res["trace"]["steps"]]


def test_happy_path_with_builtin_events_recorded():
    res, _ = run([
        [FC("get_thread_signals", {"thread_id": "THR-001"})],
        [{"type": "code", "code": "print(14*60+3-(14*60+1))"}, {"type": "code_result", "outcome": "OK", "output": "2"},
         FC("validate_summary", {"thread_id": "THR-001", "summary_json": GOOD}, "c2")],
        TXT(GOOD)])
    assert res["accepted"] and res["output"] == THR001_VALID
    assert res["trace"]["mode"] == "SIMULATED"
    assert "builtin_code_execution" in kinds(res) and kinds(res).count("tool_call") == 2


def test_tool_results_are_sent_back_with_call_id():
    _, client = run([[FC("get_thread_signals", {"thread_id": "THR-001"}, "abc")], TXT(GOOD)])
    sent = client.received[1][1][0]
    assert sent["id"] == "abc" and sent["result"]["signal_count"] == 6


def test_bounded_correction_then_accept():
    bad = mod(THR001_VALID, lambda d: d["signals_used"].pop())
    res, client = run([TXT(bad), TXT(GOOD)])
    assert res["accepted"] and "correction_request" in kinds(res)
    assert "failed contract validation" in client.received[1][1]


def test_rejected_after_retry_limit():
    res, _ = run([TXT("not json")] * 5, max_corrections=2)
    assert not res["accepted"] and res["stop_reason"] == "rejected_after_corrections" and res["output"] is None
    assert kinds(res).count("correction_request") == 2


def test_cross_thread_tool_call_refused():
    res, _ = run([[FC("get_thread_signals", {"thread_id": "THR-002"})], TXT(GOOD)])
    result = [s for s in res["trace"]["steps"] if s["type"] == "tool_result"][0]["result"]
    assert result["error"] == "thread_not_allowed"


def test_malformed_arguments_rejected_before_tool_runs():
    res, _ = run([[FC("get_thread_signals", {"thread_id": "THR-001", "extra": 1})], TXT(GOOD)])
    result = [s for s in res["trace"]["steps"] if s["type"] == "tool_result"][0]["result"]
    assert result["error"] == "invalid_arguments"


def test_unknown_tool():
    res, _ = run([[FC("send_slack_message", {"text": "hi"})], TXT(GOOD)])
    assert [s for s in res["trace"]["steps"] if s["type"] == "tool_result"][0]["result"]["error"] == "unknown_tool"


def test_tool_execution_failure_does_not_crash(monkeypatch):
    def boom(*a, **k): raise RuntimeError("disk on fire")
    monkeypatch.setattr(nt, "get_thread_signals", boom)
    res, _ = run([[FC("get_thread_signals", {"thread_id": "THR-001"})], TXT(GOOD)])
    r = [s for s in res["trace"]["steps"] if s["type"] == "tool_result"][0]["result"]
    assert r["error"] == "tool_execution_failed"
    # the final gate cannot verify the answer either, so it must fail closed
    assert not res["accepted"] and res["output"] is None


def test_api_error_stops_cleanly():
    res, _ = run([ConnectionError("network down")])
    assert res["stop_reason"] == "api_error" and not res["accepted"]


def test_max_model_calls_bound():
    res, _ = run([[FC("get_thread_signals", {"thread_id": "THR-001"})]] * 20, max_model_calls=4)
    assert res["stop_reason"] == "max_model_calls"

def test_external_evidence_is_reused_without_duplicate_retrieval(monkeypatch):
    signals = nt.get_thread_signals("THR-001")["signals"]

    def unexpected_retrieval(*args, **kwargs):
        raise AssertionError("Narrator attempted a second evidence retrieval")

    monkeypatch.setattr(nt, "get_thread_signals", unexpected_retrieval)

    res, _ = run([
        [FC("get_thread_signals", {"thread_id": "THR-001"})],
        [FC("validate_summary", {"thread_id": "THR-001", "summary_json": GOOD})],
        TXT(GOOD),
    ], evidence_signals=signals)

    assert res["accepted"]
    tool_results = [
        step["result"] for step in res["trace"]["steps"]
        if step["type"] == "tool_result"
    ]
    assert tool_results[0]["signals"] == signals
    assert tool_results[0]["signal_count"] == len(signals)
    assert tool_results[1]["valid"] is True
    assert res["trace"]["request"].find("Authoritative evidence supplied") >= 0
