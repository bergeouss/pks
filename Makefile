.PHONY: help dev build test clean logs

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

dev: ## Start development environment
	docker-compose up --build

build: ## Build production images
	docker-compose build

test: ## Run backend tests
	docker-compose exec backend pytest

clean: ## Clean up containers and volumes
	docker-compose down -v

logs: ## Show logs from all services
	docker-compose logs -f

backend-shell: ## Open backend shell
	docker-compose exec backend /bin/bash
