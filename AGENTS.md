# Repository Guidelines

## Project Overview

Rulate is a generic, programmable rule-based comparison engine for evaluating and classifying
relationships between pairs of objects. It uses declarative YAML/JSON schemas and rules to determine
compatibility between items in a catalog.

Initial use case: wardrobe compatibility checking (which clothing items can be worn together), but
the engine is designed to be domain-agnostic.

## Quick Reference

Common commands (prefer `make` targets):

- `make install`: install all dependencies (backend + frontend + hooks).
- `make dev-backend`: start API server on `http://localhost:8000`.
- `make dev-frontend`: start web UI on `http://localhost:5173`.
- `make format`: auto-fix formatting (modifies files).
- `make check`: CI-safe checks excluding e2e (read-only).
- `make check-all`: full CI mirror including e2e.
- `make test`: unit tests (backend + frontend).
- `make test-backend`: backend tests only.
- `make test-frontend`: frontend unit tests only.

For all commands: `make` or `make help`.

## Project Structure & Module Organization

- `rulate/`: core Python engine + CLI (`rulate/cli.py`) and evaluation logic (`rulate/engine/`).
- `api/`: FastAPI app (`api/main.py`), routers (`api/routers/`), DB layer (`api/database/`).
- `web/`: SvelteKit UI (routes in `web/src/routes/`, client code in `web/src/lib/`).
- `tests/`: Python tests (`tests/unit/`, `tests/integration/`).
- `docs/`: specifications and roadmap; start with `docs/SPECIFICATION.md`.
- `examples/`: sample configurations (e.g. `examples/wardrobe/`).

## Build, Test, and Development Commands

Use the `Makefile` targets as the default interface:

- `make install`: install backend (via `uv`) + frontend deps + pre-commit hooks.
- `make format`: auto-fix formatting (Python + frontend).
- `make dev-backend`: run FastAPI on `:8000`.
- `make dev-frontend`: run SvelteKit dev server on `:5173`.
- `make serve-production`: build + serve the unified production server on port `8000`.
- `make check`: read-only CI checks (lint + typecheck + unit tests; excludes e2e).
- `make check-all`: full CI mirror, including Playwright e2e.
- Workflow: `make format` while iterating, then `make check` before pushing; hooks run on `git commit`.

### Development Servers

- Dev mode (two processes): `make dev-backend` + `make dev-frontend`.
- Production-like unified server: `make serve-production` (expects built assets in `web/build/`).

## Coding Style & Naming Conventions

- Python: format with `black` (line length 100) and lint with `ruff`.
- Type checking: `mypy` is enforced for `rulate/`.
- Frontend: `prettier` formatting, `eslint` linting, `svelte-check` for TS/Svelte.
- Naming: Python `snake_case` / `PascalCase`; TS `camelCase` / `PascalCase`.

## Testing Guidelines

- Backend: `pytest` (`make test-backend` / `uv run pytest`).
- Frontend unit: `vitest` (`make test-frontend` / `cd web && npm test`).
- E2E: `playwright` (`make test-e2e`; API must be running on `:8000`).
- Coverage expectations are high (see `CONTRIBUTING.md`); add tests for user-facing behavior changes.
- Coverage: `make test-cov` (both), `make test-cov-backend` (backend), or `make test-cov-frontend` (frontend).

## Architecture Notes (High Signal)

Rulate is organized as three layers:

1. Core engine (`rulate/`): schema + ruleset + catalog loading/validation; pairwise evaluation; and
   optional cluster evaluation for finding compatible sets.
2. REST API (`api/`): FastAPI app with SQLite persistence for managing schemas, rulesets, catalogs,
   and items via HTTP.
3. Web UI (`web/`): SvelteKit + TypeScript UI for authoring and exploring schemas/rules/catalogs.

Core engine modules (most frequently edited):

- `rulate/engine/operators.py`: operator implementations and `OPERATOR_REGISTRY`.
- `rulate/engine/condition_evaluator.py`: evaluates pairwise condition dictionaries.
- `rulate/engine/cluster_condition_evaluator.py`: evaluates cluster condition dictionaries.
- `rulate/engine/evaluator.py`: pairwise evaluation orchestration.
- `rulate/engine/cluster_evaluator.py`: cluster finding (Bron–Kerbosch with pivoting).

Cluster mechanism (when working on cluster features):

- Pairwise `RuleSet` builds a compatibility graph.
- `ClusterRuleSet` applies set-level constraints to candidate clusters.
- Cluster relationships (subset/superset/overlap) are derived after clique finding.

## Implementation Notes (Common Footguns)

- Adding operators: implement in `rulate/engine/operators.py`, register in `OPERATOR_REGISTRY`, and add focused unit tests.
- API JSON fields: in `api/database/models.py`, use explicit `get_*()` / `set_*()` methods (not properties/direct JSON strings).
- Svelte 5: prefer `onclick` props (not `on:click`), and reassign mutated objects to trigger reactivity (`obj = obj`).
- Rule conditions are nested dictionaries (e.g. `{"all": [{"equals": {"field": "x"}}, {"not": {...}}]}`).
- `RuleEvaluation.passed` is “rule allowed compatibility” (exclusion rules invert the raw condition result).

## Using the CLI (Core Engine)

Examples (via `uv`):

- Validate: `uv run rulate validate schema examples/wardrobe/schema_v2.yaml`
- Evaluate pair: `uv run rulate evaluate pair <item1> <item2> --catalog ... --rules ... --schema ...`
- Matrix: `uv run rulate evaluate matrix --catalog ... --rules ... --format summary`

## Code Quality Workflow

- Auto-fix while iterating: `make format` (or `make format-backend` / `make format-frontend`).
- Verify before pushing: `make check` (fast, read-only, excludes e2e); use `make check-all` when you need e2e.
- Pre-commit hooks run on `git commit`; prefer fixing issues via `make format` rather than bypassing hooks.

### Type Checking Note

- `mypy` is enforced for the core engine (`rulate/`).
- The API layer (`api/`) may be excluded from strict typing due to SQLAlchemy typing complexity; follow
  existing patterns instead of fighting the type system.

## Configuration & Local Data

- The API uses SQLite for development; don’t commit local DBs or build/coverage artifacts unless requested.
- Unified production serving expects built assets in `web/build/` (via `make serve-production` / `make build-frontend`).

## Commit & Pull Request Guidelines

- Use Conventional Commits (`feat: …`, `fix: …`, `chore(deps): …`) per `CONTRIBUTING.md`.
- PRs: include description, test plan (`make check`), screenshots for UI changes, and linked issues/breaking-change notes.

## Agent-Specific Instructions

- When invoking Python, use `python3` (not `python`).
- Prefer using the repo’s patch workflow (e.g., apply patch/diff tools) over heredocs for file creation.
