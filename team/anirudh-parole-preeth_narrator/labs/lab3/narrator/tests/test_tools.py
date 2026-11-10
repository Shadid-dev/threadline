import hashlib
import json

from narrator import narrator_tools as nt


def test_real_fixtures_group_into_two_threads():
    t1 = nt.get_thread_signals("THR-001")
    t2 = nt.get_thread_signals("THR-002")
    assert [s["signal_id"] for s in t1["signals"]] == [f"SIG-00{i}" for i in range(1, 7)]
    assert [s["signal_id"] for s in t2["signals"]] == ["SIG-007", "SIG-008"]
    assert all(s["thread_id"] == "THR-001" for s in t1["signals"])


def test_unknown_thread_returns_zero_signals_not_error():
    r = nt.get_thread_signals("THR-099")
    assert r["found"] is False and r["signals"] == [] and "error" not in r


def test_invalid_thread_id_format():
    assert nt.get_thread_signals("thread one")["error"] == "invalid_thread_id"


def test_thread_lock_refuses_other_thread():
    r = nt.get_thread_signals("THR-002", allowed_thread_id="THR-001")
    assert r["error"] == "thread_not_allowed" and "signals" not in r


def test_duplicate_signal_ids_are_refused_not_deduplicated(tmp_path):
    sigs = json.loads(nt.DEFAULT_FIXTURES.read_text())
    sigs.append(dict(sigs[0]))
    p = tmp_path / "dupe.json"; p.write_text(json.dumps(sigs))
    r = nt.get_thread_signals("THR-001", fixtures_path=p)
    assert r["error"] == "fixture_error" and "SIG-001" in r["message"]


def test_malformed_fixture_json(tmp_path):
    p = tmp_path / "bad.json"; p.write_text("[{not json")
    assert nt.get_thread_signals("THR-001", fixtures_path=p)["error"] == "fixture_error"


def test_malformed_timestamp(tmp_path):
    sigs = json.loads(nt.DEFAULT_FIXTURES.read_text()); sigs[0]["timestamp"] = "2pm"
    p = tmp_path / "ts.json"; p.write_text(json.dumps(sigs))
    assert "malformed timestamp" in nt.get_thread_signals("THR-001", fixtures_path=p)["message"]


def test_missing_fixture_file(tmp_path):
    assert nt.get_thread_signals("THR-001", fixtures_path=tmp_path / "nope.json")["error"] == "fixture_error"


def test_tools_are_read_only():
    before = hashlib.sha256(nt.DEFAULT_FIXTURES.read_bytes()).hexdigest()
    nt.get_thread_signals("THR-001")
    nt.validate_summary("THR-001", "{}")
    assert hashlib.sha256(nt.DEFAULT_FIXTURES.read_bytes()).hexdigest() == before
