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
	@echo "  make lint              Check all code (backend + frontend)"
	@echo "  make lint-backend      Check Python code with ruff (no fixes)"
	@echo "  make lint-frontend     Check frontend with ESLint"
	@echo "  make typecheck         Run all type checking (backend + frontend)"
	@echo "  make typecheck-backend Run mypy on rulate/ (core only)"
	@echo "  make typecheck-frontend Run svelte-check on frontend"
	@echo ""
	@echo "Testing:"
	@echo "  make test              Run all unit tests (backend + frontend)"
	@echo "  make test-backend      Run backend pytest suite"
	@echo "  make test-frontend     Run frontend unit tests (vitest)"
	@echo "  make test-cov          Run all tests with coverage (backend + frontend)"
	@echo "  make test-cov-backend  Run backend tests with coverage report"
	@echo "  make test-cov-frontend Run frontend tests with coverage report"
	@echo "  make test-e2e          Run frontend E2E tests (playwright)"
	@echo ""
	@echo "Comprehensive Checks (CI-ready):"
	@echo "  make check             Run all checks except e2e (lint + typecheck + test)"
	@echo "  make check-backend     Run all backend checks (lint + typecheck + test)"
	@echo "  make check-frontend    Run all frontend checks (format + lint + typecheck + tests + e2e)"
	@echo "  make check-all         Run ALL checks including e2e - mirrors CI"
	@echo "  make pre-commit        Run pre-commit hooks on all files"
	@echo ""
	@echo "Development Servers:"
	@echo "  make dev               Start both servers in tmux split panes (recommended)"
	@echo "  make dev-backend       Start FastAPI server (port 8000)"
	@echo "  make dev-frontend      Start SvelteKit dev server (port 5173)"
	@echo ""
	@echo "Production Build & Serve:"
	@echo "  make build-frontend    Build frontend for production"
	@echo "  make serve-production  Build and serve unified production server (port 8000)"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make docker-build      Build Docker image"
	@echo "  make docker-up         Start production server in Docker (detached)"
	@echo "  make docker-down       Stop Docker containers"
	@echo "  make docker-logs       View Docker container logs"
	@echo "  make docker-clean      Remove Docker containers and images"
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

.PHONY: setup-claude-code-env
setup-claude-code-env:
	@if [ "$$CLAUDE_CODE_ENTRYPOINT" = "remote" ]; then \
		echo "Detected Claude Code remote environment - setting up Python 3.14..."; \
		uv self update; \
	fi

.PHONY: install
install: install-backend install-frontend install-hooks
	@echo "✓ All dependencies installed"

.PHONY: install-backend
install-backend: setup-claude-code-env
	@echo "Installing Python dependencies..."
	@uv python find --show-version 3.14 >/dev/null || uv python install --upgrade --default 3.14
	uv sync --dev

.PHONY: install-frontend
install-frontend:
	@echo "Installing frontend dependencies..."
	npm install -g npm@11
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
	cd web && npm run format
	@echo "Fixing frontend code with eslint..."
	cd web && npm run lint:fix
#
# Linting & type checking targets (read-only)
#

.PHONY: lint
lint: lint-backend lint-frontend
	@echo "✓ All linting passed"

.PHONY: lint-backend
lint-backend:
	@echo "Linting Python code with ruff (check only)..."
	uv run ruff check .

.PHONY: lint-frontend
lint-frontend:
	@echo "Linting frontend code with ESLint..."
	cd web && npm run lint

.PHONY: typecheck
typecheck: typecheck-backend typecheck-frontend
	@echo "✓ All type checking passed"

.PHONY: typecheck-backend
typecheck-backend:
	@echo "Type checking core engine with mypy..."
	uv run mypy rulate

.PHONY: typecheck-frontend
typecheck-frontend:
	@echo "Type checking frontend with svelte-check..."
	cd web && npm run typecheck

#
# Testing targets
#

.PHONY: test
test: test-backend test-frontend
	@echo "✓ All unit tests passed"

.PHONY: test-backend
test-backend:
	@echo "Running backend tests..."
	uv run pytest -qq

.PHONY: test-frontend
test-frontend:
	@echo "Running frontend unit tests..."
	cd web && npm test

.PHONY: test-cov
test-cov: test-cov-backend test-cov-frontend
	@echo "✓ All unit tests passed"

.PHONY: test-cov-backend
test-cov-backend:
	@echo "Running backend tests with coverage..."
	uv run pytest -qq --cov=rulate --cov=api --cov-report=html --cov-report=term

.PHONY: test-cov-frontend
test-cov-frontend:
	@echo "Running frontend tests with coverage..."
	cd web && npm run test:coverage

.PHONY: test-e2e
test-e2e:
	@echo "Running E2E tests..."
	@echo "Installing Playwright browsers..."
	cd web && npx playwright install --with-deps
	cd web && npm run test:e2e

