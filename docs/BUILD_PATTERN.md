# Build Pattern: Source Code, Docker, and Storage Integration

## Overview

This document outlines the enhanced build pattern for the LinkedIn Agent project, focusing on the relationships between source code, Docker containers, and persistent storage. The pattern supports multiple deployment scenarios: local development, production queue processing, and Apify platform integration.

## Architecture Components

### 1. Source Code Organization

```
src/
├── __main__.py          # Apify platform entry point
├── cli.py              # Local CLI entry point  
├── server.py           # FastAPI REST API
├── worker.py           # Queue worker process
├── agent.py            # LLM orchestration
├── crawler/
│   └── linkedin.py     # Playwright-based scraping
├── adapters/
│   ├── base.py         # Platform abstraction interface
│   ├── apify_adapter.py # Apify platform adapter
│   └── local_adapter.py # Local development adapter
├── database.py         # SQLite job persistence
└── queue/
    └── redis_queue.py  # Redis queue abstraction
```

### 2. Docker Build Strategy

#### Multi-Stage Build Pattern

```dockerfile
# Stage 1: Dependencies
FROM apify/actor-python:3.13 as deps
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Stage 2: Source Code
FROM apify/actor-python:3.13 as source
COPY --from=deps /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY src/ ./src/
COPY requirements.txt ./
RUN python3 -m compileall -q src/

# Stage 3: Runtime
FROM apify/actor-python:3.13 as runtime
COPY --from=source /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=source /app/src /app/src
COPY --from=source /app/requirements.txt /app/requirements.txt

# Create storage directories
RUN mkdir -p /app/data/jobs /app/storage
RUN useradd --create-home apify && chown -R apify:apify /app
USER apify
```

#### Build Optimization

1. **Layer Caching**: Dependencies installed first, source code copied last
2. **Multi-Stage**: Separate stages for deps, source, and runtime
3. **Compilation**: Python bytecode compilation for performance
4. **Security**: Non-root user execution

### 3. Storage Integration Pattern

#### Persistent Storage Structure

```
/app/
├── data/                    # Runtime data (mounted volume)
│   ├── jobs.db             # SQLite database
│   ├── jobs/               # Job files and results
│   │   ├── job_1/
│   │   │   ├── batches/    # Input batch files
│   │   │   └── outputs/    # Batch results
│   │   └── job_1_final.xlsx # Final merged result
│   └── logs/               # Application logs
└── storage/                # Apify platform storage
    └── key_value_stores/   # Platform-specific storage
```

#### Volume Mount Strategy

```yaml
# docker-compose.yml
volumes:
  - ./data:/app/data:rw        # Runtime data persistence
  - ./storage:/app/storage:ro  # Platform storage (read-only)
  - redis_data:/var/lib/redis  # Redis persistence
```

### 4. Environment-Specific Builds

#### Development Build

```dockerfile
# Dockerfile.dev
FROM apify/actor-python:3.13

# Install development dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install -r requirements.txt -r requirements-dev.txt

# Copy source with hot-reload support
COPY src/ ./src/
COPY .env.example .env

# Development entry point
CMD ["python", "-m", "src.cli", "input.json"]
```

#### Production Build

```dockerfile
# Dockerfile.prod
FROM apify/actor-python:3.13 as builder

# Multi-stage build for production
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY src/ ./src/
RUN python3 -m compileall -q src/

# Runtime stage
FROM apify/actor-python:3.13-slim
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /app/src /app/src

# Production entry point
CMD ["python", "src/server.py"]
```

### 5. Build Automation Pattern

#### Makefile Integration

```makefile
.PHONY: build-dev build-prod build-apify deploy

# Development build
build-dev:
	docker build -f Dockerfile.dev -t linkedin-agent:dev .

# Production build  
build-prod:
	docker build -f Dockerfile.prod -t linkedin-agent:prod .

# Apify platform build
build-apify:
	docker build -f Dockerfile -t linkedin-agent:apify .

# Deploy with storage setup
deploy: build-prod
	mkdir -p data/jobs data/logs storage
	docker-compose up -d

# Clean storage
clean-storage:
	rm -rf data/jobs/* data/logs/* storage/*
```

#### CI/CD Pipeline

```yaml
# .github/workflows/build.yml
name: Build and Deploy

on:
  push:
    branches: [main, develop]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: |
          docker build -f Dockerfile.prod -t linkedin-agent:${{ github.sha }} .
          
      - name: Run tests
        run: |
          docker run --rm linkedin-agent:${{ github.sha }} python -m pytest tests/
          
      - name: Deploy to staging
        if: github.ref == 'refs/heads/develop'
        run: |
          # Deploy to staging environment
          
      - name: Deploy to production  
        if: github.ref == 'refs/heads/main'
        run: |
          # Deploy to production environment
```

