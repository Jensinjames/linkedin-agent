# Build Pattern & Storage Integration Guide

This guide explains the enhanced build pattern for the LinkedIn Agent project, covering Docker optimization, storage strategies, and deployment patterns.

## Quick Start

### Development Environment
```bash
# Build and run development environment
make dev

# Or manually:
make build-dev
docker-compose up -d
```

### Production Environment
```bash
# Build and deploy production environment
make deploy

# Or manually:
make build-prod
docker-compose -f docker-compose.prod.yml up -d
```

## Architecture Overview

### Source Code Structure
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
├── health.py           # Health check endpoints
└── queue/
    └── redis_queue.py  # Redis queue abstraction
```

### Storage Architecture
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

## Docker Build Strategy

### Multi-Stage Build Pattern

The project uses a multi-stage Docker build for optimal performance and security:

1. **Dependencies Stage**: Install Python packages
2. **Builder Stage**: Compile source code and create bytecode
3. **Runtime Stage**: Create minimal runtime image with compiled code

### Build Commands

```bash
# Development build (with debugging tools)
make build-dev

# Production build (optimized)
make build-prod

# Apify platform build (original)
make build-apify
```

### Build Optimization Features

- **Layer Caching**: Dependencies installed first for better caching
- **Multi-Stage**: Separate stages for deps, source, and runtime
- **Bytecode Compilation**: Python bytecode compilation for performance
- **Security**: Non-root user execution
- **Health Checks**: Built-in health check endpoints

## Storage Integration

### Persistent Storage

The application uses a layered storage approach:

1. **Runtime Data** (`./data/`): Job files, database, logs
2. **Platform Storage** (`./storage/`): Apify-specific storage (read-only)
3. **Redis Data**: Queue persistence via Docker volumes

### Volume Mounts

```yaml
volumes:
  - ./data:/app/data:rw        # Runtime data persistence
  - ./storage:/app/storage:ro  # Platform storage (read-only)
  - redis_data:/var/lib/redis  # Redis persistence
```

### Storage Operations

```bash
# Clean storage
make clean-storage

# Backup all data
make backup

# Verify backup integrity
make backup-verify

# Clean old backups
make backup-cleanup
```

## Environment-Specific Configurations

### Development Environment

**File**: `Dockerfile.dev`
- Includes debugging tools (pytest, black, isort, mypy)
- Hot-reload support
- Development entry point
- Exposed ports for debugging

**Usage**:
```bash
make dev
# Access API at http://localhost:8000
# Access logs: make logs
```

### Production Environment

**File**: `Dockerfile.prod`
- Multi-stage build for minimal image size
- Compiled bytecode for performance
- Security hardening (non-root user)
- Health checks and monitoring

**File**: `docker-compose.prod.yml`
- Multiple worker replicas
- Redis persistence
- Monitoring with Prometheus
- Health checks and restart policies

**Usage**:
```bash
make deploy
# Production API at http://localhost:8000
# Monitoring at http://localhost:9090
```

## Health Monitoring

### Health Check Endpoints

The application provides comprehensive health monitoring:

- `/health` - Full system health check
- `/health/simple` - Simple health check for load balancers
- `/health/ready` - Kubernetes readiness probe
- `/health/live` - Kubernetes liveness probe

### Health Check Components

1. **Database**: SQLite connectivity and table structure
2. **Redis**: Connection and queue status
3. **Storage**: File system access and disk space
4. **Environment**: Required environment variables

### Usage

```bash
# Check system health
make health

# Or manually:
curl http://localhost:8000/health
```

## Backup and Recovery

### Backup Strategy

The backup system handles:

1. **SQLite Database**: Binary copy + SQL dump
2. **Job Files**: Compressed tar archive
3. **Redis Data**: RDB dump file
4. **Storage Directory**: Platform storage backup
5. **Manifest**: Backup metadata and verification

### Backup Commands

```bash
# Create backup
make backup

