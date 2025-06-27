# 🚀 LinkedIn Agent - Clean Architecture

A production-ready LinkedIn scraping agent with a clean, organized architecture. This project has been restructured for better maintainability, scalability, and developer experience.

## 🏗️ Project Structure

```
linkedin-agent/
├── 📁 backend/                    # Core LinkedIn scraping engine
│   ├── src/                      # Main Python source code
│   ├── tests/                    # Backend tests
│   ├── requirements.txt          # Python dependencies
│   └── Dockerfile*              # Backend containers
├── 📁 frontend/                  # React admin dashboard
│   ├── src/                     # React components
│   └── package.json             # Frontend dependencies
├── 📁 infrastructure/            # Deployment & DevOps
│   ├── docker/                  # Docker configurations
│   ├── scripts/                 # Utility scripts
│   └── monitoring/              # Monitoring configs
├── 📁 docs/                      # Documentation
├── 📁 examples/                  # Sample inputs & configs
└── 📁 storage/                   # Runtime data (gitignored)
```

## 🚀 Quick Start

### 1. Setup Development Environment

```bash
# Clone and setup
git clone <your-repo>
cd linkedin-agent
make setup-dev

# Edit environment variables
nano .env  # Add your API keys

# Start development
make dev
```

### 2. Setup Production Environment

```bash
# Setup production
make setup-prod

# Edit production settings
nano .env

# Deploy
make deploy
```

## ✨ Key Features

- **🎯 Clean Architecture**: Separated backend, frontend, and infrastructure
- **🐳 Docker-First**: Multi-stage builds with development and production configs
- **📊 Queue Processing**: Redis-based job queue with worker processes
- **🔒 Security**: JWT authentication and role-based access
- **📈 Monitoring**: Health checks and Prometheus integration
- **💾 Persistent Storage**: SQLite database with backup automation
- **🔄 Batch Processing**: Excel/CSV input with resumable processing
- **🎨 Modern UI**: React-based admin dashboard

## 🛠️ Development Commands

```bash
# Show all available commands
make help

# Backend development
make dev                    # Start backend services
make backend-test          # Run backend tests
make backend-lint          # Run backend linting

# Frontend development
make frontend-dev          # Start frontend development
make frontend-test         # Run frontend tests
make frontend-lint         # Run frontend linting

# Full stack development
make fullstack-dev         # Start both backend and frontend

# Production
make deploy                # Deploy to production
make stop                  # Stop all services
make clean                 # Clean up containers

# Utilities
make status                # Check service status
make logs                  # View service logs
make backup                # Create backup
make health                # Health check
```

## 📚 Documentation

- **[Project Structure](PROJECT_STRUCTURE.md)** - Detailed structure guide
- **[Architecture](docs/ARCHITECTURE.md)** - System design and components
- **[API Documentation](docs/API.md)** - REST API reference
- **[Deployment](docs/DEPLOYMENT.md)** - Production deployment guide
- **[Development](docs/DEVELOPMENT.md)** - Development workflow

## 🔧 Configuration

### Environment Variables

Copy the example environment file and configure:

```bash
cp examples/env.example .env
```

Key variables:
- `OPENAI_API_KEY` - OpenAI API key for LLM features
- `APIFY_TOKEN` - Apify token for proxy and platform features
- `SUPABASE_JWT_SECRET` - JWT secret for authentication

### Input Formats

The system supports multiple input formats:

1. **JSON Input**: Direct LinkedIn URLs
2. **CSV/Excel**: Batch processing with LinkedIn URLs
3. **REST API**: Programmatic job submission

See `examples/` directory for sample inputs.

## 🚦 Usage Examples

### CLI Mode
```bash
cd backend
python -m src.cli ../examples/input.json
```

### REST API
```bash
# Submit job
curl -F "owner_email=user@example.com" \
     -F "input_file=@examples/input.csv" \
     http://localhost:8000/submit

# Check status
curl http://localhost:8000/status/1

# Download results
curl -OJ http://localhost:8000/result/1
```

### Batch Processing
```bash
cd backend
./batch_scrape_excel.sh ../examples/input.xlsx
```

## 🏗️ Architecture Overview

### Backend Components
- **API Server**: FastAPI REST API for job management
- **Worker**: Queue processing with Redis
- **Crawler**: Playwright-based LinkedIn scraping
- **Database**: SQLite for job persistence
- **Agent**: LLM orchestration for summarization

### Frontend Components
- **Admin Dashboard**: React-based management interface
- **Authentication**: Supabase-based auth with role management
- **Real-time Updates**: WebSocket integration for job status

### Infrastructure
- **Docker**: Multi-stage builds for development and production
- **Monitoring**: Prometheus and health checks
- **Backup**: Automated backup system
- **CI/CD**: Ready for pipeline integration

## 🔒 Security

- **Authentication**: JWT-based authentication with Supabase
- **Authorization**: Role-based access control (admin/user)
- **Input Validation**: Comprehensive input sanitization
- **Container Security**: Non-root user execution
- **Network Security**: Internal service communication

## 📊 Monitoring & Health

### Health Endpoints
- `/health` - Full system health check
- `/health/simple` - Simple health check
- `/health/ready` - Kubernetes readiness probe
- `/health/live` - Kubernetes liveness probe

### Monitoring
- **Prometheus**: Metrics collection
- **Grafana**: Dashboard (optional)
- **Logs**: Structured logging with rotation

## 🚀 Deployment

### Development
```bash
make setup-dev
make dev
```

### Production
```bash
make setup-prod
make deploy
```

### Docker Compose
```bash
# Development
cd infrastructure/docker
docker-compose up -d

# Production
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

### Development Workflow
```bash
# Setup development environment
make setup-dev

# Make changes in backend/src/ or frontend/src/

# Test your changes
make backend-test
make frontend-test

# Format code
make backend-lint
make frontend-lint

# Commit and push
git add .
git commit -m "feat: your feature description"
git push origin feature/your-feature
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `docs/` directory
- **Examples**: See `examples/` directory for usage examples
- **Issues**: Report bugs and feature requests via GitHub issues

---

**🎉 Welcome to the clean, organized LinkedIn Agent!** 

This restructured project makes development, deployment, and maintenance much easier. The separation of concerns and clear documentation will help you get up and running quickly.