# DevStart

[![PyPI version](https://img.shields.io/pypi/v/devstart)](https://pypi.org/project/devstart/)
[![Python](https://img.shields.io/pypi/pyversions/devstart)](https://pypi.org/project/devstart/)
[![License: MIT](https://img.shields.io/pypi/l/devstart)](https://github.com/AymanKastali/DevStart/blob/main/LICENSE)

CLI tool that scaffolds Python projects with all dev tooling pre-configured.

Stop wasting time setting up ruff, mypy, pytest, Docker, CI, and pre-commit from scratch every time you start a new project. DevStart gives you a production-ready development environment in seconds.

## Features

- **`src/` layout** with hatch dynamic versioning (`__version__` as single source of truth)
- **Dev tooling out of the box**: ruff (lint + format), mypy (strict), pytest, debugpy
- **Docker & Docker Compose** with dev and prod configurations
- **GitHub Actions CI** with pre-commit integration
- **Devcontainer** with shared `.venv` — same venv on host and in container, no permission issues
- **Pre-commit hooks**: ruff, codespell, gitleaks, mypy, pytest
- **PlantUML diagram templates** for project documentation
- **Makefile** with `setup`, `lint`, `format`, `test`, `check`, `docker-up`, and more
- Interactive or fully flag-driven project creation

## Installation

```bash
uv tool install devstart
```

Or with pip:

```bash
pip install devstart
```

## Quick Start

```bash
# Interactive — prompts for project details
devstart new myproject

# Non-interactive — use all defaults
devstart new myproject -y

# Scaffold into current directory
devstart new .
```

## Usage

```bash
devstart new myproject \
  --description "My awesome project" \
  --author "Your Name" \
  --python 3.14 \
  -y
```

| Flag | Default | Description |
|---|---|---|
| `[NAME]` | (prompted) | Project name (positional arg) |
| `--description` / `-d` | (prompted) | Project description |
| `--author` / `-a` | (prompted) | Author name |
| `--python` | `3.14` | Python version |
| `--no-interactive` / `-y` | false | Use defaults, skip all prompts |

## Generated Project Structure

```
myproject/
├── src/myproject/
│   ├── __init__.py
│   ├── __main__.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_main.py
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── docker-compose.prod.yml
├── docs/
│   └── diagrams/
│       └── class_diagram.puml
├── .vscode/
│   ├── launch.json
│   └── settings.json
├── .github/workflows/ci.yml
├── .devcontainer/
│   ├── devcontainer.json
│   └── docker-compose.yml
├── .pre-commit-config.yaml
├── pyproject.toml
├── README.md
├── Makefile
├── .gitignore
├── .dockerignore
├── .env
└── .env.example
```

## What You Get

Every generated project is immediately runnable:

```bash
cd myproject
make setup    # installs uv, syncs deps, sets up git + pre-commit
make check    # runs lint + format check + type check + tests
make test     # runs pytest
make format   # auto-formats with ruff
make infra      # starts infrastructure services
make docker-up  # starts app + infrastructure
```

## Contributing

```bash
git clone https://github.com/AymanKastali/DevStart.git
cd DevStart
make setup
make check
```

## License

MIT