# Verify latest backup
make backup-verify

# Clean old backups (older than 30 days)
make backup-cleanup
```

### Backup Structure

```
backups/
├── 20241201_143022/          # Timestamped backup
│   ├── jobs.db              # SQLite database
│   ├── jobs.sql             # SQL dump
│   ├── jobs.tar.gz          # Job files
│   ├── redis_dump.rdb       # Redis data
│   ├── storage.tar.gz       # Platform storage
│   ├── manifest.txt         # Backup metadata
│   └── backup.log           # Backup log
└── latest -> 20241201_143022 # Symlink to latest
```

## Development Workflow

### Local Development

```bash
# Setup development environment
make install

# Run locally
make run

# Or with Docker
make dev
```

### Testing

```bash
# Run tests
make test

# Code formatting
make lint

# Type checking
make type-check
```

### Logging and Monitoring

```bash
# View all logs
make logs

# View specific service logs
make logs-api
make logs-worker

# Check service status
make status
```

## Production Deployment

### Deployment Checklist

1. **Environment Variables**: Set required environment variables
2. **Storage Setup**: Create necessary directories
3. **Build**: Create production Docker image
4. **Deploy**: Start production services
5. **Verify**: Check health endpoints
6. **Monitor**: Set up monitoring and alerting

### Environment Variables

Required environment variables (see `.env.example`):

```bash
# API Keys
OPENAI_API_KEY=your-openai-api-key
APIFY_TOKEN=your-apify-token

# Security
SUPABASE_JWT_SECRET=your-jwt-secret

# Storage
SQLITE_PATH=/app/data/jobs.db
JOBS_DIR=/app/data/jobs

# Redis
REDIS_URL=redis://redis:6379/0
```

### Deployment Commands

```bash
# Full production deployment
make deploy

# Stop production services
make stop-prod

# Clean up everything
make clean
```

## Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure storage directories have correct permissions
2. **Health Check Failures**: Check environment variables and service connectivity
3. **Backup Failures**: Verify Docker containers are running for Redis backup
4. **Build Failures**: Check Docker daemon and available disk space

### Debug Commands

```bash
# Check container status
docker-compose ps

# View service logs
make logs

# Check health endpoints
make health

# Verify backup integrity
make backup-verify
```

### Performance Optimization

1. **Docker Layer Caching**: Rebuild only when necessary
2. **Multi-Stage Builds**: Minimize final image size
3. **Bytecode Compilation**: Improve Python performance
4. **Volume Optimization**: Use appropriate volume mounts

## Security Considerations

### Container Security

- Non-root user execution
- Minimal runtime image
- Security scanning with safety
- Regular base image updates

### Storage Security

- Path validation for file operations
- Filename sanitization
- Read-only mounts where appropriate
- Backup encryption (implement as needed)

### Network Security

- Internal service communication
- Health check endpoints
- Authentication required for API endpoints
- CORS configuration for production

## Best Practices

1. **Immutable Infrastructure**: Use tagged Docker images
2. **Configuration Management**: Environment variables for configuration
3. **Security First**: Non-root users and minimal privileges
4. **Monitoring**: Comprehensive health checks
5. **Backup Strategy**: Regular automated backups
6. **Documentation**: Keep procedures documented
7. **Testing**: Automated testing at every stage

## Next Steps

### Phase 1: Foundation ✅
- [x] Multi-stage Docker builds
- [x] Persistent storage volumes
- [x] Environment-specific configurations
- [x] Health checks

### Phase 2: Automation
- [ ] CI/CD pipeline setup
- [ ] Automated testing integration
- [ ] Backup automation
- [ ] Monitoring and alerting

### Phase 3: Optimization
- [ ] Docker layer caching optimization
- [ ] Database migration system
- [ ] Security hardening
- [ ] Performance tuning

### Phase 4: Production
- [ ] Staging environment deployment
- [ ] Load testing
- [ ] Production deployment
- [ ] Monitoring and alerting setup