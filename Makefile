# Makefile for PQC Migration Auditor

.PHONY: help install install-dev test test-cov lint clean scan-examples

help:
	@echo "PQC Migration Auditor - Makefile Commands"
	@echo ""
	@echo "  make install       Install the package and dependencies"
	@echo "  make install-dev   Install with development dependencies"
	@echo "  make test          Run unit tests"
	@echo "  make test-cov      Run tests with coverage report"
	@echo "  make scan-examples Scan the example dummy repository"
	@echo "  make clean         Remove build artifacts and cache files"
	@echo ""

install:
	pip install -e .

install-dev:
	pip install -e ".[dev,pcap]"

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=pqc_migration_auditor --cov-report=term-missing --cov-report=html

lint:
	@echo "Running basic code checks..."
	python -m py_compile pqc_migration_auditor/*.py
	python -m py_compile pqc_migration_auditor/*/*.py

scan-examples:
	@echo "Scanning dummy repository for quantum-vulnerable crypto..."
	python -m pqc_migration_auditor --mode code --target examples/dummy_repo --verbose

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

.DEFAULT_GOAL := help
