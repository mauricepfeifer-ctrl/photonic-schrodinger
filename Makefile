.PHONY: help install lint test run-launch run-nucleus run-swarm docker-up docker-down clean

PYTHON := python3
PIP := pip

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	$(PIP) install -r requirements.txt
	pre-commit install

lint: ## Run linting with Ruff
	ruff check .

test: ## Run tests with Pytest
	pytest tests/ -v

run-launch: ## Run the full Empire Launch
	$(PYTHON) empire_launch.py

run-nucleus: ## Run the Nucleus (Autopilot)
	$(PYTHON) empire_nucleus.py --interactive

run-swarm: ## Run the Mega Swarm
	$(PYTHON) kimi_mega_swarm.py

docker-up: ## Start only essential Docker services
	docker-compose up -d redis n8n prometheus grafana

docker-down: ## Stop all Docker services
	docker-compose down

clean: ## Remove cache files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .ruff_cache
