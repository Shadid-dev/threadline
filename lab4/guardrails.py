"""Module 6 guardrails for ThreadLine: G2 (injection), G3 (secrets), G7 (cause words).

These are plain Python rules, not a model, so text inside a signal cannot talk them out of their job.
"""
from __future__ import annotations

import copy
import re

# G2: phrases that try to give the system orders from inside a signal.
INJECTION_PATTERNS = [
    r"ignore (all |any )?(previous|prior|above) (instructions|rules)",
    r"disregard (all |any )?(previous|prior|above)",
    r"system (override|prompt)",
    r"you are now",
    r"act as (an? )?(admin|administrator|root)",
    r"(approve|execute|run) (this|the) (action|rollback|command) (now|immediately)",
    r"do not (tell|inform|alert) (the )?(human|user|on-?call)",
]

# G3: secrets that must never reach a model or a log.
SECRET_PATTERNS = [
    r"AKIA[0-9A-Z]{16}",                                  # AWS access key
    r"gh[pousr]_[A-Za-z0-9]{20,}",                        # GitHub token
    r"AIza[0-9A-Za-z_\-]{30,}",                           # Google API key
    r"sk-[A-Za-z0-9]{20,}",                               # generic secret key
    r"(?i)bearer\s+[A-Za-z0-9._\-]{20,}",                 # bearer token
    r"(?i)(password|passwd|pwd|secret|api[_-]?key|token)\s*[:=]\s*\S+",
]

# G7: words that claim a cause. The Narrator may only report what was observed.
CAUSE_WORDS = [r"\bcaused\b", r"\broot cause\b", r"\bbecause of\b", r"\bdue to\b", r"\bresulted in\b"]


def check_injection(text: str) -> list[str]:
    """G2. Returns the suspicious phrases found (empty list means clean)."""
    found = []
    for pattern in INJECTION_PATTERNS:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            found.append(match.group(0))
    return found


def redact_secrets(text: str) -> tuple[str, int]:
    """G3. Returns the text with every secret replaced by [REDACTED], and how many were hidden."""
    count = 0
    for pattern in SECRET_PATTERNS:
        text, n = re.subn(pattern, "[REDACTED]", text)
        count += n
    return text, count


def check_cause_words(text: str) -> list[str]:
    """G7. Returns the cause words found in a Narrator summary (empty list means clean)."""
    return [m.group(0) for p in CAUSE_WORDS for m in re.finditer(p, text, flags=re.IGNORECASE)]


def guard_signal(signal: dict) -> dict:
    """Runs G2 and G3 on a signal that already passed G1 (validate_signal).

    Returns a copy with content redacted and two extra fields the agents can read:
    injection_detected (bool) and redactions (int). The original signal is not changed.
    """
    guarded = copy.deepcopy(signal)
    guarded["content"], guarded_count = redact_secrets(guarded["content"])
    hits = check_injection(guarded["content"])
    guarded["injection_detected"] = bool(hits)
    guarded["redactions"] = guarded_count
    return guarded