### 6. Storage Migration and Backup

#### Database Migration Pattern

```python
# src/database/migrations.py
import sqlite3
import os
from pathlib import Path

class DatabaseMigrator:
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def migrate(self):
        """Run database migrations"""
        conn = sqlite3.connect(self.db_path)
        
        # Migration 1: Add new columns
        conn.execute("""
            ALTER TABLE jobs ADD COLUMN priority INTEGER DEFAULT 0;
        """)
        
        # Migration 2: Create indexes
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
        """)
        
        conn.commit()
        conn.close()
```

#### Backup Strategy

```bash
#!/bin/bash
# scripts/backup.sh

BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup SQLite database
cp data/jobs.db "$BACKUP_DIR/"

# Backup job files
tar -czf "$BACKUP_DIR/jobs.tar.gz" data/jobs/

# Backup Redis data (if needed)
docker exec linkedin-agent-redis redis-cli BGSAVE
cp /var/lib/docker/volumes/linkedin-agent_redis_data/_data/dump.rdb "$BACKUP_DIR/"

echo "Backup completed: $BACKUP_DIR"
```

### 7. Monitoring and Observability

#### Health Check Pattern

```python
# src/health.py
from fastapi import APIRouter
import sqlite3
import redis
import os

router = APIRouter()

@router.get("/health")
async def health_check():
    """Comprehensive health check"""
    status = {
        "status": "healthy",
        "components": {}
    }
    
    # Database health
    try:
        conn = sqlite3.connect(os.environ.get("SQLITE_PATH"))
        conn.execute("SELECT 1")
        status["components"]["database"] = "healthy"
    except Exception as e:
        status["components"]["database"] = f"unhealthy: {e}"
        status["status"] = "degraded"
    
    # Redis health
    try:
        r = redis.from_url(os.environ.get("REDIS_URL"))
        r.ping()
        status["components"]["redis"] = "healthy"
    except Exception as e:
        status["components"]["redis"] = f"unhealthy: {e}"
        status["status"] = "degraded"
    
    # Storage health
    jobs_dir = os.environ.get("JOBS_DIR")
    if os.path.exists(jobs_dir) and os.access(jobs_dir, os.W_OK):
        status["components"]["storage"] = "healthy"
    else:
        status["components"]["storage"] = "unhealthy"
        status["status"] = "degraded"
    
    return status
```

### 8. Security Considerations

#### Container Security

```dockerfile
# Security enhancements
FROM apify/actor-python:3.13-slim

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Set proper permissions
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Security scanning
RUN pip install safety
RUN safety check
```

#### Storage Security

```python
# src/security.py
import os
from pathlib import Path

def secure_file_path(file_path: str, base_dir: str) -> bool:
    """Validate file path is within allowed directory"""
    try:
        file_path = os.path.abspath(file_path)
        base_dir = os.path.abspath(base_dir)
        return file_path.startswith(base_dir)
    except Exception:
        return False

def sanitize_filename(filename: str) -> str:
    """Remove potentially dangerous characters from filename"""
    return "".join(c for c in filename if c.isalnum() or c in "._-")
```

## Implementation Checklist

### Phase 1: Foundation
- [ ] Implement multi-stage Docker builds
- [ ] Set up persistent storage volumes
- [ ] Create environment-specific configurations
- [ ] Implement health checks

### Phase 2: Automation
- [ ] Set up CI/CD pipeline
- [ ] Implement automated testing
- [ ] Create backup and restore procedures
- [ ] Add monitoring and logging

### Phase 3: Optimization
- [ ] Optimize Docker layer caching
- [ ] Implement database migrations
- [ ] Add security hardening
- [ ] Performance tuning

### Phase 4: Production
- [ ] Deploy to staging environment
- [ ] Load testing and optimization
- [ ] Production deployment
- [ ] Monitoring and alerting setup

## Best Practices

1. **Immutable Infrastructure**: Use tagged Docker images for deployments
2. **Configuration Management**: Use environment variables for configuration
3. **Security First**: Run containers as non-root users
4. **Monitoring**: Implement comprehensive health checks
5. **Backup Strategy**: Regular automated backups of persistent data
6. **Documentation**: Keep build and deployment procedures documented
7. **Testing**: Automated testing at every stage of the build process