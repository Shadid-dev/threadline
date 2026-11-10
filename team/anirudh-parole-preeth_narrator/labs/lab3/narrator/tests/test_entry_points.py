import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def run(args, env_extra=None):
    import os
    env = {k: v for k, v in os.environ.items() if k != "GEMINI_API_KEY"}
    env.update(env_extra or {})
    return subprocess.run([sys.executable, "-m", *args], cwd=REPO, env=env,
                          capture_output=True, text=True, timeout=60)


def test_unknown_prompt_id_is_an_error(tmp_path):
    r = run(["narrator.test_prompts_narrator", "P9"], {"GEMINI_API_KEY": "dummy"})
    assert r.returncode != 0 and "Unknown prompt id" in r.stderr


def test_check_setup_diagnoses_network_and_stops():
    from narrator.check_setup import diagnose
    assert diagnose("ConnectError: [Errno -2] Name or service not known").startswith("NETWORK")
    assert diagnose("429 RESOURCE_EXHAUSTED").startswith("QUOTA")
    assert diagnose("404 NOT_FOUND models/x").startswith("MODEL")


def test_trace_text_header_shows_outcome():
    from narrator.narrator_agent import ScriptedClient, run as agent_run
    from narrator.test_prompts_narrator import trace_to_text
    res = agent_run("THR-001", client=ScriptedClient([ConnectionError("down")]), verbose=False)
    text = trace_to_text(res)
    assert "MODE: SIMULATED" in text and "NOT ACCEPTED (api_error)" in text.splitlines()[1]
