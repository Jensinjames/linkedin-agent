# LinkedIn Agent - AI Coding Agent Instructions

## Architecture Overview

This is a **production-ready LinkedIn scraping system** with clean separation between backend, frontend, and infrastructure. The system supports multiple execution modes: CLI, REST API, queue processing, and Apify platform integration.

### Key Components
- **Backend** (`/backend/src/`): FastAPI REST API + Redis queue workers + SQLite persistence
- **Frontend** (`/frontend/src/`): React admin dashboard with Supabase auth
- **Infrastructure** (`/infrastructure/`): Docker configs, monitoring, deployment scripts
- **Platform Adapters** (`/backend/src/adapters/`): Abstraction layer for Apify vs local execution

## Critical Architecture Patterns

### 1. Platform Adapter Pattern
All external interactions go through adapters implementing `PlatformAdapter` interface:
- `ApifyAdapter`: For Apify platform integration
- `LocalAdapter`: For local/development execution
- `SimpleLocalAdapter`: Minimal dependencies version

This enables the same core logic to run on Apify platform or local infrastructure.

### 2. Multi-Mode Execution
The system has 4 distinct entry points:
- **CLI Mode**: `python -m src.cli input.json` (direct execution)
- **API Mode**: `python src/server.py` (FastAPI REST server)
- **Worker Mode**: `python src/worker.py` (Redis queue consumer)
- **Apify Mode**: `python -m src` (platform integration)

### 3. Queue-Based Processing
Jobs flow through Redis queues with SQLite persistence:
1. REST API accepts uploads → creates job → queues for processing
2. Worker processes queue → updates database → stores results
3. Large Excel files are automatically batched (10K rows/batch)

## Development Workflow Commands

**Never run ad-hoc commands** - always use the project's Makefile:

```bash
# Essential commands
make help              # Show all available commands
make setup-dev         # Initialize development environment
make dev              # Start backend services (API + Worker + Redis)
make fullstack-dev    # Start backend + frontend
make simple-run       # Run minimal version without Redis/external deps

# Backend development
make backend-test     # Run backend tests
make backend-lint     # Run backend linting

# Frontend development  
make frontend-dev     # Start React dev server
make frontend-test    # Run frontend tests

# Production deployment
make setup-prod       # Setup production environment
make deploy          # Deploy with docker-compose.prod.yml
```

## Virtual Environment Setup

**For development without Docker**, use virtual environments:

```bash
# 1. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Linux/Mac
# .venv\Scripts\activate   # On Windows

# 2. Install dependencies
cd backend
pip install -r requirements_simple.txt  # Minimal dependencies
# OR
pip install -r requirements.txt         # Full features

# 3. Run application modes
python simple_main.py ../examples/input.json       # CLI mode
python simple_server.py                            # API server
python -m src.cli ../examples/input.json          # Full CLI mode
python src/server.py                               # Full API server

# 4. Environment setup
cp ../examples/env.example ../.env
# Edit .env with your API keys (OPENAI_API_KEY, etc.)
```

## Data Storage and Output

**All job data automatically saved to structured storage:**

```bash
# Primary storage location
storage/data/
├── jobs/                 # Individual job results
│   └── {job_id}/
│       ├── job_result.json    # Structured output
│       ├── contacts.csv       # CSV export
│       └── summary.txt        # Human-readable summary
├── logs/                 # Application logs
├── exports/             # Batch exports
└── jobs.db             # SQLite database (full mode)
```

**Output Schema:** All responses use structured `JobResult` format with:
- **job_summary**: Metadata (ID, status, timing, counts)
- **contacts**: Array of `ContactInfo` objects with emails, phones, social links
- **statistics**: Aggregated counts and metrics
- **errors**: Structured error information

## Virtual Environment Setup

For development without Docker, use Python virtual environments:

### Quick Setup (Recommended)
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies and setup
make setup-dev
cd backend && pip install -r requirements.txt
```

### Simple Mode (Minimal Dependencies)
```bash
# For development without Redis/Docker
cd backend
pip install -r requirements_simple.txt

# Test the setup
python simple_main.py ../examples/input.json

# Start simple API server
python simple_server.py
```

### Individual Entry Points
```bash
# CLI mode (direct processing)
cd backend && python -m src.cli ../examples/input.json

# API server mode  
cd backend && python src/server.py  # http://localhost:8000

# Worker mode (requires Redis)
cd backend && python src/worker.py
```

## Structured Output and Job Management

### Job Data Storage Structure
All job results are automatically saved in structured formats:

```bash
storage/data/jobs/{job_id}/
├── result.json              # Full structured data (Pydantic schema)
├── result_formatted.json    # Human-readable formatted data
├── contacts.csv             # CSV export of contacts
├── summary.txt              # Plain text summary report
└── metadata.json            # Job metadata only
```

### Output Schema (schemas_output.py)
- **JobResult**: Complete job with metadata, contacts, errors, summary
- **ContactInfo**: Structured contact data with validation
- **JobMetadata**: Job execution details and statistics
- **JobStatus**: Enum for job states (pending, processing, completed, failed)

### Job Management CLI
```bash
# View all jobs with structured output
cd backend && python job_manager.py list

