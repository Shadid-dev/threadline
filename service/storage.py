"""Persistent storage for the ThreadLine service (step 13).

Threads and approvals are kept in a database instead of memory or local files,
so they survive restarts. The rules stay in lab4: these classes only change WHERE
data is saved, never WHAT is allowed.

    DATABASE_URL not set  ->  SQLite file service_data/threadline.db (local runs)
"""
from __future__ import annotations

import copy
import json
import os
import sqlite3
from pathlib import Path

from lab4.approval import ApprovalQueue
from lab4.system import ThreadStore


class Database:
    """Two tables: 'state' holds the current threads and approvals as JSON;
    'audit_log' is H3 and is append-only (INSERT only, never UPDATE or DELETE)."""

    def __init__(self, url: str | None = None):
        url = url or os.getenv("DATABASE_URL") or "sqlite:///service_data/threadline.db"
        if not url.startswith("sqlite:///"):
            raise ValueError("Only sqlite:/// URLs are supported until step 13b (Postgres)")
        path = Path(url.removeprefix("sqlite:///"))
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.execute("CREATE TABLE IF NOT EXISTS state (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS audit_log (id INTEGER PRIMARY KEY, entry TEXT NOT NULL)")
        self.conn.commit()

    def get(self, key, default):
        row = self.conn.execute("SELECT value FROM state WHERE key = ?", (key,)).fetchone()
        return json.loads(row[0]) if row else default

    def put(self, key, value):
        self.conn.execute("INSERT INTO state (key, value) VALUES (?, ?) "
                          "ON CONFLICT (key) DO UPDATE SET value = excluded.value",
                          (key, json.dumps(value)))
        self.conn.commit()

    def append_audit(self, entry):
        self.conn.execute("INSERT INTO audit_log (entry) VALUES (?)", (json.dumps(entry),))
        self.conn.commit()

    def audit_entries(self):
        return [json.loads(r[0]) for r in self.conn.execute("SELECT entry FROM audit_log ORDER BY id")]


class DbThreadStore(ThreadStore):
    """lab4 ThreadStore that loads its threads at start and saves after every change."""

    def __init__(self, db: Database):
        super().__init__(threads=db.get("threads", []))
        self.db = db

    def commit(self, signal, thread_id=None):
        thread, changed = super().commit(signal, thread_id)   # all lab4 checks run here
        if changed:
            self.db.put("threads", self.threads)
        return thread, changed


class DbApprovalQueue(ApprovalQueue):
    """lab4 ApprovalQueue (H1-H3 rules unchanged) with the database instead of files."""

    def __init__(self, db: Database):
        self.db = db

    def _load(self):
        return copy.deepcopy(self.db.get("approvals", []))

    def _save(self, items):
        self.db.put("approvals", items)

    def _audit(self, entry):
        self.db.append_audit(entry)
