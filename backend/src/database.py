# Enhanced database layer with connection pooling, transactions, and indexing
# Place in src/database.py
import sqlite3
import json
import threading
import logging
from datetime import datetime
from typing import Optional, Any, Dict, List
from contextlib import contextmanager
from queue import Queue, Empty

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_jobs_owner_email ON jobs(owner_email);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at);
CREATE INDEX IF NOT EXISTS idx_batches_job_id ON batches(job_id);
CREATE INDEX IF NOT EXISTS idx_batches_status ON batches(status);
"""

class ConnectionPool:
    """Simple connection pool for SQLite"""
    def __init__(self, sqlite_path: str, max_connections: int = 10):
        self.sqlite_path = sqlite_path
        self.max_connections = max_connections
        self.pool = Queue(maxsize=max_connections)
        self.lock = threading.Lock()
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize the connection pool"""
        for _ in range(self.max_connections):
            conn = self._create_connection()
            self.pool.put(conn)
    
    def _create_connection(self):
        """Create a new database connection"""
        conn = sqlite3.connect(
            self.sqlite_path, 
            check_same_thread=False, 
            isolation_level=None,
            timeout=30.0
        )
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=MEMORY")
        return conn
    
    @contextmanager
    def get_connection(self):
        """Get a connection from the pool"""
        conn = None
        try:
            conn = self.pool.get(timeout=5.0)
            yield conn
        except Empty:
            # If pool is empty, create a temporary connection
            logger.warning("Connection pool exhausted, creating temporary connection")
            conn = self._create_connection()
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                try:
                    # Return connection to pool if it's healthy
                    conn.execute("SELECT 1")  # Test connection
                    if self.pool.qsize() < self.max_connections:
                        self.pool.put(conn)
                    else:
                        conn.close()
                except:
                    conn.close()
    
    def close_all(self):
        """Close all connections in the pool"""
        while not self.pool.empty():
            try:
                conn = self.pool.get_nowait()
                conn.close()
            except Empty:
                break

def get_conn(sqlite_path: str):
    conn = sqlite3.connect(sqlite_path, check_same_thread=False, isolation_level=None)
    conn.row_factory = sqlite3.Row
    return conn

