"""Offline tests of how real Gemini response parts are converted (no API call)."""
from google.genai import types

from narrator.narrator_agent import parse_parts, sanitize_for_api, GeminiClient
from narrator.tool_schemas import GET_THREAD_SIGNALS


def test_function_call_and_code_execution_parts():
    parts = [
        types.Part(executable_code=types.ExecutableCode(code="print(2)", language="PYTHON")),
        types.Part(code_execution_result=types.CodeExecutionResult(outcome="OUTCOME_OK", output="2\n")),
        types.Part(function_call=types.FunctionCall(id="x1", name="get_thread_signals", args={"thread_id": "THR-001"})),
        types.Part(text="done"),
    ]
    ev = parse_parts(parts)
    assert [e["type"] for e in ev] == ["code", "code_result", "function_call", "text"]
    assert ev[2] == {"type": "function_call", "id": "x1", "name": "get_thread_signals", "args": {"thread_id": "THR-001"}}


def test_server_side_tool_parts_are_recognised_as_builtin():
    # Code execution normally returns executable_code parts; this covers the
    # generic server-side tool_call/tool_response form as a fallback.
    parts = [types.Part(tool_call=types.ToolCall(id="t", tool_type=types.ToolType.TOOL_TYPE_UNSPECIFIED, args={"code": "print(1)"})),
             types.Part(tool_response=types.ToolResponse(id="t", tool_type=types.ToolType.TOOL_TYPE_UNSPECIFIED, response={"outcome": "OUTCOME_OK", "output": "1"}))]
    assert [e["type"] for e in parse_parts(parts)] == ["code", "code_result"]


def test_thought_parts_are_skipped():
    assert parse_parts([types.Part(text="secret plan", thought=True)]) == []


def test_sanitized_schema_drops_only_risky_keywords():
    s = sanitize_for_api(GET_THREAD_SIGNALS["parameters"])
    assert "additionalProperties" not in s and "pattern" not in s["properties"]["thread_id"]
    assert s["required"] == ["thread_id"]


def test_config_contains_both_custom_and_builtin_tools(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-not-used")
    c = GeminiClient()
    names = [f.name for f in c.config.tools[0].function_declarations]
    assert names == ["get_thread_signals", "validate_summary"]
    assert c.config.tools[1].code_execution is not None
    assert c.config.tool_config.include_server_side_tool_invocations is True
    assert c.config.automatic_function_calling.disable is True


def test_transient_errors_are_retried_then_succeed(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-not-used")
    c = GeminiClient()
    monkeypatch.setattr("narrator.narrator_agent.time.sleep", lambda s: None)
    calls = {"n": 0}
    ok = types.GenerateContentResponse(candidates=[types.Candidate(
        content=types.Content(role="model", parts=[types.Part(text="{}")]))])
    def fake(**kw):
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("429 RESOURCE_EXHAUSTED quota")
        return ok
    monkeypatch.setattr(c.client.models, "generate_content", fake)
    assert c.send_text("hi") == [{"type": "text", "text": "{}"}]
    assert calls["n"] == 3 and len(c.notes) == 2


def test_non_transient_errors_are_not_retried(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-not-used")
    c = GeminiClient()
    calls = {"n": 0}
    def fake(**kw):
        calls["n"] += 1
        raise RuntimeError("404 model not found")
    monkeypatch.setattr(c.client.models, "generate_content", fake)
    import pytest
    with pytest.raises(RuntimeError):
        c.send_text("hi")
    assert calls["n"] == 1


def test_schema_rejection_falls_back_to_sanitized_once(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-not-used")
    c = GeminiClient()
    seen = []
    ok = types.GenerateContentResponse(candidates=[types.Candidate(
        content=types.Content(role="model", parts=[types.Part(text="ok")]))])
    def fake(**kw):
        decl = kw["config"].tools[0].function_declarations[0].parameters_json_schema
        seen.append("pattern" in decl["properties"]["thread_id"])
        if seen[-1]:
            raise RuntimeError("400 INVALID_ARGUMENT Unknown name pattern in parameters")
        return ok
    monkeypatch.setattr(c.client.models, "generate_content", fake)
    assert c.send_text("hi")[0]["text"] == "ok"
    assert seen == [True, False] and c.schema_mode == "sanitized"
