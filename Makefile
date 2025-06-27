.PHONY: install run build-dev build-prod build-apify deploy clean-storage backup test health

# Development setup
install:
	./setup.sh

# Local development run
run:
	python3 -m src.cli input.json

# Docker builds
build-dev:
	docker build -f Dockerfile.dev -t linkedin-agent:dev .

build-prod:
	docker build -f Dockerfile.prod -t linkedin-agent:prod .

build-apify:
	docker build -f Dockerfile -t linkedin-agent:apify .

# Development environment
dev: build-dev
	mkdir -p data/jobs data/logs storage
	docker-compose up -d

# Production deployment
deploy: build-prod
	mkdir -p data/jobs data/logs storage backups
	docker-compose -f docker-compose.prod.yml up -d

# Clean storage directories
clean-storage:
	rm -rf data/jobs/* data/logs/* storage/*
	@echo "Storage cleaned"

# Backup operations
backup:
	./scripts/backup.sh

backup-verify:
	./scripts/backup.sh --verify

backup-cleanup:
	./scripts/backup.sh --cleanup

# Testing
test:
	python -m pytest tests/ -v

# Health checks
health:
	curl -f http://localhost:8000/health || echo "Health check failed"

# Development tools
lint:
	black src/ tests/
	isort src/ tests/

type-check:
	mypy src/

# Utility commands
logs:
	docker-compose logs -f

logs-api:
	docker-compose logs -f api

logs-worker:
	docker-compose logs -f worker

# Stop all services
stop:
	docker-compose down

stop-prod:
	docker-compose -f docker-compose.prod.yml down

# Remove all containers and volumes
clean:
	docker-compose down -v
	docker system prune -f

# Show status
status:
	docker-compose ps
	docker-compose exec redis redis-cli info | grep connected_clients
