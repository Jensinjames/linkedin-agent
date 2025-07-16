# See prior message for full code (worker loop, batch chunking, retry, Excel pipeline)
# Place in src/worker.py
import os
import sys
import time
import json
import shutil
import logging
import traceback
import uuid
from pathlib import Path
from datetime import datetime
import polars as pl

from src.database import JobDB
from src.queue.redis_queue import RedisQueue

# Config
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
# Use local paths for development, container paths for production
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DATA_DIR = os.path.join(BASE_DIR, "..", "storage", "data")
SQLITE_PATH = os.environ.get("SQLITE_PATH", os.path.join(DEFAULT_DATA_DIR, "jobs.db"))
JOBS_DIR = os.environ.get("JOBS_DIR", os.path.join(DEFAULT_DATA_DIR, "jobs"))
BATCH_SIZE = 10000
MAX_RETRIES = 3

# Create necessary directories
try:
    os.makedirs(JOBS_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)
except PermissionError as e:
    print(f"Warning: Could not create directories: {e}")
    print(f"Make sure you have write permissions for: {JOBS_DIR}")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def batch_csv(input_path, output_dir, batch_size):
    # Returns list of batch file paths
    df = pl.read_csv(input_path)
    n = len(df)
    batch_files = []
    for i in range(0, n, batch_size):
        batch_df = df.slice(i, batch_size)
        batch_file = os.path.join(output_dir, f"batch_{i//batch_size:04d}.csv")
        batch_df.write_csv(batch_file)
        batch_files.append(batch_file)
    return batch_files

def batch_xlsx(input_path, output_dir, batch_size):
    # Returns list of batch file paths
    df = pl.read_excel(input_path)
    n = len(df)
    batch_files = []
    for i in range(0, n, batch_size):
        batch_df = df.slice(i, batch_size)
        batch_file = os.path.join(output_dir, f"batch_{i//batch_size:04d}.xlsx")
        batch_df.write_excel(batch_file)
        batch_files.append(batch_file)
    return batch_files

def merge_excel(outputs, final_path):
    import pandas as pd
    dfs = []
    for f in outputs:
        if Path(f).exists() and Path(f).stat().st_size > 0:
            try:
                dfs.append(pd.read_excel(f))
            except Exception:
                continue
    if dfs:
        pd.concat(dfs, ignore_index=True).to_excel(final_path, index=False)

def run_batch(batch_json_path, batch_output_json, batch_output_xlsx):
    # Run CLI for batch, then convert output to Excel
    import subprocess
    try:
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", batch_json_path],
            capture_output=True,
            text=True,
            check=True
        )
        with open(batch_output_json, "w") as f:
            f.write(result.stdout)
        # Convert JSON to Excel
        import polars as pl
        import pandas as pd
        with open(batch_output_json) as f:
            data = json.load(f)
        records = data["results"] if "results" in data else data
        if not records:
            pd.DataFrame().to_excel(batch_output_xlsx, index=False)
        else:
            out = []
            for x in records:
                out.append({
                    'Full Name': x.get('name', ''),
                    'Headline': x.get('headline', ''),
                    'Company': x.get('company') or x.get('company_name', ''),
                    'Location': x.get('location', ''),
                    'Connections': x.get('connections', ''),
                    'About': x.get('about', ''),
                    'Experience': str(x.get('experience', '')),
                    'Education': str(x.get('education', '')),
                    'Skills': ', '.join(x.get('skills', [])) if isinstance(x.get('skills'), list) else (x.get('skills') or '')
                })
            pd.DataFrame(out).to_excel(batch_output_xlsx, index=False)
        return True, None
    except Exception as e:
        with open(batch_output_json, "w") as f:
            f.write(json.dumps({"error": str(e), "traceback": traceback.format_exc()}))
        return False, str(e)

