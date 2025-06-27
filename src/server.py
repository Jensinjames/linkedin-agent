# See prior message for full code (FastAPI REST API, job submission, status, results)
# Place in src/server.py
import os
import json
from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import shutil
import uuid
from jose import jwt, JWTError

from src.database import JobDB
from src.queue.redis_queue import RedisQueue

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
SQLITE_PATH = os.environ.get("SQLITE_PATH", "/app/data/jobs.db")
JOBS_DIR = os.environ.get("JOBS_DIR", "/app/data/jobs")

SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET", "changeme")

def verify_admin(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    roles = []
    app_meta = payload.get("app_metadata") or {}
    if isinstance(app_meta, dict):
        roles = app_meta.get("roles", [])
    if isinstance(roles, str):
        roles = [roles]
    if "admin" not in roles and payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload

os.makedirs(JOBS_DIR, exist_ok=True)

app = FastAPI(title="LinkedIn Agent Job Queue API", version="1.0")

# Allow all origins for development (adjust in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

jobdb = JobDB(SQLITE_PATH)
queue = RedisQueue(redis_url=REDIS_URL)

@app.post("/submit")
async def submit_job(
    owner_email: str = Form(..., description="Submitter's email"),
    input_json: Optional[str] = Form(None, description="Input JSON (stringified)"),
    input_file: Optional[UploadFile] = File(None, description="Excel or CSV input"),
    webhook: Optional[str] = Form(None, description="Webhook URL for completion callback"),
    concurrency: Optional[int] = Form(2, description="Crawler concurrency"),
    max_retries: Optional[int] = Form(3, description="Max retries per batch"),
    timeout_secs: Optional[int] = Form(60, description="Timeout per batch in seconds"),
    user: dict = Depends(verify_admin)
):
    """
    Submit a new scraping job. Accepts a JSON config (required) and/or an uploaded Excel/CSV file.
    Returns a job_id.
    """
    job_input = {}
    input_path = None

    # Handle uploaded file
    if input_file:
        ext = os.path.splitext(input_file.filename)[-1].lower()
        if ext not in [".csv", ".xlsx"]:
            raise HTTPException(status_code=400, detail="Only .csv or .xlsx supported for input_file")
        file_id = str(uuid.uuid4())
        input_path = os.path.join(JOBS_DIR, f"{file_id}{ext}")
        with open(input_path, "wb") as f:
            shutil.copyfileobj(input_file.file, f)
        job_input["inputType"] = "csv" if ext == ".csv" else "excel"
        job_input["inputPath"] = input_path

    # Merge input_json with file info if both provided
    if input_json:
        try:
            job_input.update(json.loads(input_json))
        except Exception:
            raise HTTPException(status_code=400, detail="input_json must be valid JSON")

    # Enforce required fields
    if "query" not in job_input and not input_path:
        raise HTTPException(status_code=400, detail="Must provide either 'query' or upload an input_file")

    # Add runtime params
    job_input["webhook"] = webhook
    job_input["concurrency"] = concurrency
    job_input["maxRetries"] = max_retries
    job_input["timeoutSecs"] = timeout_secs

    # Save to DB and enqueue
    job_id = jobdb.create_job(job_input, owner_email)
    job_input["job_id"] = job_id
    jobdb.update_job_status(job_id, "queued")
    queue.enqueue(job_input)
    return {"job_id": job_id, "status": "queued"}

@app.get("/status/{job_id}")
async def job_status(job_id: int, user: dict = Depends(verify_admin)):
    """Get job status and stats."""
    job = jobdb.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    batches = jobdb.get_batches(job_id)
    return {
        "job": job,
        "batches": batches
    }

@app.get("/result/{job_id}")
async def get_result(job_id: int, user: dict = Depends(verify_admin)):
    """Download the final Excel result for a completed job."""
    job = jobdb.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "finished":
        return JSONResponse({"status": job["status"], "error": "Job not complete yet"}, status_code=202)
    # Output path: {JOBS_DIR}/job_{job_id}_final.xlsx
    output_path = os.path.normpath(os.path.join(JOBS_DIR, f"job_{job_id}_final.xlsx"))
    if not output_path.startswith(JOBS_DIR):
        raise HTTPException(status_code=400, detail="Invalid job ID or unauthorized access")
    if not os.path.isfile(output_path):
        return JSONResponse({"error": "Result Excel not found"}, status_code=500)
    from fastapi.responses import FileResponse
    return FileResponse(output_path, filename=f"linkedin_results_{job_id}.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@app.get("/jobs")
async def list_jobs(email: Optional[str] = None, user: dict = Depends(verify_admin)):
    jobs = jobdb.list_jobs(owner_email=email)
    return jobs

@app.get("/")
async def root():
    return {"message": "LinkedIn Agent Job Queue API is running"}