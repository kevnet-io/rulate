# Makefile for Rulate
# Generic rule-based comparison engine
#
# Quick reference:
#   make help          - Show all available targets
#   make check-all     - Run all checks (backend + frontend) - matches CI
#   make format        - Auto-fix all formatting issues
#   make dev           - Start both backend and frontend dev servers

.PHONY: help
help:
	@echo "Rulate Development Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install           Install all dependencies (backend + frontend)"
	@echo "  make install-backend   Install Python dependencies with uv"
	@echo "  make install-frontend  Install Node.js dependencies"
	@echo "  make install-hooks     Install pre-commit hooks"
	@echo ""
	@echo "Formatting (modifies files):"
	@echo "  make format            Format all code (backend + frontend)"
	@echo "  make format-backend    Format Python code with black + ruff --fix"
	@echo "  make format-frontend   Format frontend code with prettier"
	@echo ""
	@echo "Linting & Type Checking (read-only):"
	@echo "  make lint              Check Python code with ruff (no fixes)"
	@echo "  make typecheck         Run mypy on rulate/ (core only)"
	@echo "  make lint-frontend     Check frontend with ESLint"
	@echo ""
	@echo "Testing:"
	@echo "  make test              Run backend pytest suite"
	@echo "  make test-cov          Run backend tests with coverage report"
	@echo "  make test-frontend     Run frontend unit tests (vitest)"
	@echo "  make test-e2e          Run frontend E2E tests (playwright)"
	@echo ""
	@echo "Comprehensive Checks (CI-ready):"
	@echo "  make check             Run all backend checks (lint + typecheck + test)"
	@echo "  make check-frontend    Run all frontend checks (prettier + eslint + svelte + tests)"
	@echo "  make check-all         Run ALL checks (backend + frontend) - mirrors CI"
	@echo "  make pre-commit        Run pre-commit hooks on all files"
	@echo ""
	@echo "Development Servers:"
	@echo "  make dev-backend       Start FastAPI server (port 8000)"
	@echo "  make dev-frontend      Start SvelteKit dev server (port 5173)"
	@echo "  make dev               Start both servers (requires terminal multiplexer)"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean             Remove build artifacts and caches"
	@echo "  make clean-backend     Remove Python caches and build files"
	@echo "  make clean-frontend    Remove Node.js build artifacts"
	@echo "  make clean-db          Remove development databases"
	@echo ""
	@echo "Default target: help"

# Default target
.DEFAULT_GOAL := help

#
# Installation targets
#

.PHONY: install
install: install-backend install-frontend install-hooks
	@echo "✓ All dependencies installed"

.PHONY: install-backend
install-backend:
	@echo "Installing Python dependencies..."
	uv sync --dev

.PHONY: install-frontend
install-frontend:
	@echo "Installing frontend dependencies..."
	cd web && npm install

.PHONY: install-hooks
install-hooks:
	@echo "Installing pre-commit hooks..."
	uv run pre-commit install

#
# Formatting targets (modify files)
#

.PHONY: format
format: format-backend format-frontend
	@echo "✓ All code formatted"

.PHONY: format-backend
format-backend:
	@echo "Formatting Python code with black..."
	uv run black .
	@echo "Fixing Python code with ruff..."
	uv run ruff check . --fix

.PHONY: format-frontend
format-frontend:
	@echo "Formatting frontend code with prettier..."
	cd web && npx prettier --write .

#
# Linting & type checking targets (read-only)
#

.PHONY: lint
lint:
	@echo "Linting Python code with ruff (check only)..."
	uv run ruff check .

.PHONY: typecheck
typecheck:
	@echo "Type checking core engine with mypy..."
	uv run mypy rulate

.PHONY: lint-frontend
lint-frontend:
	@echo "Linting frontend code with ESLint..."
	cd web && npm run lint

#
# Testing targets
#

.PHONY: test
test:
	@echo "Running backend tests..."
	uv run pytest

.PHONY: test-cov
test-cov:
	@echo "Running backend tests with coverage..."
	uv run pytest --cov=rulate --cov=api --cov-report=html --cov-report=term

.PHONY: test-frontend
test-frontend:
	@echo "Running frontend unit tests..."
	cd web && npm test

.PHONY: test-e2e
test-e2e:
	@echo "Running E2E tests..."
	@echo "Note: Requires API server running on port 8000"
	cd web && npm run test:e2e

#
# Comprehensive check targets (CI-ready)
#

.PHONY: check
check: lint typecheck test
	@echo "✓ All backend checks passed"

.PHONY: check-frontend
check-frontend:
	@echo "Running all frontend checks..."
	cd web && npm run check:full

.PHONY: check-all
check-all: check check-frontend
	@echo "✓ All checks passed (backend + frontend)"

.PHONY: pre-commit
pre-commit:
	@echo "Running pre-commit hooks on all files..."
	uv run pre-commit run --all-files

#
# Development server targets
#

.PHONY: dev-backend
dev-backend:
	@echo "Starting FastAPI server on http://localhost:8000..."
	@echo "API docs: http://localhost:8000/docs"
	uv run uvicorn api.main:app --reload

.PHONY: dev-frontend
dev-frontend:
	@echo "Starting SvelteKit dev server on http://localhost:5173..."
	cd web && npm run dev

.PHONY: dev
dev:
	@echo "Starting both backend and frontend servers..."
	@echo "This requires running in separate terminals or a terminal multiplexer"
	@echo ""
	@echo "Terminal 1: make dev-backend"
	@echo "Terminal 2: make dev-frontend"
	@echo ""
	@echo "Alternatively, use a tool like 'make -j2' with background processes"

#
# Cleanup targets
#

.PHONY: clean
clean: clean-backend clean-frontend
	@echo "✓ All build artifacts cleaned"

.PHONY: clean-backend
clean-backend:
	@echo "Cleaning Python build artifacts..."
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf rulate.egg-info
	rm -rf dist
	rm -rf build
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✓ Backend artifacts cleaned"

.PHONY: clean-frontend
clean-frontend:
	@echo "Cleaning frontend build artifacts..."
	cd web && rm -rf .svelte-kit
	cd web && rm -rf build
	cd web && rm -rf coverage
	cd web && rm -rf playwright-report
	@echo "✓ Frontend artifacts cleaned"
	@echo "Note: node_modules preserved (run 'rm -rf web/node_modules' manually if needed)"

#
# Database utilities
#

.PHONY: clean-db
clean-db:
	@echo "Cleaning development databases..."
	rm -f rulate.db
	rm -f e2e_test.db
	@echo "✓ Database files removed"
