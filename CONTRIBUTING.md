# Contributing to Rulate

Thank you for your interest in contributing to Rulate! This guide will help you get started with development and understand our contribution process.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Architecture](#project-architecture)
- [Development Workflow](#development-workflow)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing](#testing)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

## Code of Conduct

This project adheres to a code of conduct based on respect, inclusivity, and collaboration. Please be kind and constructive in all interactions.

## Getting Started

Rulate is a generic, programmable rule-based comparison engine. Before contributing:

1. Read the [README.md](README.md) for project overview
2. Review [docs/SPECIFICATION.md](docs/SPECIFICATION.md) for technical details
3. Check [docs/FUTURE_TASKS.md](docs/FUTURE_TASKS.md) for planned features
4. Browse existing [issues](https://github.com/kevnet-io/rulate/issues) and [pull requests](https://github.com/kevnet-io/rulate/pulls)

## Development Setup

### Prerequisites

- **Python 3.10+** (3.10, 3.11, or 3.12 recommended)
- **Node.js 20+** (for web UI development)
- **uv** (Python package installer) - Install: `pip install uv`
- **Git**

### Initial Setup

1. **Fork and clone the repository:**

```bash
git clone https://github.com/YOUR_USERNAME/rulate.git
cd rulate
```

2. **Install Python dependencies:**

```bash
uv sync --dev
```

This creates a virtual environment in `.venv/` and installs all dependencies.

3. **Install pre-commit hooks (recommended):**

```bash
pip install pre-commit
pre-commit install
```

This automatically runs code quality checks before each commit.

4. **Set up the web UI (if contributing to frontend):**

```bash
cd web
npm install
```

### Verify Installation

```bash
# Run backend tests
uv run pytest

# Run frontend tests
cd web
npm test

# Start the API server
uv run uvicorn api.main:app --reload

# Start the web UI (in another terminal)
cd web
npm run dev
```

## Project Architecture

Rulate has a three-layer architecture:

### 1. Core Engine (`rulate/`)
Domain-agnostic evaluation engine written in Python.

- **`rulate/models/`** - Pydantic data models (Schema, RuleSet, Catalog, etc.)
- **`rulate/engine/operators.py`** - Operator implementations for rule conditions
- **`rulate/engine/evaluator.py`** - Main evaluation orchestrator
- **`rulate/engine/cluster_evaluator.py`** - Cluster finding engine
- **`rulate/utils/`** - YAML/JSON loaders and utilities
- **`rulate/cli.py`** - Command-line interface

### 2. REST API (`api/`)
FastAPI backend with SQLite persistence.

- **`api/main.py`** - FastAPI app setup
- **`api/routers/`** - API endpoint implementations
- **`api/database/models.py`** - SQLAlchemy ORM models
- **`api/database/connection.py`** - Database session management

### 3. Web UI (`web/`)
SvelteKit 2.0 frontend with TypeScript.

- **`web/src/routes/`** - Page components
- **`web/src/lib/api/client.ts`** - API client
- **`web/src/lib/components/`** - Reusable UI components

See [docs/CLAUDE.md](docs/CLAUDE.md) for detailed architecture documentation.

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Your Changes

- Write clean, well-documented code
- Follow the code style guidelines (see below)
- Add tests for new functionality
- Update documentation as needed

### 3. Run Tests Locally

```bash
# Backend tests
uv run pytest

# Backend with coverage
uv run pytest --cov=rulate --cov=api

# Frontend unit tests
cd web
npm test

# Frontend E2E tests
npm run test:e2e
```

### 4. Run Code Quality Checks

```bash
# Python formatting
uv run black .

# Python linting
uv run ruff check . --fix

# Python type checking
uv run mypy rulate

# Frontend linting
cd web
npm run lint
```

Or simply commit - pre-commit hooks will run these automatically!

### 5. Commit Your Changes

See [Commit Messages](#commit-messages) section below.

### 6. Push and Create a Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a PR on GitHub using the pull request template.

## Code Style Guidelines

### Python

- **Formatter:** [Black](https://black.readthedocs.io/) (line length: 100)
- **Linter:** [Ruff](https://docs.astral.sh/ruff/)
- **Type Checker:** [Mypy](https://mypy.readthedocs.io/)

**Key conventions:**
- Use type hints for function arguments and return values
- Write docstrings for public functions and classes
- Prefer descriptive variable names over comments
- Keep functions focused and small
- Use Pydantic models for data validation

**Example:**

```python
def evaluate_pair(
    item1: Item,
    item2: Item,
    rules: list[Rule]
) -> ComparisonResult:
    """
    Evaluate compatibility between two items using the given rules.

    Args:
        item1: First item to compare
        item2: Second item to compare
        rules: List of rules to apply

    Returns:
        ComparisonResult with compatibility decision and rule evaluations
    """
    # Implementation here
```

### TypeScript/Svelte

- **Formatter:** [Prettier](https://prettier.io/)
- **Linter:** [ESLint](https://eslint.org/)

**Key conventions:**
- Use TypeScript for type safety
- Svelte 5 syntax (runes: `$state`, `$derived`, `$effect`)
- Event handlers use `onclick` prop, not `on:click` directive
- Prefer composition over inheritance
- Keep components focused and reusable

**Example:**

```typescript
interface Item {
  id: string;
  name: string;
  attributes: Record<string, any>;
}

async function fetchItems(catalogName: string): Promise<Item[]> {
  const response = await fetch(`/api/v1/catalogs/${catalogName}/items`);
  if (!response.ok) throw new Error('Failed to fetch items');
  return response.json();
}
```

## Testing

### Backend Tests

We use **pytest** with high coverage standards (94%+ required).

**Test location:** `tests/`

**Running tests:**

```bash
# All tests
uv run pytest

# Specific file
uv run pytest tests/unit/test_schema.py

# Specific test
uv run pytest tests/unit/test_schema.py::TestSchema::test_create_simple_schema

# With coverage report
uv run pytest --cov=rulate --cov=api --cov-report=html
```

**Writing tests:**

```python
import pytest
from rulate.models.schema import Schema

def test_schema_validation():
    """Test that schema validates dimensions correctly."""
    schema = Schema(
        name="test_schema",
        version="1.0.0",
        dimensions=[
            {"name": "color", "type": "enum", "values": ["red", "blue"]}
        ]
    )
    # Valid attribute
    schema.validate_attributes({"color": "red"})  # Should pass

    # Invalid attribute
    with pytest.raises(ValueError):
        schema.validate_attributes({"color": "green"})
```

### Frontend Tests

We use **Vitest** for unit tests and **Playwright** for E2E tests (100% production code coverage).

**Test location:** `web/tests/`

**Running tests:**

```bash
cd web

# Unit tests
npm test

# E2E tests
npm run test:e2e

# E2E tests with UI
npm run test:e2e -- --ui
```

**Writing unit tests:**

```typescript
import { describe, it, expect } from 'vitest';
import { parseAttributeValue } from '$lib/utils/forms';

describe('parseAttributeValue', () => {
  it('parses integer values', () => {
    expect(parseAttributeValue('42', 'integer')).toBe(42);
  });

  it('parses boolean values', () => {
    expect(parseAttributeValue('true', 'boolean')).toBe(true);
  });
});
```

## Commit Messages

We follow a conventional commit message format for clarity and automated changelog generation.

### Format

```
<type>: <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Build process, tooling, dependencies

### Example

```bash
git commit -m "feat: Add min_cluster_size operator for cluster constraints

Implements MinClusterSizeOperator to enforce minimum cluster sizes.
This allows users to define cluster rules that require a minimum
number of items in each compatible set.

Closes #42

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Important:** Include the Claude Code attribution footer if you used Claude Code assistance.

## Pull Request Process

### Before Submitting

1. **Ensure all tests pass:**
   ```bash
   uv run pytest
   cd web && npm test && npm run test:e2e
   ```

2. **Run code quality checks:**
   ```bash
   uv run black . && uv run ruff check . && uv run mypy rulate
   ```

3. **Update documentation:**
   - Update README.md if adding user-facing features
   - Update docs/CLAUDE.md if changing architecture
   - Add docstrings and comments where needed

4. **Add tests:**
   - Backend: Maintain 94%+ coverage
   - Frontend: Maintain 100% production code coverage

### PR Checklist

Use the pull request template and ensure:

- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] Code style checks pass
- [ ] No breaking changes (or clearly documented)
- [ ] Commits follow conventional format
- [ ] PR description clearly explains changes

### Review Process

1. Automated CI checks will run (tests, linting, type checking)
2. Maintainers will review your code
3. Address any feedback or requested changes
4. Once approved, your PR will be merged

## Reporting Bugs

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) to report bugs.

**Include:**
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Error messages or screenshots

## Suggesting Features

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md) to suggest features.

**Include:**
- Clear description of the feature
- Use case / problem it solves
- Proposed solution
- Alternatives considered

Check [docs/FUTURE_TASKS.md](docs/FUTURE_TASKS.md) for features already on the roadmap.

## Questions?

- **Documentation:** See [docs/](docs/) directory
- **Examples:** See [examples/wardrobe/](examples/wardrobe/)
- **Architecture:** See [docs/CLAUDE.md](docs/CLAUDE.md)
- **Issues:** Browse or create an [issue](https://github.com/kevnet-io/rulate/issues)

Thank you for contributing to Rulate! 🎉
