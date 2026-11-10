"""Live setup check (run on your laptop):  python -m narrator.check_setup

Makes ONE small real request with both tool types enabled and reports, in plain
words, whether the key, the model and the built-in + custom tool combination
work. Never prints the key. If the configured model fails, tries a few others
and tells you exactly which line to put in .env.
"""
import os
import sys

FALLBACK_MODELS = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.8-flash"]


def diagnose(msg):
    m = msg.lower()
    if any(k in m for k in ("name or service not known", "getaddrinfo", "nodename nor servname",
                            "connecterror", "connection refused", "timed out", "network is unreachable")):
        return "NETWORK: cannot reach generativelanguage.googleapis.com. Check your internet/VPN/firewall."
    if "api key" in m or "api_key_invalid" in m or "permission" in m or "401" in m or "403" in m:
        return "KEY: the API key was rejected. Create a new key at aistudio.google.com/apikey and update .env."
    if "not found" in m or "404" in m:
        return "MODEL: this model name is not available to your key."
    if "429" in m or "resource_exhausted" in m or "quota" in m:
        return "QUOTA: rate limit or free-tier quota reached. Wait a minute and retry."
    if "include_server_side" in m or "combination" in m or ("code_execution" in m and "function" in m):
        return "COMBINATION: this model refused built-in + custom tools together."
    return "OTHER: see the error text."


def probe(model):
    from google.genai import types
    from .narrator_agent import GeminiClient
    c = GeminiClient(model=model,
                     system_instruction="You are testing tools. Follow the user's steps exactly.")
    ev = c.send_text("Step 1: use code execution to print 14*60+3-(14*60+1). "
                     "Step 2: call get_thread_signals with thread_id THR-001.")
    kinds = [e["type"] for e in ev]
    return kinds, c.notes


def main():
    from dotenv import load_dotenv
    load_dotenv()
    import google.genai as g
    print("google-genai version:", g.__version__)
    if int(g.__version__.split(".")[0]) < 2:
        sys.exit("Upgrade the SDK:  pip install -U google-genai")
    if not os.environ.get("GEMINI_API_KEY"):
        sys.exit("No GEMINI_API_KEY found. Put GEMINI_API_KEY=... in the .env file in the repo root.")
    print("API key: found (not shown)")
    from .narrator_agent import DEFAULT_MODEL
    configured = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)
    for model in [configured] + [m for m in FALLBACK_MODELS if m != configured]:
        print(f"\nTesting model {model} ...")
        try:
            kinds, notes = probe(model)
        except Exception as e:
            print("  FAILED:", str(e)[:400])
            print("  ->", diagnose(str(e)))
            if diagnose(str(e)).split(":")[0] in ("KEY", "QUOTA", "NETWORK"):
                sys.exit(1)
            continue
        for n in notes:
            print("  note:", n[:200])
        builtin = any(k in ("code", "code_result") for k in kinds)
        custom = "function_call" in kinds
        print(f"  response parts: {kinds}")
        print(f"  built-in code execution used: {builtin}   custom function call requested: {custom}")
        if custom:
            print(f"\nOK: {model} accepts both tool types in one request.")
            if model != configured:
                print(f"Add this line to .env:  GEMINI_MODEL={model}")
            print("Next:  python -m narrator.test_prompts_narrator")
            return
        print("  The request worked but the model did not call the custom tool; trying next model.")
    sys.exit("No model passed. Copy this whole output and send it back.")


if __name__ == "__main__":
    main()
