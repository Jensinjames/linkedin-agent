# Enhanced FastAPI REST API with rate limiting, security, and error handling
# Place in src/server.py
import os
import json
import time
import logging
from collections import defaultdict, deque
from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.base import BaseHTTPMiddleware
from typing import Optional, List
import shutil
import uuid
from jose import jwt, JWTError
import re

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from src.database import JobDB
from src.queue.redis_queue import RedisQueue
from src.health import router as health_router

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
SQLITE_PATH = os.environ.get("SQLITE_PATH", "/app/data/jobs.db")
JOBS_DIR = os.environ.get("JOBS_DIR", "/app/data/jobs")

SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET", "changeme")

# Rate limiting configuration
RATE_LIMIT_REQUESTS = int(os.environ.get("RATE_LIMIT_REQUESTS", "100"))  # requests per window
RATE_LIMIT_WINDOW = int(os.environ.get("RATE_LIMIT_WINDOW", "3600"))     # window in seconds (1 hour)

# CORS configuration
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window approach"""
    
    def __init__(self, app, requests_per_window: int = RATE_LIMIT_REQUESTS, window_seconds: int = RATE_LIMIT_WINDOW):
        super().__init__(app)
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.clients = defaultdict(deque)
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier (IP address or user ID from token)"""
        # Try to get user ID from authorization header
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                token = auth_header.split(" ", 1)[1]
                payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"])
                return f"user:{payload.get('sub', 'unknown')}"
            except:
                pass
        
        # Fall back to IP address
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return f"ip:{forwarded_for.split(',')[0].strip()}"
        return f"ip:{request.client.host}"
    
    def _is_rate_limited(self, client_id: str) -> bool:
        """Check if client is rate limited"""
        now = time.time()
        client_requests = self.clients[client_id]
        
        # Remove old requests outside the window
        while client_requests and client_requests[0] <= now - self.window_seconds:
            client_requests.popleft()
        
        # Check if limit exceeded
        if len(client_requests) >= self.requests_per_window:
            return True
        
        # Add current request
        client_requests.append(now)
        return False
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        client_id = self._get_client_id(request)
        
        if self._is_rate_limited(client_id):
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded", "retry_after": self.window_seconds}
            )
        
        return await call_next(request)

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def sanitize_string(value: str, max_length: int = 1000) -> str:
    """Sanitize string input"""
    if not isinstance(value, str):
        raise ValueError("Value must be a string")
    
    # Remove null bytes and control characters
    sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', value)
    
    # Limit length
    if len(sanitized) > max_length:
        raise ValueError(f"String too long (max {max_length} characters)")
    
    return sanitized.strip()

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

app = FastAPI(
    title="LinkedIn Agent Job Queue API", 
    version="1.0",
    description="Secure LinkedIn scraping job queue with rate limiting and authentication"
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Secure CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["X-Total-Count"]
)

# Include health check router
app.include_router(health_router, tags=["health"])

# Global exception handler for better error handling
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    logger.error(f"Validation error on {request.url}: {exc}")
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid input", "detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "An unexpected error occurred"}
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
    Submit a new scraping job with comprehensive input validation.
    Accepts a JSON config (required) and/or an uploaded Excel/CSV file.
    Returns a job_id.
    """
    try:
        # Validate and sanitize owner_email
        owner_email = sanitize_string(owner_email, 254)  # RFC 5321 email length limit
        if not validate_email(owner_email):
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        # Validate numeric parameters
        if concurrency is not None and (not isinstance(concurrency, int) or concurrency < 1 or concurrency > 10):
            raise HTTPException(status_code=400, detail="Concurrency must be between 1 and 10")
        
        if max_retries is not None and (not isinstance(max_retries, int) or max_retries < 0 or max_retries > 10):
            raise HTTPException(status_code=400, detail="Max retries must be between 0 and 10")
        
        if timeout_secs is not None and (not isinstance(timeout_secs, int) or timeout_secs < 10 or timeout_secs > 300):
            raise HTTPException(status_code=400, detail="Timeout must be between 10 and 300 seconds")
        
        # Validate webhook URL if provided
        if webhook:
            webhook = sanitize_string(webhook, 2048)
            if not webhook.startswith(('http://', 'https://')):
                raise HTTPException(status_code=400, detail="Webhook must be a valid HTTP/HTTPS URL")
        
        job_input = {}
        input_path = None

        # Handle uploaded file with validation
        if input_file:
            # Validate file size (max 10MB)
            if input_file.size and input_file.size > 10 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="File size must be less than 10MB")
            
            # Validate filename
            if not input_file.filename:
                raise HTTPException(status_code=400, detail="Filename is required")
            
            filename = sanitize_string(input_file.filename, 255)
            ext = os.path.splitext(filename)[-1].lower()
            if ext not in [".csv", ".xlsx"]:
                raise HTTPException(status_code=400, detail="Only .csv or .xlsx files are supported")
            
            # Generate secure file path
            file_id = str(uuid.uuid4())
            input_path = os.path.join(JOBS_DIR, f"{file_id}{ext}")
            
            # Ensure path is within JOBS_DIR (prevent directory traversal)
            if not os.path.abspath(input_path).startswith(os.path.abspath(JOBS_DIR)):
                raise HTTPException(status_code=400, detail="Invalid file path")
            
            # Save file securely
            with open(input_path, "wb") as f:
                shutil.copyfileobj(input_file.file, f)
            
            job_input["inputType"] = "csv" if ext == ".csv" else "excel"
            job_input["inputPath"] = input_path
            logger.info(f"Uploaded file saved: {input_path}")

        # Validate and parse input_json
        if input_json:
            input_json = sanitize_string(input_json, 10000)  # Limit JSON size
            try:
                parsed_json = json.loads(input_json)
                if not isinstance(parsed_json, dict):
                    raise HTTPException(status_code=400, detail="input_json must be a JSON object")
                job_input.update(parsed_json)
            except json.JSONDecodeError as e:
                raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")

        # Validate required fields
        if "query" not in job_input and not input_path:
            raise HTTPException(status_code=400, detail="Must provide either 'query' in input_json or upload an input_file")
        
        # Validate query if provided
        if "query" in job_input:
            if not isinstance(job_input["query"], str):
                raise HTTPException(status_code=400, detail="Query must be a string")
            job_input["query"] = sanitize_string(job_input["query"], 1000)

        # Add runtime params with defaults
        job_input["webhook"] = webhook
        job_input["concurrency"] = concurrency or 2
        job_input["maxRetries"] = max_retries or 3
        job_input["timeoutSecs"] = timeout_secs or 60

        # Save to DB and enqueue with transaction
        job_id = jobdb.create_job(job_input, owner_email)
        job_input["job_id"] = job_id
        jobdb.update_job_status(job_id, "queued")
        queue.enqueue(job_input)
        
        logger.info(f"Job {job_id} submitted successfully by {owner_email}")
        return {"job_id": job_id, "status": "queued"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting job: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to submit job")

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