#
# Comprehensive check targets (CI-ready)
#

.PHONY: check
check: install lint typecheck test
	@echo "✓ All checks passed (excluding e2e)"

.PHONY: check-backend
check-backend: install-backend lint-backend typecheck-backend test-backend
	@echo "✓ All backend checks passed"

.PHONY: check-frontend
check-frontend: install-frontend lint-frontend typecheck-frontend test-frontend
	@echo "✓ All frontend checks passed"

.PHONY: check-all
check-all: check test-e2e
	@echo "✓ All checks passed (including e2e)"

.PHONY: pre-commit
pre-commit: install
	@echo "Running pre-commit hooks on all files..."
	uv run pre-commit run --all-files

#
# Development server targets
#

.PHONY: dev-backend
dev-backend:
	@echo "Starting FastAPI server on http://localhost:8000..."
	@echo "API docs: http://localhost:8000/docs"
	uv run python3 -m uvicorn api.main:app --reload

.PHONY: dev-frontend
dev-frontend:
	@echo "Starting SvelteKit dev server on http://localhost:5173..."
	cd web && npm run dev

.PHONY: dev
dev:
	@if command -v tmux >/dev/null 2>&1; then \
		echo "Starting servers in tmux split panes..."; \
		tmux kill-session -t rulate 2>/dev/null || true; \
		tmux new-session -d -s rulate \
			'echo "╔═══════════════════════════════════════════════════════════════════════════╗"; \
			 echo "║                    RULATE DEV - TMUX QUICK REFERENCE                      ║"; \
			 echo "╠═══════════════════════════════════════════════════════════════════════════╣"; \
			 echo "║  Ctrl+C          Stop all servers and exit tmux                           ║"; \
			 echo "║  Ctrl+B then D   Detach (servers keep running in background)              ║"; \
			 echo "║  Ctrl+B then ↓   Switch to backend/frontend panes                         ║"; \
			 echo "║  Ctrl+B then [   Scroll mode (press q to exit)                            ║"; \
			 echo "║  Ctrl+B then Z   Zoom current pane (toggle fullscreen)                    ║"; \
			 echo "║                                                                           ║"; \
			 echo "║  Backend: http://localhost:8000/docs  │  Frontend: http://localhost:5173  ║"; \
			 echo "║  Reconnect: tmux attach -t rulate     │  Kill: tmux kill-session -t rulate║"; \
			 echo "╚═══════════════════════════════════════════════════════════════════════════╝"; \
			 cat'; \
		tmux split-window -v -t rulate -l 75% 'make dev-backend'; \
		tmux split-window -h -t rulate:0.1 'make dev-frontend'; \
		tmux select-pane -t rulate:0.1; \
		tmux attach-session -t rulate; \
	else \
		echo "Error: tmux is required for 'make dev'"; \
		echo ""; \
		echo "Install tmux:"; \
		echo "  macOS:   brew install tmux"; \
		echo "  Ubuntu:  sudo apt-get install tmux"; \
		echo "  Arch:    sudo pacman -S tmux"; \
		echo ""; \
		echo "Or run servers manually in separate terminals:"; \
		echo "  Terminal 1: make dev-backend"; \
		echo "  Terminal 2: make dev-frontend"; \
		exit 1; \
	fi

#
# Production build and serve targets
#

.PHONY: build-frontend
build-frontend:
	@echo "Building frontend for production..."
	cd web && npm run build
	@echo "✓ Frontend built to web/build/"

.PHONY: serve-production
serve-production: build-frontend
	@echo "Starting production server on http://localhost:8000..."
	@echo "Serving unified API + frontend"
	uv run uvicorn api.main:app --host 0.0.0.0 --port 8000

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

#
# Docker targets
#

.PHONY: docker-build
docker-build:
	@echo "Building Docker image..."
	docker build -t rulate:latest .
	@echo "✓ Docker image built: rulate:latest"

.PHONY: docker-up
docker-up:
	@echo "Starting Rulate in Docker..."
	docker-compose up -d
	@echo "✓ Rulate running at http://localhost:8000"
	@echo "  Health: http://localhost:8000/health"
	@echo "  API docs: http://localhost:8000/docs"
	@echo "  View logs: make docker-logs"
	@echo "  Stop: make docker-down"

.PHONY: docker-down
docker-down:
	@echo "Stopping Rulate Docker containers..."
	docker-compose down
	@echo "✓ Containers stopped"

.PHONY: docker-logs
docker-logs:
	@echo "Following Docker logs (Ctrl+C to stop)..."
	docker-compose logs -f

.PHONY: docker-clean
docker-clean:
	@echo "Cleaning Docker resources..."
	docker-compose down -v
	docker rmi rulate:latest 2>/dev/null || true
	@echo "✓ Docker resources cleaned"
