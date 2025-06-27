# 🚀 Advanced LinkedIn Scraping Agent

A production-ready LinkedIn scraping agent with queueing, resumable batching, anti-detection, REST API, and CLI/batch support.

---

## ✨ Features

- **Playwright-based LinkedIn scraping** with low-fingerprint anti-detection
- **Rotating residential proxies** via Apify Proxy groups (see `proxyConfiguration` in input config)
- **Excel → JSON → Excel pipeline**: Drop in a spreadsheet, get a CRM-ready workbook (Full Name, Headline, Company, Location, Connections, About, Experience, Education, Skills)
- **Production queue**: Docker Compose stack with REST API, Redis queue, and SQLite job persistence
- **Batch/resumable chunking**: 10,000 profiles per batch, with automatic retry/resume
- **CLI/REST/webhook integration**: Trigger jobs from CLI, n8n, Zapier, or your own backend
- **Configurable knobs**: concurrency, maxRetries, timeoutSecs
- **One-command spin-up**: `docker compose up -d` for API, worker, Redis, and SQLite
- **Job tracking**: `/status/{job_id}`, `/result/{job_id}` endpoints

---

## 🚦 Usage

### 1. Quick Start (Production Queue)

```bash
cp .env.example .env
docker compose up -d
```

- REST API runs on http://localhost:8000

#### Submit a job (Excel/CSV or JSON):

```bash
# Excel/CSV file upload
curl -F "owner_email=me@example.com" -F "input_file=@input.xlsx" http://localhost:8000/submit

# JSON input
curl -F "owner_email=me@example.com" -F "input_json={\"query\":\"https://linkedin.com/in/someone\"}" http://localhost:8000/submit
```

#### Check job status:

```bash
curl http://localhost:8000/status/1
```

#### Download results:

```bash
curl -OJ http://localhost:8000/result/1
```

### 2. Batch Processing Script

For very large spreadsheets, split and submit in chunks:

```bash
./src/batch_scrape_excel.sh my_contacts.xlsx
```

### 3. CLI/Manual Mode

```bash
python -m src.cli input.json
# or (using wrapper for n8n/Zapier)
python src/apify_wrapper.py --input input.json --webhook <your_webhook_url>
```

---

## 🛠️ Architecture

- **src/server.py**: FastAPI REST API for job submission/status/results
- **src/worker.py**: Worker process (consumes jobs from Redis, processes batches, saves results)
- **src/database.py**: SQLite job/result storage (resumable, tracks batches, status, errors)
- **src/queue/redis_queue.py**: Simple Redis queue
- **src/apify_wrapper.py**: CLI/REST bridge for single jobs and webhooks
- **src/batch_scrape_excel.sh**: Bash util to split/submit large Excel files

---

## ⚙️ Configuration

See `.env.example` for all environment variables.
- Set `OPENAI_API_KEY` and `APIFY_TOKEN` (for LLM/proxy features)
- `REDIS_URL` and `SQLITE_PATH` are set by default for Compose
- `BATCH_SIZE`, `CONCURRENCY`, `MAX_RETRIES`, `TIMEOUT_SECS` control batch/worker behavior

---

## 📑 API Endpoints

- `POST   /submit`   → submit new job (Excel/CSV, JSON, or both)
- `GET    /status/{job_id}` → status, batch progress, error info
- `GET    /result/{job_id}` → download Excel results
- `GET    /jobs`     → list all jobs

---

## 🔒 Security

- **No authentication** by default (add API keys/proxy if needed)
- All results/logs stored in `./data/jobs` (mount as a volume for persistence in Docker)

---

## 🧑‍💻 Developer Notes

- To add custom fields, change output mapping in `src/worker.py`
- To enable authentication, add a header check in `src/server.py`
- Queue/persistence is SQLite by default (easy to swap for MySQL/Postgres)

---

## 📝 Example Input (JSON)

```json
{
  "query": "https://www.linkedin.com/company/apifytech/",
  "maxDepth": 2,
  "includeSocials": true,
  "summarizeResults": false,
  "inputType": "json"
}
```

---

## 📦 One-command setup

```bash
docker compose up -d
# REST API: http://localhost:8000
```

## 🏗️ Directory Structure

- `src/server.py`          # REST API
- `src/worker.py`          # Worker loop
- `src/database.py`        # SQLite helpers
- `src/queue/redis_queue.py` # Redis queue
- `src/apify_wrapper.py`   # CLI + webhook runner
- `src/batch_scrape_excel.sh` # Bash batch util

---

## License

MIT