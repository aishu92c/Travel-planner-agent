.PHONY: help install install-dev install-all clean test test-unit test-integration lint format type-check pre-commit docker-build docker-up docker-down cdk-deploy cdk-destroy

help:
	@echo "Available commands:"
	@echo "  make install          - Install production dependencies"
	@echo "  make install-dev      - Install development dependencies"
	@echo "  make install-all      - Install all dependencies"
	@echo "  make clean            - Remove build artifacts and cache"
	@echo "  make test             - Run all tests"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make lint             - Run linters (ruff)"
	@echo "  make format           - Format code (black + ruff)"
	@echo "  make type-check       - Run type checking (mypy)"
	@echo "  make pre-commit       - Run pre-commit hooks"
	@echo "  make docker-build     - Build Docker image"
	@echo "  make docker-up        - Start Docker services"
	@echo "  make docker-down      - Stop Docker services"
	@echo "  make cdk-deploy       - Deploy AWS infrastructure"
	@echo "  make cdk-destroy      - Destroy AWS infrastructure"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

install-all:
	pip install -e ".[all]"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf build/ dist/ htmlcov/ .coverage

test:
	pytest tests/ -v

test-unit:
	pytest tests/unit/ -v -m unit

test-integration:
	pytest tests/integration/ -v -m integration

test-cov:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

lint:
	ruff check src/ tests/

format:
	black src/ tests/
	ruff check --fix src/ tests/

type-check:
	mypy src/

pre-commit:
	pre-commit run --all-files

docker-build:
	docker-compose -f docker/docker-compose.yml build

docker-up:
	docker-compose -f docker/docker-compose.yml up -d

docker-down:
	docker-compose -f docker/docker-compose.yml down

cdk-synth:
	cd infrastructure && cdk synth

cdk-deploy:
	cd infrastructure && cdk deploy --all

cdk-destroy:
	cd infrastructure && cdk destroy --all

setup-local:
	./scripts/local_dev_setup.sh

seed-data:
	python scripts/seed_knowledge_base.py

run-dev:
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
