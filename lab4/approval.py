"""Module 6 human approval for ThreadLine: H1 (queue), H2 (decision), H3 (audit log).

Run from the repository root:
    python3 -m lab4.approval list
    python3 -m lab4.approval approve APR-001 --by "Shadid" --reason "Evidence matches the alert"
    python3 -m lab4.approval reject  APR-001 --by "Shadid" --reason "Wrong service"
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DIR = Path("lab4/approvals")


class ApprovalError(ValueError):
    """Raised when a decision breaks an H2 rule. Nothing is changed or logged as approved."""


class ApprovalQueue:
    """H1: every drafted action waits here as 'pending' until a named person decides."""

    def __init__(self, folder=DEFAULT_DIR):
        self.folder = Path(folder)
        self.queue_path = self.folder / "queue.json"
        self.audit_path = self.folder / "audit_log.jsonl"

    def _load(self):
        if not self.queue_path.exists():
            return []
        return json.loads(self.queue_path.read_text())

    def _save(self, items):
        self.folder.mkdir(parents=True, exist_ok=True)
        self.queue_path.write_text(json.dumps(items, indent=2) + "\n")

    def _audit(self, entry):
        # H3: append only. Old lines are never rewritten.
        self.folder.mkdir(parents=True, exist_ok=True)
        with self.audit_path.open("a") as log:
            log.write(json.dumps(entry) + "\n")

    def submit(self, thread_id, action, guardrails):
        """H1. Called by the Supervisor. Returns the new proposal ID."""
        items = self._load()
        proposal = {
            "proposal_id": f"APR-{len(items) + 1:03}",
            "thread_id": thread_id,
            "action": action,
            "guardrails": guardrails,
            "status": "pending",
            "executed": False,
            "submitted_at": _now(),
        }
        items.append(proposal)
        self._save(items)
        self._audit({"time": proposal["submitted_at"], "proposal_id": proposal["proposal_id"],
                     "event": "submitted", "by": "Supervisor", "thread_id": thread_id})
        return proposal["proposal_id"]

    def pending(self):
        return [p for p in self._load() if p["status"] == "pending"]

    def decide(self, proposal_id, decision, reviewer, reason):
        """H2. A named person approves or rejects. Approval never skips a guardrail."""
        if decision not in {"approve", "reject"}:
            raise ApprovalError("decision must be approve or reject")
        if not reviewer or not reviewer.strip():
            raise ApprovalError("a reviewer name is required")
        if not reason or not reason.strip():
            raise ApprovalError("a reason is required")
        items = self._load()
        proposal = next((p for p in items if p["proposal_id"] == proposal_id), None)
        if proposal is None:
            raise ApprovalError(f"unknown proposal {proposal_id}")
        if proposal["status"] != "pending":
            raise ApprovalError(f"{proposal_id} was already {proposal['status']}")
        if decision == "approve":
            # Guardrails win over people: a flagged or malformed proposal cannot be approved.
            if proposal["guardrails"].get("injection_detected"):
                raise ApprovalError("cannot approve: G2 flagged possible prompt injection")
            if proposal["action"].get("requires_human_approval") is not True:
                raise ApprovalError("cannot approve: G6 approval flag missing")
        proposal["status"] = "approved" if decision == "approve" else "rejected"
        proposal["decided_by"] = reviewer.strip()
        proposal["reason"] = reason.strip()
        proposal["decided_at"] = _now()
        # R2: approving records consent only. ThreadLine has no executor, so nothing runs.
        self._save(items)
        self._audit({"time": proposal["decided_at"], "proposal_id": proposal_id,
                     "event": proposal["status"], "by": proposal["decided_by"],
                     "reason": proposal["reason"], "executed": False})
        return proposal


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def main():
    parser = argparse.ArgumentParser(description="Approve or reject ThreadLine proposals")
    parser.add_argument("--dir", type=Path, default=DEFAULT_DIR)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    for name in ("approve", "reject"):
        p = sub.add_parser(name)
        p.add_argument("proposal_id")
        p.add_argument("--by", required=True)
        p.add_argument("--reason", required=True)
    args = parser.parse_args()
    queue = ApprovalQueue(args.dir)
    if args.command == "list":
        for p in queue.pending():
            print(p["proposal_id"], p["thread_id"], p["action"]["kind"], p["action"]["cited_signals"])
        return
    try:
        p = queue.decide(args.proposal_id, args.command, args.by, args.reason)
    except ApprovalError as exc:
        raise SystemExit(f"Refused: {exc}")
    print(p["proposal_id"], p["status"], "by", p["decided_by"], "- executed:", p["executed"])


if __name__ == "__main__":
    main()