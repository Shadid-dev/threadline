import json
from pathlib import Path

from narrator import narrator_tools as nt
from narrator.make_prompt_fixtures import build
from .helpers import THR001_VALID, THR002_VALID, EMPTY_VALID, C, mod, rules

PF = Path(nt.__file__).parent / "prompt_fixtures"
build()


def v(tid, s, **kw):
    return nt.validate_summary(tid, s if isinstance(s, str) else json.dumps(s), **kw)


def test_valid_outputs_pass():
    assert v("THR-001", THR001_VALID)["valid"]
    assert v("THR-002", THR002_VALID)["valid"]
    assert v("THR-099", EMPTY_VALID)["valid"]


def test_semantic_rules_are_reported_not_checked():
    r = v("THR-001", THR001_VALID)
    assert {n["rule"] for n in r["not_checked"]} >= {9, 10, "support"}


def test_malformed_json():
    assert rules(v("THR-001", "{oops")) == {"json"}


def test_code_fences_are_rejected_with_hint():
    r = v("THR-001", "```json\\n" + json.dumps(THR001_VALID) + "\\n```")
    assert not r["valid"] and "code fences" in r["errors"][0]["message"]


def test_missing_required_field():
    assert rules(v("THR-001", mod(THR001_VALID, lambda d: d.pop("signals_used")))) == {"schema"}


def test_extra_field_rejected():
    assert rules(v("THR-001", mod(THR001_VALID, lambda d: d.update(root_cause="deploy")))) == {"schema"}


def test_invalid_status_value():
    assert rules(v("THR-001", mod(THR001_VALID, lambda d: d.update(status="resolved")))) == {"schema"}


def test_invalid_confidence_value():
    assert rules(v("THR-001", mod(THR001_VALID, lambda d: d["claims"][0].update(confidence="90%")))) == {"schema"}


def test_uncited_claim_rejected():
    assert rules(v("THR-001", mod(THR001_VALID, lambda d: d["claims"][0].update(signal_ids=[])))) == {"schema"}


def test_rule1_wrong_thread_id():
    assert 1 in rules(v("THR-001", mod(THR001_VALID, lambda d: d.update(thread_id="THR-002"))))


def test_rule2_citation_from_another_thread():
    def f(d):
        d["claims"].append(C("Login was slow.", ["SIG-007"], "high")); d["signals_used"].append("SIG-007")
    assert 2 in rules(v("THR-001", mod(THR001_VALID, f)))


def test_rule3_signals_used_mismatch():
    assert rules(v("THR-001", mod(THR001_VALID, lambda d: d["signals_used"].remove("SIG-004")))) == {3}
    assert rules(v("THR-002", mod(THR002_VALID, lambda d: d["signals_used"].append("SIG-001")))) >= {2, 3}


def test_rule4_order():
    assert rules(v("THR-001", mod(THR001_VALID, lambda d: d["claims"].reverse()))) == {4}


def test_rule5_unplaced_signal_has_timestamp():
    assert 5 in rules(v("THR-001", mod(THR001_VALID, lambda d: d["unplaced_signals"].append("SIG-001"))))


def test_rules_6_7_8_status_vs_signal_count():
    assert 6 in rules(v("THR-001", mod(THR001_VALID, lambda d: d.update(status="insufficient_evidence"))))
    assert 7 in rules(v("THR-001", mod(THR001_VALID, lambda d: d.update(status="limited_evidence"))))
    assert 8 in rules(v("THR-099", mod(EMPTY_VALID, lambda d: d.update(status="ok"))))
    assert 8 in rules(v("THR-001", mod(THR001_VALID, lambda d: d.update(headline=None))))


def test_p3_missing_timestamp_valid_and_rule10():
    fx = PF / "p3_missing_timestamp.json"
    def good(d):
        c = d["claims"].pop(3); c["text"] = "A customer ticket reported being unable to pay for an order."
        d["claims"].append(c); d["unplaced_signals"] = ["SIG-004"]
    assert v("THR-001", mod(THR001_VALID, good), fixtures_path=fx)["valid"]
    def invented_time(d):
        c = d["claims"].pop(3); d["claims"].append(c); d["unplaced_signals"] = ["SIG-004"]  # still says 14:18
    assert 10 in rules(v("THR-001", mod(THR001_VALID, invented_time), fixtures_path=fx))
    def not_last(d):
        d["claims"][3]["text"] = "A customer ticket reported being unable to pay."; d["unplaced_signals"] = ["SIG-004"]
    assert 4 in rules(v("THR-001", mod(THR001_VALID, not_last), fixtures_path=fx))
    r = v("THR-001", THR001_VALID, fixtures_path=fx)   # forgot unplaced_signals
    assert any("SIG-004" in w["message"] for w in r["warnings"])


def test_p4_injection_flag_cannot_be_cited():
    fx = PF / "p4_injection.json"

    ok = mod(
        THR002_VALID,
        lambda d: d["flagged_signals"].append({
            "signal_id": "SIG-009",
            "reason": "embedded_instruction",
        }),
    )
    assert v("THR-002", ok, fixtures_path=fx)["valid"]

    def cite_flagged_signal(d):
        d["claims"].append(
            C("A Slack message contained an embedded instruction.",
              ["SIG-009"], "low")
        )
        d["signals_used"].append("SIG-009")

    bad = mod(json.loads(ok), cite_flagged_signal)
    assert rules(v("THR-002", bad, fixtures_path=fx)) == {"safety"}


def test_causation_and_recommendation_are_warned():
    def f(d): d["claims"][1]["text"] = "The deployment caused a TypeError; we should roll back."
    r = v("THR-001", mod(THR001_VALID, f))
    assert r["valid"] and len([w for w in r["warnings"] if w["rule"] == "instruction"]) == 2


def test_validator_scope_lock():
    assert not v("THR-002", THR002_VALID, allowed_thread_id="THR-001")["valid"]

def test_supplied_evidence_is_used_without_retrieval(monkeypatch):
    signals = nt.get_thread_signals("THR-001")["signals"]

    def unexpected_retrieval(*args, **kwargs):
        raise AssertionError("Validator performed a duplicate evidence retrieval")

    monkeypatch.setattr(nt, "get_thread_signals", unexpected_retrieval)
    result = v("THR-001", THR001_VALID, signals=signals)

    assert result["valid"]


def test_supplied_evidence_rejects_cross_thread_records():
    signals = nt.get_thread_signals("THR-001")["signals"]
    signals[0]["thread_id"] = "THR-002"

    result = v("THR-001", THR001_VALID, signals=signals)

    assert not result["valid"]
    assert any("does not belong" in e["message"] for e in result["errors"])


def test_supplied_evidence_rejects_duplicate_signal_ids():
    signals = nt.get_thread_signals("THR-001")["signals"]
    signals.append(dict(signals[0]))

    result = v("THR-001", THR001_VALID, signals=signals)

    assert not result["valid"]
    assert any("duplicate signal_id" in e["message"] for e in result["errors"])


def test_supplied_evidence_rejects_malformed_records():
    result = v("THR-001", THR001_VALID, signals=["not a signal record"])

    assert not result["valid"]
    assert any("not an object" in e["message"] for e in result["errors"])
