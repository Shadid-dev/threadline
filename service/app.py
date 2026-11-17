"""ThreadLine web service: the existing lab4 pipeline behind an HTTP API.

Run locally from the repository root:
    python3 -m uvicorn service.app:app --reload
Then open http://127.0.0.1:8000/docs to try every endpoint in the browser.
"""
from __future__ import annotations

import threading

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from lab4.approval import ApprovalError
from lab4.system import OfflineBackend, Orchestrator
from service.storage import Database, DbApprovalQueue, DbThreadStore

app = FastAPI(title="ThreadLine", description="Shared incident context for responders and agents.")

# One database, store, approval queue and Supervisor for the whole service.
DB = Database()                      # DATABASE_URL, or a local SQLite file by default
STORE = DbThreadStore(DB)
QUEUE = DbApprovalQueue(DB)
SYSTEM = Orchestrator(mode="dynamic", backend=OfflineBackend(), store=STORE, queue=QUEUE)
LOCK = threading.Lock()   # one signal at a time, so two requests never edit the store together


class Signal(BaseModel):
    """The 5-field signal every source is converted into (same fields G1 checks)."""
    signal_id: str
    source: str
    service: str | None
    timestamp: str
    content: str



class Decision(BaseModel):
    """A responder's answer to a pending proposal (H2: name and reason are required)."""
    decision: str     # "approve" or "reject"
    by: str
    reason: str

@app.get("/health")
def health():
    return {"status": "ok", "backend": SYSTEM.backend.name, "threads": len(STORE.threads)}


@app.post("/signals")
def post_signal(signal: Signal):
    with LOCK:
        try:
            output = SYSTEM.run(signal.model_dump())
        except ValueError as exc:            # G1 rejected the signal; nothing was stored
            raise HTTPException(status_code=422, detail=str(exc))
    return output["result"]


@app.get("/threads")
def list_threads():
    return STORE.threads


@app.get("/approvals")
def pending_approvals():
    return QUEUE.pending()


@app.post("/approvals/{proposal_id}")
def decide(proposal_id: str, decision: Decision):
    try:
        with LOCK:                           # same lock as /signals: one writer at a time
            return QUEUE.decide(proposal_id, decision.decision, decision.by, decision.reason)
    except ApprovalError as exc:             # H2 refused the decision; nothing changed
        raise HTTPException(status_code=409, detail=str(exc))
