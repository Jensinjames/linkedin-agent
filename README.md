# 🚀 LinkedIn Agent

> **A powerful LinkedIn scraping agent** that extracts contact information from LinkedIn profiles and company pages using AI-powered automation.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Playwright](https://img.shields.io/badge/Playwright-enabled-orange.svg)](https://playwright.dev)

## ✨ What This Does

- **🎯 Extract Contact Information** from LinkedIn profiles and company pages
- **🤖 AI-Powered Summarization** using OpenAI GPT models
- **📊 Batch Processing** support for Excel/CSV files
- **🔄 Multiple Execution Modes** (CLI, API, Simple)
- **💾 Data Storage** with SQLite and structured job management
- **🌐 Web Scraping** powered by Playwright for reliable automation

## 🚀 Quick Start (5 Minutes Setup)

### Prerequisites
- **Python 3.9+** installed on your system
- **Git** for cloning the repository
- **OpenAI API Key** (optional, for AI summarization)

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/Jensinjames/linkedin-agent.git
cd linkedin-agent

# Run the automated setup (creates .env, directories, installs dependencies)
make setup-dev
```

### 2. Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install all required packages
cd backend
pip install -r requirements.txt

# Install Playwright browsers (required for web scraping)
playwright install
```

### 3. Configure Your Settings

```bash
# Edit the .env file with your API keys (optional)
nano .env
```

**Required settings in `.env`:**
```bash
# Optional: Add your OpenAI API key for AI summarization
OPENAI_API_KEY=your-openai-api-key-here

# Optional: Add Apify token for enhanced proxy support
APIFY_TOKEN=your-apify-token-here
```

### 4. Test Your Setup

```bash
# Test with the example LinkedIn company page
source .venv/bin/activate
cd backend

# Copy example input to accessible location
cp ../examples/input.json ../storage/data/input.json

# Run the scraper
python simple_main.py ../storage/data/input.json
```

✅ **You should see scraped LinkedIn data in JSON format!**

---

## 📁 Project Structure

```
linkedin-agent/
├── 📁 backend/                    # Core LinkedIn scraping engine
│   ├── src/                      # Main Python source code
│   ├── tests/                    # Backend tests
│   ├── requirements.txt          # Python dependencies
│   ├── simple_main.py           # Simple execution mode
│   └── Dockerfile*              # Backend containers
├── 📁 frontend/                  # React admin dashboard
│   ├── src/                     # React components
│   └── package.json             # Frontend dependencies
├── 📁 infrastructure/            # Deployment & DevOps
│   ├── docker/                  # Docker configurations
│   ├── scripts/                 # Utility scripts
│   └── monitoring/              # Monitoring configs
├── 📁 examples/                  # Sample inputs & configs
│   ├── input.json              # Example LinkedIn URL
│   ├── input.csv               # Example CSV batch input
│   └── env.example             # Environment template
├── 📁 storage/                   # Runtime data (auto-created)
│   ├── data/jobs/              # Job results
│   └── data/logs/              # Application logs
├── .env                         # Your API keys (auto-created)
├── Makefile                     # Development commands
└── README.md                    # This file
```

## 🎯 Usage Examples

### Basic Usage: Scrape a LinkedIn Company Page

```bash
# 1. Activate your virtual environment
source .venv/bin/activate
cd backend

# 2. Create input file with LinkedIn URL
echo '{
  "query": "https://www.linkedin.com/company/microsoft/",
  "maxDepth": 2,
  "includeSocials": true
}' > ../storage/data/my_input.json

# 3. Run the scraper
python simple_main.py ../storage/data/my_input.json
```

**Expected Output:**
```json
{
  "url": "https://www.linkedin.com/company/microsoft/",
  "contacts": [
    {
      "name": "Microsoft",
      "title": "Microsoft | LinkedIn",
      "company": null,
      "location": "Redmond, Washington",
      "emails": [],
      "phones": [],
      "social_links": {
        "linkedin.com": "https://www.linkedin.com/company/microsoft/"
      },
      "linkedin_url": "https://www.linkedin.com/company/microsoft/",
      "website": "https://www.microsoft.com",
      "description": "Microsoft is a technology company..."
    }
  ]
}
```

### Batch Processing with CSV Files

```bash
# 1. Create a CSV file with multiple LinkedIn URLs
echo "linkedin_url,company_name
https://www.linkedin.com/company/microsoft/,Microsoft
https://www.linkedin.com/company/google/,Google" > ../storage/data/companies.csv

# 2. Process the batch (requires additional setup)
cd backend
python -m src.cli ../storage/data/companies.csv
```

### API Mode (Advanced)

```bash
# 1. Start the API server (requires Redis)
cd backend
python src/server.py

# 2. In another terminal, submit a job
curl -X POST "http://localhost:8000/submit" \
  -F "owner_email=you@example.com" \
  -F "input_file=@../examples/input.json"

# 3. Check job status
curl "http://localhost:8000/status/{job_id}"
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

#### Excel Templates

For Excel batch processing, use the provided templates:

- **`examples/linkedin_template.xlsx`** - Empty template with correct structure
- **`examples/sample_input.xlsx`** - Example data showing proper format

Excel files must have tabs named:

- `Company_Profiles` - For LinkedIn company pages
- `Individual_Profiles` - For LinkedIn personal profiles

See `docs/EXCEL_FORMAT.md` for detailed format requirements.

See `examples/` directory for sample inputs.

## 🚦 Usage Examples

The LinkedIn Agent supports multiple execution modes depending on your needs:

### Execution Modes

1. ** CLI Mode
** (Direct execution)
```bash
cd backend
python -m src.cli ../examples/input.json
```

2. **API Mode** (REST server)
```bash
cd backend
python src/server.py  # Requires Redis running
```

3. **Worker Mode** (Queue processing)
```bash
cd backend
python src/worker.py  # Requires Redis running
```

4. **Simple Mode** (No external dependencies)
```bash
cd backend
python simple_main.py ../examples/input.json
```### REST API
Examples
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

# Enhanced processor with multi-tab support and URL validation
./src/batch_scrape_excel_enhanced.sh ../examples/sample_input.xlsx ../examples/input.json

# Legacy processor (single sheet only)
./src/batch_scrape_excel.sh ../examples/sample_input.xlsx ../examples/input.json
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
# Setup development environment (FIRST TIME ONLY)
# This installs all dependencies and creates .env file
make setup-dev

# Edit .env with your API keys (REQUIRED)
nano .env

# Start development services
make dev

# Make changes in backend/src/ or frontend/src/

# Test your changes
make backend-test
make frontend-test

# Format code
make backend-lint
make frontend-lint

# Start frontend development server (optional, in new terminal)
make frontend-dev

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

This restructured project makes development, deployment, and maintenance much easier. The separation of concerns and
clear documentation will help you get up and running quickly.