# Show detailed job result
python job_manager.py show {job_id} --format summary

# Export jobs to Excel
python job_manager.py export {job_id1} {job_id2} --output results.xlsx

# Test scraping with structured output
python job_manager.py test "https://linkedin.com/company/example"

# Clean old jobs
python job_manager.py clean --days 30
```

### API Endpoints for Structured Data
```bash
# Submit job and get structured response
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"query": "https://linkedin.com/company/example"}'

# List all jobs with metadata
curl http://localhost:8000/jobs

# Get formatted job result
curl http://localhost:8000/jobs/{job_id}

# Get text summary
curl http://localhost:8000/jobs/{job_id}/summary
```

## File Location Conventions

### Backend Structure
- **Entry points**: `backend/src/{__main__.py, cli.py, server.py, worker.py}`
- **Core logic**: `backend/src/{agent.py, main.py}`
- **Crawling**: `backend/src/crawler/linkedin.py`
- **Data layer**: `backend/src/{database.py, schemas.py}`
- **Platform abstraction**: `backend/src/adapters/`
- **Queue**: `backend/src/queue/redis_queue.py`

### Frontend Structure
- **Components**: `frontend/src/components/` (with Storybook stories)
- **Pages**: `frontend/src/pages/` (Login, Teams, Credits)
- **Auth**: `frontend/src/supabaseClient.ts`

### Configuration
- **Docker**: `infrastructure/docker/docker-compose.{yml,prod.yml,simple.yml}`
- **Environment**: Copy `examples/env.example` to `.env`
- **Input templates**: `examples/{linkedin_template.xlsx, sample_input.xlsx}`

## Data Processing Patterns

### Input Handling
The system accepts multiple input formats via `ActorInput` schema:
- **JSON**: Direct LinkedIn URLs in `query` field
- **CSV**: Set `inputType="csv"` with `csv_urls` array
- **Excel**: Multi-tab support with `Company_Profiles` and `Individual_Profiles` sheets

### Batch Processing Pipeline
For large Excel files:
1. Worker splits into 10K row batches using Polars
2. Each batch processed independently with retry logic
3. Results aggregated back to single output file
4. Database tracks batch status individually

### Storage Structure
```
/app/data/
├── jobs.db          # SQLite job/batch tracking
├── jobs/            # Per-job working directories
│   └── {job_id}/
│       ├── input/   # Original input files
│       ├── batches/ # Split batch files
│       └── output/  # Final results
└── logs/           # Application logs
```

## Integration Points

### Authentication & Authorization
- **Supabase JWT**: All admin endpoints require `Bearer {token}` with `admin` role
- **Role verification**: Use `verify_admin()` dependency in FastAPI routes
- **Frontend auth**: Supabase client handles login/logout/session

### External Services
- **OpenAI**: LLM summarization when `summarizeResults=true`
- **Apify**: LinkedIn crawling via Contact Details Scraper actor
- **Redis**: Queue coordination between API and workers

### Health Monitoring
- `/health` - Full system health with database/Redis connectivity
- `/health/simple` - Basic health check
- `/health/{ready,live}` - Kubernetes probes

## Docker Development

### Multi-Stage Build Pattern
All Dockerfiles use consistent pattern:
1. **deps**: Install Python dependencies
2. **source**: Copy source code + compile
3. **runtime**: Final minimal image

### Volume Mapping
Development containers mount:
- `storage/data:/app/data` - Persistent job data
- `storage:/app/storage:ro` - Read-only storage access

## Common Issues & Solutions

### Environment Setup
- **Missing .env**: Always run `make setup-dev` first
- **Permission errors**: Ensure `storage/` directory is writable
- **Port conflicts**: Default ports are 8000 (API), 6379 (Redis), 3000 (frontend)

### Virtual Environment Issues
- **Import errors**: Ensure you're in activated venv with `source .venv/bin/activate`
- **Missing packages**: Use correct requirements file: `requirements.txt` (full) vs `requirements_simple.txt` (minimal)
- **Redis connection**: For API/Worker modes, either run `docker run -d -p 6379:6379 redis:7-alpine` or use `make dev`

### Excel Processing
- **Template format**: Use `examples/linkedin_template.xlsx` as reference
- **Sheet names**: Must be exactly `Company_Profiles` or `Individual_Profiles`
- **URL column**: Must be named `linkedin_url`

### Queue Processing
- **Stuck jobs**: Check worker logs via `make logs`
- **Redis connectivity**: Verify Redis is running in docker-compose
- **Job status**: Use `/status/{job_id}` endpoint to track progress

## Testing Strategy

- **Backend**: Unit tests in `backend/tests/`
- **Frontend**: Component tests + Storybook stories
- **Integration**: Full stack testing via `make simple-test`
- **Health checks**: Built-in endpoints for monitoring

When modifying the system, always test both CLI and API modes to ensure adapter pattern works correctly across execution environments.
