"""Narrator contract, copied from Lab 2 (INSE_691_Lab_2_Anirudh_Preeth.docx).

Item 4a (output JSON Schema) is reproduced exactly. Item 2 (developer
instruction) is the base of SYSTEM_INSTRUCTION in narrator_agent.py.
"""

SIGNAL_FIELDS = ["signal_id", "source", "service", "timestamp", "content", "thread_id"]

# Item 4a: exact copy of the Lab 2 output schema.
OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["thread_id", "status", "headline", "claims",
                 "unplaced_signals", "flagged_signals", "signals_used"],
    "$defs": {
        "claim": {
            "type": "object",
            "additionalProperties": False,
            "required": ["text", "signal_ids", "confidence"],
            "properties": {
                "text": {"type": "string", "minLength": 1},
                "signal_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                "confidence": {"enum": ["low", "medium", "high"]},
            },
        }
    },
    "properties": {
        "thread_id": {"type": "string"},
        "status": {"enum": ["ok", "limited_evidence", "insufficient_evidence"]},
        "headline": {"anyOf": [{"$ref": "#/$defs/claim"}, {"type": "null"}]},
        "claims": {"type": "array", "items": {"$ref": "#/$defs/claim"}},
        "unplaced_signals": {"type": "array", "items": {"type": "string"}},
        "flagged_signals": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["signal_id", "reason"],
                "properties": {
                    "signal_id": {"type": "string"},
                    "reason": {"enum": ["embedded_instruction"]},
                },
            },
        },
        "signals_used": {"type": "array", "items": {"type": "string"}},
    },
}

# Item 4b: the ten validity rules, numbered as in the contract.
VALIDITY_RULES = {
    1: "thread_id equals the input thread's thread_id.",
    2: "Every ID in any signal_ids, unplaced_signals, flagged_signals or signals_used exists in the input thread.",
    3: "signals_used equals exactly the set of all IDs cited in headline and claims.",
    4: "Claims are ordered by the earliest timestamp among their cited signals; claims citing only untimed signals come last.",
    5: "Every ID in unplaced_signals refers to a signal whose timestamp is missing in the input.",
    6: "If status is insufficient_evidence: zero signals, headline null, claims empty.",
    7: "If status is limited_evidence: exactly one signal.",
    8: "If status is ok: two or more signals and headline not null.",
    9: "A claim citing signals that contradict each other has confidence low.",
    10: "A claim citing a signal with a missing relevant field cannot have confidence high.",
}
