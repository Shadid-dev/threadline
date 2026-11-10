"""Analysis Agent for ThreadLine Lab 4.

Reuses the Lab 3 Narrator to create a validated incident summary.
"""

from dotenv import load_dotenv

from narrator import narrator_agent


def run(thread_id: str, evidence_signals: list) -> dict:
    """Analyze one thread using the exact evidence retrieved by the Evidence Agent."""
    try:
        # Load the existing .env without printing or exposing secrets.
        load_dotenv()

        client = narrator_agent.GeminiClient()
        result = narrator_agent.run(
            thread_id,
            client=client,
            prompt_id="lab4_analysis",
            verbose=False,
            evidence_signals=evidence_signals,
        )

        return {
            "agent": "AnalysisAgent",
            "ok": bool(result.get("accepted")),
            "thread_id": thread_id,
            "decision": (
                "summary_accepted"
                if result.get("accepted")
                else "analysis_failed"
            ),
            "output": result.get("output"),
            "stop_reason": result.get("stop_reason"),
            "validation": result.get("validation"),
            "trace": result.get("trace"),
        }

    except Exception as exc:
        return {
            "agent": "AnalysisAgent",
            "ok": False,
            "thread_id": thread_id,
            "decision": "stop",
            "error": f"{type(exc).__name__}: {exc}",
        }
