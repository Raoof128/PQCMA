# Makefile for PQC Migration Auditor
# Provides common development and deployment tasks

.PHONY: help install install-dev install-all test test-unit test-integration test-coverage lint format type-check security clean build docker-build docker-run docker-test docker-clean pre-commit run-example scan-code

# Default target
.DEFAULT_GOAL := help

help:
	@echo "PQC Migration Auditor - Makefile Commands"
	@echo ""
	@echo "Installation:"
	@echo "  make install          Install package and dependencies"
	@echo "  make install-dev      Install with development dependencies"
	@echo "  make install-all      Install with all optional dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run all tests"
	@echo "  make test-unit        Run unit tests only"
	@echo "  make test-integration Run integration tests"
	@echo "  make test-coverage    Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             Run all linters"
	@echo "  make format           Format code with black and isort"
	@echo "  make type-check       Run mypy type checking"
	@echo "  make security         Run security checks"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     Build Docker image"
	@echo "  make docker-run       Run scanner in Docker"
	@echo "  make docker-test      Run tests in Docker"
	@echo "  make docker-clean     Remove Docker images and containers"
	@echo ""
	@echo "Build:"
	@echo "  make build            Build distribution packages"
	@echo "  make clean            Clean build artifacts"
	@echo "  make clean-all        Clean all generated files"
	@echo ""
	@echo "Development:"
	@echo "  make pre-commit       Install pre-commit hooks"
	@echo "  make run-example      Run scanner on example code"
	@echo "  make scan-code        Scan this codebase for vulnerabilities"

# Installation targets
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

install-all:
	pip install -e ".[all,dev]"

# Testing targets
test: test-unit test-integration
	@echo "All tests completed"

test-unit:
	pytest tests/ -v

test-integration:
	python test_integration.py
	python test_basic.py

test-coverage:
	pytest tests/ -v --cov=pqc_migration_auditor --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

# Code quality targets
lint:
	@echo "Running flake8..."
	flake8 pqc_migration_auditor/ tests/ || true
	@echo "Running pylint..."
	pylint pqc_migration_auditor/ --exit-zero || true
	@echo "Running mypy..."
	mypy pqc_migration_auditor/ --ignore-missing-imports || true

format:
	@echo "Formatting with black..."
	black pqc_migration_auditor/ tests/ || echo "black not installed"
	@echo "Sorting imports with isort..."
	isort pqc_migration_auditor/ tests/ || echo "isort not installed"

type-check:
	mypy pqc_migration_auditor/ --ignore-missing-imports || echo "mypy not installed"

security:
	@echo "Running bandit security checks..."
	bandit -r pqc_migration_auditor/ || echo "bandit not installed"
	@echo "Checking dependencies for vulnerabilities..."
	safety check || echo "safety not installed"

# Docker targets
docker-build:
	docker build -t pqc-migration-auditor:latest .

docker-run:
	docker run -v $(PWD)/examples/dummy_repo:/scan:ro \
	           -v $(PWD)/reports:/reports \
	           pqc-migration-auditor:latest \
	           scan /scan --output /reports/docker-scan.json

docker-test:
	docker run pqc-migration-auditor:latest --version

docker-clean:
	docker-compose down -v || true
	docker rmi pqc-migration-auditor:latest || true

# Build targets
build: clean
	python -m build

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .eggs/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
	find . -type f -name '*.pyo' -delete 2>/dev/null || true

clean-all: clean
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf reports/
	rm -rf .tox/

# Development targets
pre-commit:
	pip install pre-commit
	pre-commit install

run-example:
	mkdir -p reports
	pqc-audit scan examples/dummy_repo --output reports/example-scan.json
	@echo "Scan complete! Results in reports/example-scan.json"

scan-code:
	mkdir -p reports
	pqc-audit scan . --output reports/self-scan.json
	@echo "Code scan complete! Results in reports/self-scan.json"
