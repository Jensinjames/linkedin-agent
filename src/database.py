# See prior message for full code (SQLite job/result schema and helpers)
# Place in src/database.py
import sqlite3
import json
from datetime import datetime
from typing import Optional, Any, Dict, List

DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_email TEXT,
    input_json TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    created_at TEXT NOT NULL,
    started_at TEXT,
    finished_at TEXT,
    result_json TEXT,
    log_path TEXT,
    error_msg TEXT
);

CREATE TABLE IF NOT EXISTS batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    batch_index INTEGER NOT NULL,
    input_path TEXT,
    output_path TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    started_at TEXT,
    finished_at TEXT,
    error_msg TEXT,
    FOREIGN KEY(job_id) REFERENCES jobs(id)
);
"""

def get_conn(sqlite_path: str):
    conn = sqlite3.connect(sqlite_path, check_same_thread=False, isolation_level=None)
    conn.row_factory = sqlite3.Row
    return conn

class JobDB:
    def __init__(self, sqlite_path: str):
        self.sqlite_path = sqlite_path
        self.conn = get_conn(sqlite_path)
        self.ensure_schema()

    def ensure_schema(self):
        with self.conn:
            self.conn.executescript(DB_SCHEMA)

    def create_job(self, input_json: Dict, owner_email: Optional[str]) -> int:
        now = datetime.utcnow().isoformat()
        cur = self.conn.execute(
            "INSERT INTO jobs (owner_email, input_json, status, created_at) VALUES (?, ?, 'queued', ?)",
            (owner_email, json.dumps(input_json), now)
        )
        return cur.lastrowid

    def update_job_status(self, job_id: int, status: str, error_msg: Optional[str] = None):
        now = datetime.utcnow().isoformat()
        if status == "running":
            self.conn.execute(
                "UPDATE jobs SET status=?, started_at=? WHERE id=?",
                (status, now, job_id)
            )
        elif status in ("finished", "failed"):
            self.conn.execute(
                "UPDATE jobs SET status=?, finished_at=?, error_msg=? WHERE id=?",
                (status, now, error_msg, job_id)
            )
        else:
            self.conn.execute(
                "UPDATE jobs SET status=? WHERE id=?",
                (status, job_id)
            )

    def save_job_result(self, job_id: int, result: Any):
        self.conn.execute(
            "UPDATE jobs SET result_json=? WHERE id=?",
            (json.dumps(result), job_id)
        )

    def get_job(self, job_id: int) -> Optional[Dict]:
        cur = self.conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def list_jobs(self, owner_email: Optional[str] = None) -> List[Dict]:
        if owner_email:
            cur = self.conn.execute("SELECT * FROM jobs WHERE owner_email=? ORDER BY id DESC", (owner_email,))
        else:
            cur = self.conn.execute("SELECT * FROM jobs ORDER BY id DESC")
        return [dict(row) for row in cur.fetchall()]

    def create_batch(self, job_id: int, batch_index: int, input_path: str) -> int:
        cur = self.conn.execute(
            "INSERT INTO batches (job_id, batch_index, input_path, status) VALUES (?, ?, ?, 'pending')",
            (job_id, batch_index, input_path)
        )
        return cur.lastrowid

    def update_batch_status(self, batch_id: int, status: str, error_msg: Optional[str] = None):
        now = datetime.utcnow().isoformat()
        if status == "running":
            self.conn.execute(
                "UPDATE batches SET status=?, started_at=? WHERE id=?",
                (status, now, batch_id)
            )
        elif status in ("finished", "failed"):
            self.conn.execute(
                "UPDATE batches SET status=?, finished_at=?, error_msg=? WHERE id=?",
                (status, now, error_msg, batch_id)
            )
        else:
            self.conn.execute(
                "UPDATE batches SET status=? WHERE id=?",
                (status, batch_id)
            )

    def save_batch_output(self, batch_id: int, output_path: str):
        self.conn.execute(
            "UPDATE batches SET output_path=? WHERE id=?",
            (output_path, batch_id)
        )

    def get_batches(self, job_id: int) -> List[Dict]:
        cur = self.conn.execute("SELECT * FROM batches WHERE job_id=? ORDER BY batch_index ASC", (job_id,))
        return [dict(row) for row in cur.fetchall()]

    def get_pending_batches(self, job_id: int) -> List[Dict]:
        cur = self.conn.execute(
            "SELECT * FROM batches WHERE job_id=? AND status IN ('pending','failed') ORDER BY batch_index ASC",
            (job_id,)
        )
        return [dict(row) for row in cur.fetchall()]

    def get_batch(self, batch_id: int) -> Optional[Dict]:
        cur = self.conn.execute("SELECT * FROM batches WHERE id=?", (batch_id,))
        row = cur.fetchone()
        return dict(row) if row else None