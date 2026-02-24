# DevStart

CLI tool that scaffolds Python projects with all dev tooling pre-configured.

## Features

- Scaffolds a clean Python project with `src/` layout
- Pre-configured dev tooling: ruff, mypy, pytest, debugpy
- Docker & Docker Compose included by default
- PlantUML diagram templates for project documentation
- Optional: GitHub Actions CI, devcontainer, pre-commit hooks, Docker, diagrams
- Interactive or flag-driven project creation

## Installation

```bash
uv tool install devstart
```

## Usage

### Interactive

```bash
devstart new myproject
```

### Non-interactive (use defaults)

```bash
devstart new myproject -y
```

### All flags

```bash
devstart new myproject \
  --description "My awesome project" \
  --author "Your Name" \
  --python 3.14 \
  --no-ci \
  --no-devcontainer \
  --no-precommit \
  -y
```

| Flag | Default | Description |
|---|---|---|
| `[NAME]` | (prompted) | Project name (positional arg) |
| `--description` / `-d` | (prompted) | Project description |
| `--author` / `-a` | (prompted) | Author name |
| `--python` | `3.14` | Python version |
| `--no-ci` | false | Skip GitHub Actions CI |
| `--no-devcontainer` | false | Skip devcontainer setup |
| `--no-precommit` | false | Skip pre-commit hooks config |
| `--docker/--no-docker` | true | Include Docker setup |
| `--diagrams/--no-diagrams` | true | Include PlantUML diagram templates |
| `--no-interactive` / `-y` | false | Use defaults, skip all prompts |

### Generated Project Structure

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
├── docker/                      # optional
│   ├── Dockerfile
│   └── docker-compose.yml
├── docs/                        # optional
│   └── diagrams/
│       └── class_diagram.puml
├── .vscode/
│   ├── launch.json
│   └── settings.json
├── .github/workflows/ci.yml    # optional
├── .devcontainer/               # optional
├── .pre-commit-config.yaml      # optional
├── pyproject.toml
├── README.md
├── Makefile
├── .gitignore
├── .dockerignore
└── .env
```

## Development

```bash
uv sync --all-groups
uv run pytest
uv run ruff check src/
```

---

*Generated projects come with ruff, mypy, pytest, and debugpy pre-configured.*