class JobDB:
    def __init__(self, sqlite_path: str):
        self.sqlite_path = sqlite_path
        self.pool = ConnectionPool(sqlite_path)
        self.ensure_schema()

    def ensure_schema(self):
        with self.pool.get_connection() as conn:
            conn.executescript(DB_SCHEMA)
            logger.info("Database schema initialized successfully")

    @contextmanager
    def transaction(self):
        """Context manager for database transactions with rollback support"""
        with self.pool.get_connection() as conn:
            try:
                conn.execute("BEGIN TRANSACTION")
                yield conn
                conn.execute("COMMIT")
                logger.debug("Transaction committed successfully")
            except Exception as e:
                conn.execute("ROLLBACK")
                logger.error(f"Transaction rolled back due to error: {e}")
                raise

    def create_job(self, input_json: Dict, owner_email: Optional[str]) -> int:
        """Create a new job with input validation"""
        # Input validation
        if not isinstance(input_json, dict):
            raise ValueError("input_json must be a dictionary")
        if owner_email and not isinstance(owner_email, str):
            raise ValueError("owner_email must be a string")
        
        now = datetime.utcnow().isoformat()
        try:
            with self.transaction() as conn:
                cur = conn.execute(
                    "INSERT INTO jobs (owner_email, input_json, status, created_at) VALUES (?, ?, 'queued', ?)",
                    (owner_email, json.dumps(input_json), now)
                )
                job_id = cur.lastrowid
                logger.info(f"Created job {job_id} for owner {owner_email}")
                return job_id
        except Exception as e:
            logger.error(f"Failed to create job: {e}")
            raise

    def update_job_status(self, job_id: int, status: str, error_msg: Optional[str] = None):
        """Update job status with validation"""
        # Input validation
        if not isinstance(job_id, int) or job_id <= 0:
            raise ValueError("job_id must be a positive integer")
        if not isinstance(status, str) or status not in ["queued", "running", "finished", "failed"]:
            raise ValueError("status must be one of: queued, running, finished, failed")
        
        now = datetime.utcnow().isoformat()
        try:
            with self.transaction() as conn:
                if status == "running":
                    conn.execute(
                        "UPDATE jobs SET status=?, started_at=? WHERE id=?",
                        (status, now, job_id)
                    )
                elif status in ("finished", "failed"):
                    conn.execute(
                        "UPDATE jobs SET status=?, finished_at=?, error_msg=? WHERE id=?",
                        (status, now, error_msg, job_id)
                    )
                else:
                    conn.execute(
                        "UPDATE jobs SET status=? WHERE id=?",
                        (status, job_id)
                    )
                logger.info(f"Updated job {job_id} status to {status}")
        except Exception as e:
            logger.error(f"Failed to update job {job_id} status: {e}")
            raise

    def save_job_result(self, job_id: int, result: Any):
        """Save job result with validation"""
        if not isinstance(job_id, int) or job_id <= 0:
            raise ValueError("job_id must be a positive integer")
        
        try:
            with self.transaction() as conn:
                conn.execute(
                    "UPDATE jobs SET result_json=? WHERE id=?",
                    (json.dumps(result), job_id)
                )
                logger.info(f"Saved result for job {job_id}")
        except Exception as e:
            logger.error(f"Failed to save result for job {job_id}: {e}")
            raise

    def get_job(self, job_id: int) -> Optional[Dict]:
        """Get job by ID with validation"""
        if not isinstance(job_id, int) or job_id <= 0:
            raise ValueError("job_id must be a positive integer")
        
        try:
            with self.pool.get_connection() as conn:
                cur = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,))
                row = cur.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {e}")
            raise

    def list_jobs(self, owner_email: Optional[str] = None) -> List[Dict]:
        """List jobs with optional owner filter"""
        try:
            with self.pool.get_connection() as conn:
                if owner_email:
                    if not isinstance(owner_email, str):
                        raise ValueError("owner_email must be a string")
                    cur = conn.execute("SELECT * FROM jobs WHERE owner_email=? ORDER BY id DESC", (owner_email,))
                else:
                    cur = conn.execute("SELECT * FROM jobs ORDER BY id DESC")
                return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Failed to list jobs: {e}")
            raise

    def create_batch(self, job_id: int, batch_index: int, input_path: str) -> int:
        """Create a new batch with validation"""
        # Input validation
        if not isinstance(job_id, int) or job_id <= 0:
            raise ValueError("job_id must be a positive integer")
        if not isinstance(batch_index, int) or batch_index < 0:
            raise ValueError("batch_index must be a non-negative integer")
        if not isinstance(input_path, str) or not input_path.strip():
            raise ValueError("input_path must be a non-empty string")
        
        try:
            with self.transaction() as conn:
                cur = conn.execute(
                    "INSERT INTO batches (job_id, batch_index, input_path, status) VALUES (?, ?, ?, 'pending')",
                    (job_id, batch_index, input_path)
                )
                batch_id = cur.lastrowid
                logger.info(f"Created batch {batch_id} for job {job_id}")
                return batch_id
        except Exception as e:
            logger.error(f"Failed to create batch for job {job_id}: {e}")
            raise

    def update_batch_status(self, batch_id: int, status: str, error_msg: Optional[str] = None):
        """Update batch status with validation"""
        # Input validation
        if not isinstance(batch_id, int) or batch_id <= 0:
            raise ValueError("batch_id must be a positive integer")
        if not isinstance(status, str) or status not in ["pending", "running", "finished", "failed"]:
            raise ValueError("status must be one of: pending, running, finished, failed")
        
        now = datetime.utcnow().isoformat()
        try:
            with self.transaction() as conn:
                if status == "running":
                    conn.execute(
                        "UPDATE batches SET status=?, started_at=? WHERE id=?",
                        (status, now, batch_id)
                    )
                elif status in ("finished", "failed"):
                    conn.execute(
                        "UPDATE batches SET status=?, finished_at=?, error_msg=? WHERE id=?",
                        (status, now, error_msg, batch_id)
                    )
                else:
                    conn.execute(
                        "UPDATE batches SET status=? WHERE id=?",
                        (status, batch_id)
                    )
                logger.info(f"Updated batch {batch_id} status to {status}")
        except Exception as e:
            logger.error(f"Failed to update batch {batch_id} status: {e}")
            raise

    def save_batch_output(self, batch_id: int, output_path: str):
        """Save batch output path with validation"""
        if not isinstance(batch_id, int) or batch_id <= 0:
            raise ValueError("batch_id must be a positive integer")
        if not isinstance(output_path, str) or not output_path.strip():
            raise ValueError("output_path must be a non-empty string")
        
        try:
            with self.transaction() as conn:
                conn.execute(
                    "UPDATE batches SET output_path=? WHERE id=?",
                    (output_path, batch_id)
                )
                logger.info(f"Saved output path for batch {batch_id}")
        except Exception as e:
            logger.error(f"Failed to save output path for batch {batch_id}: {e}")
            raise

    def get_batches(self, job_id: int) -> List[Dict]:
        """Get all batches for a job with validation"""
        if not isinstance(job_id, int) or job_id <= 0:
            raise ValueError("job_id must be a positive integer")
        
        try:
            with self.pool.get_connection() as conn:
                cur = conn.execute("SELECT * FROM batches WHERE job_id=? ORDER BY batch_index ASC", (job_id,))
                return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get batches for job {job_id}: {e}")
            raise

    def get_pending_batches(self, job_id: int) -> List[Dict]:
        """Get pending batches for a job with validation"""
        if not isinstance(job_id, int) or job_id <= 0:
            raise ValueError("job_id must be a positive integer")
        
        try:
            with self.pool.get_connection() as conn:
                cur = conn.execute(
                    "SELECT * FROM batches WHERE job_id=? AND status IN ('pending','failed') ORDER BY batch_index ASC",
                    (job_id,)
                )
                return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get pending batches for job {job_id}: {e}")
            raise

    def get_batch(self, batch_id: int) -> Optional[Dict]:
        """Get batch by ID with validation"""
        if not isinstance(batch_id, int) or batch_id <= 0:
            raise ValueError("batch_id must be a positive integer")
        
        try:
            with self.pool.get_connection() as conn:
                cur = conn.execute("SELECT * FROM batches WHERE id=?", (batch_id,))
                row = cur.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Failed to get batch {batch_id}: {e}")
            raise

    def close(self):
        """Close all database connections"""
        self.pool.close_all()
        logger.info("Database connections closed")