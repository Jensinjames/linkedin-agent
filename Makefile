# LinkedIn Agent - Root Makefile
# Provides unified commands for the entire project

.PHONY: help setup-dev setup-prod dev fullstack-dev deploy stop clean status logs backup simple-setup simple-run simple-test

# Default target
help:
	@echo "LinkedIn Agent - Project Management"
	@echo "=================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  setup-dev     - Set up development environment"
	@echo "  setup-prod    - Set up production environment"
	@echo "  simple-setup  - Set up simplified version (minimal dependencies)"
	@echo ""
	@echo "Development Commands:"
	@echo "  dev           - Start backend development environment"
	@echo "  fullstack-dev - Start full stack (backend + frontend)"
	@echo "  frontend-dev  - Start frontend development only"
	@echo "  simple-run    - Run simplified version without external dependencies"
	@echo ""
	@echo "Production Commands:"
	@echo "  deploy        - Deploy to production"
	@echo "  stop          - Stop all services"
	@echo "  clean         - Clean up containers and volumes"
	@echo ""
	@echo "Utility Commands:"
	@echo "  status        - Show service status"
	@echo "  logs          - View service logs"
	@echo "  backup        - Create backup"
	@echo "  backup-verify - Verify latest backup"
	@echo "  backup-cleanup- Clean old backups"
	@echo "  simple-test   - Test simplified version"
	@echo ""
	@echo "Backend Commands:"
	@echo "  backend-build - Build backend Docker image"
	@echo "  backend-test  - Run backend tests"
	@echo "  backend-lint  - Run backend linting"
	@echo ""
	@echo "Frontend Commands:"
	@echo "  frontend-build- Build frontend Docker image"
	@echo "  frontend-test - Run frontend tests"
	@echo "  frontend-lint - Run frontend linting"

# Setup commands
setup-dev:
	@echo "Setting up development environment..."
	cp examples/env.example .env
	mkdir -p storage/data/jobs storage/data/logs
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Development environment ready!"
	@echo "Edit .env with your API keys and run 'make dev'"

setup-prod:
	@echo "Setting up production environment..."
	cp examples/env.example .env
	mkdir -p storage/data/jobs storage/data/logs storage/backups
	@echo "Production environment ready!"
	@echo "Edit .env with your production settings and run 'make deploy'"

# Development commands
dev:
	@echo "Starting backend development environment..."
	cd backend && make dev

fullstack-dev: dev
	@echo "Starting frontend development environment..."
	cd frontend && npm install && npm run dev

frontend-dev:
	@echo "Starting frontend development only..."
	cd frontend && npm install && npm run dev

# Production commands
deploy:
	@echo "Deploying to production..."
	cd infrastructure/docker && docker-compose -f docker-compose.prod.yml up -d

stop:
	@echo "Stopping all services..."
	cd infrastructure/docker && docker-compose down
	cd infrastructure/docker && docker-compose -f docker-compose.prod.yml down

clean:
	@echo "Cleaning up containers and volumes..."
	cd infrastructure/docker && docker-compose down -v
	cd infrastructure/docker && docker-compose -f docker-compose.prod.yml down -v
	docker system prune -f

# Utility commands
status:
	@echo "Service Status:"
	cd infrastructure/docker && docker-compose ps
	@echo ""
	@echo "Redis Info:"
	cd infrastructure/docker && docker-compose exec redis redis-cli info | grep connected_clients || echo "Redis not running"

logs:
	@echo "Viewing service logs..."
	cd infrastructure/docker && docker-compose logs -f

backup:
	@echo "Creating backup..."
	infrastructure/scripts/backup.sh

backup-verify:
	@echo "Verifying backup..."
	infrastructure/scripts/backup.sh --verify

backup-cleanup:
	@echo "Cleaning old backups..."
	infrastructure/scripts/backup.sh --cleanup

# Backend commands
backend-build:
	@echo "Building backend Docker image..."
	cd backend && make build-prod

backend-test:
	@echo "Running backend tests..."
	cd backend && make test

backend-lint:
	@echo "Running backend linting..."
	cd backend && make lint

# Frontend commands
frontend-build:
	@echo "Building frontend Docker image..."
	cd frontend && npm run build

frontend-test:
	@echo "Running frontend tests..."
	cd frontend && npm test

frontend-lint:
	@echo "Running frontend linting..."
	cd frontend && npm run lint

# Simplified version commands
simple-setup:
	@echo "Setting up simplified LinkedIn Agent (minimal dependencies)..."
	./setup_simple.sh

simple-run:
	@echo "Running simplified version..."
	cd backend && python simple_main.py examples/input.json

simple-test:
	@echo "Testing simplified version..."
	cd backend && python -c "import asyncio; from src.adapters.simple_local_adapter import SimpleLocalAdapter; print('✅ Simple adapter works')"
	cd infrastructure/docker && docker-compose -f docker-compose.simple.yml build
	@echo "✅ Simplified version tests passed"

# Health check
health:
	@echo "Checking system health..."
	curl -f http://localhost:8000/health || echo "Health check failed"