def process_job(job, jobdb: JobDB):
    job_id = job["job_id"]
    input_json = job.copy()
    owner_email = job.get("owner_email")
    created_at = job.get("created_at")
    job_dir = os.path.join(JOBS_DIR, f"job_{job_id}")
    batches_dir = os.path.join(job_dir, "batches")
    outputs_dir = os.path.join(job_dir, "outputs")
    os.makedirs(batches_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)
    input_path = job.get("inputPath")

    # Determine input type and batch
    batch_files = []
    if job.get("inputType") == "csv" and input_path:
        batch_files = batch_csv(input_path, batches_dir, BATCH_SIZE)
    elif job.get("inputType") == "excel" and input_path:
        batch_files = batch_xlsx(input_path, batches_dir, BATCH_SIZE)
    elif job.get("query"):
        # Single JSON "query" string, one batch only
        batch_file = os.path.join(batches_dir, "batch_0000.json")
        with open(batch_file, "w") as f:
            json.dump(job, f)
        batch_files = [batch_file]
    else:
        logging.error(f"Job {job_id} has no valid input.")
        jobdb.update_job_status(job_id, "failed", error_msg="No valid input for job")
        return

    # Register batches in DB
    for idx, batch_file in enumerate(batch_files):
        jobdb.create_batch(job_id, idx, batch_file)

    # Process each batch with retries/resume
    for batch_row in jobdb.get_batches(job_id):
        batch_id = batch_row["id"]
        batch_index = batch_row["batch_index"]
        input_batch_path = batch_row["input_path"]
        output_json = os.path.join(outputs_dir, f"batch_{batch_index:04d}_output.json")
        output_xlsx = os.path.join(outputs_dir, f"batch_{batch_index:04d}_output.xlsx")

        # Skip if already finished
        if batch_row["status"] == "finished" and Path(output_xlsx).exists():
            continue

        for attempt in range(1, MAX_RETRIES+1):
            jobdb.update_batch_status(batch_id, "running")
            logging.info(f"Job {job_id} batch {batch_index} attempt {attempt}")
            # Prepare batch input json
            if input_batch_path.endswith(".json"):
                batch_json_path = input_batch_path
            else:
                # Create input json for this batch
                batch_json_path = os.path.join(outputs_dir, f"batch_{batch_index:04d}_input.json")
                batch_input = job.copy()
                batch_input["inputType"] = "csv" if input_batch_path.endswith(".csv") else "excel"
                batch_input["inputPath"] = input_batch_path
                with open(batch_json_path, "w") as f:
                    json.dump(batch_input, f)
            # Run and handle output
            ok, err = run_batch(batch_json_path, output_json, output_xlsx)
            if ok:
                jobdb.update_batch_status(batch_id, "finished")
                jobdb.save_batch_output(batch_id, output_xlsx)
                break
            else:
                jobdb.update_batch_status(batch_id, "failed", error_msg=err)
                time.sleep(10 * attempt)
        # If still not succeeded, mark as failed
        batch_row = jobdb.get_batch(batch_id)
        if batch_row["status"] != "finished":
            logging.error(f"Job {job_id} batch {batch_index} failed after {MAX_RETRIES} attempts.")

    # After all batches, merge results
    batch_outputs = [row["output_path"] for row in jobdb.get_batches(job_id) if row["status"] == "finished" and row["output_path"]]
    final_xlsx = os.path.join(JOBS_DIR, f"job_{job_id}_final.xlsx")
    merge_excel(batch_outputs, final_xlsx)
    # Store job result reference in DB
    jobdb.update_job_status(job_id, "finished")
    jobdb.save_job_result(job_id, {"final_xlsx": final_xlsx, "batches": batch_outputs})

    # Optionally POST webhook
    webhook = job.get("webhook")
    if webhook:
        import requests
        try:
            resp = requests.post(webhook, json={"job_id": job_id, "status": "finished", "result": {"final_xlsx": final_xlsx}})
            logging.info(f"Webhook POST to {webhook}, status {resp.status_code}")
        except Exception as e:
            logging.error(f"Failed to POST webhook: {e}")

def main():
    jobdb = JobDB(SQLITE_PATH)
    queue = RedisQueue(redis_url=REDIS_URL)
    logging.info("Worker started, waiting for jobs...")
    while True:
        job = queue.dequeue()
        if not job:
            time.sleep(2)
            continue
        job_id = job.get("job_id")
        logging.info(f"Dequeued job {job_id}")
        jobdb.update_job_status(job_id, "running")
        try:
            process_job(job, jobdb)
        except Exception as e:
            logging.error(f"Job {job_id} failed: {e}")
            jobdb.update_job_status(job_id, "failed", error_msg=str(e))
            continue

if __name__ == "__main__":
    main()