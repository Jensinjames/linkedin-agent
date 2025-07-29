# LinkedIn Agent - Project Structure Guide

## 🏗️ Clean Architecture Overview

This project has been reorganized for better maintainability and clarity. Here's the new structure:

```
linkedin-agent/
├── 📁 backend/                    # Core LinkedIn scraping engine
│   ├── src/                      # Main Python source code
│   ├── tests/                    # Backend tests
│   ├── requirements.txt          # Python dependencies
│   └── Dockerfile               # Backend container
├── 📁 frontend/                  # React admin dashboard
│   ├── src/                     # React components
│   ├── package.json             # Frontend dependencies
│   └── Dockerfile               # Frontend container
├── 📁 infrastructure/            # Deployment & DevOps
│   ├── docker/                  # Docker configurations
│   ├── scripts/                 # Utility scripts
│   └── monitoring/              # Monitoring configs
├── 📁 docs/                      # Documentation
├── 📁 examples/                  # Sample inputs & configs
└── 📁 storage/                   # Runtime data (gitignored)
```

## 🚀 Quick Start

### Development

```bash
# Backend only
cd backend && make dev

# Full stack (backend + frontend)
make fullstack-dev

# Production
make deploy
```

### Key Commands

```bash
make help              # Show all available commands
make status            # Check service status
make logs              # View logs
make backup            # Create backup
```

## 📁 Directory Details

### Backend (`/backend`)

The core LinkedIn scraping engine with multiple entry points:

- **CLI Mode**: `python -m src.cli input.json`
- **API Mode**: FastAPI REST server
- **Worker Mode**: Queue processing
- **Apify Mode**: Platform integration

### Frontend (`/frontend`)

React-based admin dashboard for:

- Job management
- Team administration
- Credit tracking
- Real-time monitoring

### Infrastructure (`/infrastructure`)

All deployment and operational concerns:

- Docker configurations
- Backup scripts
- Monitoring setup
- CI/CD pipelines

### Examples (`/examples`)

Sample configurations and inputs:

- Input JSON templates
- CSV/Excel examples
- Environment configurations

## 🔄 Migration Guide

### From Old Structure

If you're coming from the old structure:

1. **Backend code**: Moved from `/src` to `/backend/src`
2. **Docker files**: Consolidated in `/infrastructure/docker`
3. **Scripts**: Organized in `/infrastructure/scripts`
4. **Examples**: Moved to `/examples`

### Environment Setup

```bash
# Copy example environment
cp examples/env.example .env

# Set up development
make setup-dev

# Start services
make dev
```

## 🎯 Project Goals

This reorganization achieves:

1. **Separation of Concerns**: Backend, frontend, and infrastructure are clearly separated
2. **Scalability**: Easy to add new services or components
3. **Maintainability**: Clear structure makes it easy to find and modify code
4. **Deployment**: Infrastructure is isolated and reusable
5. **Documentation**: Each component has its own documentation

## 📚 Documentation Structure

- `docs/ARCHITECTURE.md` - System design and components
- `docs/API.md` - API documentation
- `docs/DEPLOYMENT.md` - Deployment guides
- `docs/DEVELOPMENT.md` - Development workflow
- `examples/` - Sample configurations and inputs

## 🔧 Development Workflow

1. **Backend Development**: Work in `/backend/src`
2. **Frontend Development**: Work in `/frontend/src`
3. **Infrastructure Changes**: Modify `/infrastructure`
4. **Testing**: Use `make test` in respective directories
5. **Deployment**: Use `make deploy` for production

This structure makes the project much more manageable and professional!