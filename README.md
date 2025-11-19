# Rulate

A generic, programmable rule-based comparison engine for evaluating and classifying relationships between pairs of objects.

## Overview

Rulate allows you to define schemas, rules, and catalogs to determine compatibility between objects. The initial use case is wardrobe compatibility checking (determining which clothing items can be worn together), but the engine is designed to be domain-agnostic.

## Features

- **Schema Definition**: Define dimensions and attributes for your domain
- **Declarative Rules**: Express compatibility logic in YAML/JSON
- **Type Safety**: Built with Pydantic for robust validation
- **CLI Interface**: Command-line tools for validation and evaluation
- **Extensible**: Easy to add custom rule types and operators

## Project Status

Currently in **Phase 1**: Core Engine Development

- [x] Project setup
- [ ] Core models (schema, rules, catalog)
- [ ] Rule evaluation engine
- [ ] CLI interface
- [ ] Example wardrobe configuration

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd rulate

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

## Quick Start

Coming soon! The CLI interface is currently under development.

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black .

# Lint
ruff check .

# Type check
mypy rulate
```

## Documentation

See [SPECIFICATION.md](SPECIFICATION.md) for detailed technical specifications.

See [TASKS.md](TASKS.md) for development roadmap and task breakdown.

## License

TBD

## Contributing

This project is currently in early development.
