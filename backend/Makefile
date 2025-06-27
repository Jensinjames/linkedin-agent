# Backend Makefile
# Handles all backend operations for the LinkedIn Agent

.PHONY: help dev build-dev build-prod build-apify test lint type-check clean run

# Default target
help:
	@echo "Backend Commands:"
	@echo "================="
	@echo ""
	@echo "Development:"
	@echo "  dev         - Start development environment"
	@echo "  run         - Run locally with Python"
	@echo ""
	@echo "Building:"
	@echo "  build-dev   - Build development Docker image"
	@echo "  build-prod  - Build production Docker image"
	@echo "  build-apify - Build Apify platform image"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  test        - Run tests"
	@echo "  lint        - Run code formatting"
	@echo "  type-check  - Run type checking"
	@echo ""
	@echo "Utilities:"
	@echo "  clean       - Clean build artifacts"

# Development
dev:
	@echo "Starting backend development environment..."
	mkdir -p ../storage/data/jobs ../storage/data/logs
	cd ../infrastructure/docker && docker-compose up -d

run:
	@echo "Running backend locally..."
	python3 -m src.cli ../examples/input.json

# Building
build-dev:
	@echo "Building development Docker image..."
	docker build -f Dockerfile.dev -t linkedin-agent-backend:dev .

build-prod:
	@echo "Building production Docker image..."
	docker build -f Dockerfile.prod -t linkedin-agent-backend:prod .

build-apify:
	@echo "Building Apify platform image..."
	docker build -f Dockerfile -t linkedin-agent-backend:apify .

# Testing & Quality
test:
	@echo "Running backend tests..."
	python -m pytest tests/ -v

lint:
	@echo "Running code formatting..."
	black src/ tests/
	isort src/ tests/

type-check:
	@echo "Running type checking..."
	mypy src/

# Utilities
clean:
	@echo "Cleaning build artifacts..."
	docker rmi linkedin-agent-backend:dev linkedin-agent-backend:prod linkedin-agent-backend:apify 2>/dev/null || true
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true