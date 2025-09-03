# Makefile for managing different environments

.PHONY: dev staging prod build clean test logs shell-backend shell-frontend

# Development (explicit)
dev:
	@echo "🚀 Starting development environment..."
	docker compose -f docker-compose.yaml -f docker-compose.dev.yaml --env-file .env.dev up --build

dev-detached:
	@echo "🚀 Starting development environment (detached)..."
	docker compose -f docker-compose.yaml -f docker-compose.dev.yaml --env-file .env.dev up --build -d

# Staging
staging:
	@echo "🧪 Starting staging environment..."
	docker compose -f docker-compose.yaml --env-file .env.staging up --build

# Production
prod:
	@echo "🏭 Starting production environment..."
	docker compose -f docker-compose.yaml -f docker-compose.prod.yaml --env-file .env.prod up --build

prod-detached:
	@echo "🏭 Starting production environment (detached)..."
	docker compose -f docker-compose.yaml -f docker-compose.prod.yaml --env-file .env.prod up --build -d

# Build all services
build:
	docker compose build

build-dev:
	docker compose -f docker-compose.yaml -f docker-compose.dev.yaml build

build-prod:
	docker compose -f docker-compose.yaml -f docker-compose.prod.yaml build

# Clean up
clean:
	@echo "🧹 Cleaning up containers and volumes..."
	docker compose -f docker-compose.yaml -f docker-compose.dev.yaml down -v --remove-orphans
	docker compose -f docker-compose.yaml -f docker-compose.prod.yaml down -v --remove-orphans
	docker system prune -f

# Stop services
stop:
	docker compose down

stop-dev:
	docker compose -f docker-compose.yaml -f docker-compose.dev.yaml down

stop-prod:
	docker compose -f docker-compose.yaml -f docker-compose.prod.yaml down

# View logs
logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f backend

logs-frontend:
	docker compose logs -f frontend

# Shell access (development)
shell-backend:
	docker compose -f docker-compose.yaml -f docker-compose.dev.yaml exec backend /bin/sh

shell-frontend:
	docker compose -f docker-compose.yaml -f docker-compose.dev.yaml exec frontend /bin/sh

# Database operations
db-migrate:
	docker compose -f docker-compose.yaml -f docker-compose.dev.yaml exec backend alembic upgrade head

db-shell:
	docker compose exec postgres psql -U ${DB_USER} -d ${DB_NAME}

# Testing
test:
	docker compose -f docker-compose.yaml -f docker-compose.dev.yaml exec backend python -m pytest

# Health check
health:
	@echo "🏥 Checking service health..."
	@curl -f http://localhost:8000/health || echo "Backend unhealthy"
	@curl -f http://localhost:3000/ || echo "Frontend unhealthy"

# Help
help:
	@echo "Available commands:"
	@echo "  dev          - Start development environment"
	@echo "  staging      - Start staging environment"
	@echo "  prod         - Start production environment"
	@echo "  build        - Build all images"
	@echo "  clean        - Clean up containers and images"
	@echo "  logs         - View logs"
	@echo "  shell-*      - Access container shell"
	@echo "  test         - Run tests"
	@echo "  health       - Check service health"