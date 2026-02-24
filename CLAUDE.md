# DevStart — Python Development Environment Scaffolding CLI

## Project Overview

DevStart is a CLI tool (installed via `uv tool install`) that scaffolds clean Python projects with all dev tooling pre-configured: Ruff (linting + formatting), mypy (type checking), debugpy (debugging), pytest (testing), pre-commit hooks, devcontainer, and GitHub Actions CI. It eliminates repetitive setup so every new Python project starts with a production-ready development environment out of the box.

## Tech Stack

- **Language**: Python 3.14+ (use modern Python features: type parameter syntax PEP 695, `type` statement, improved error messages, etc.)
- **CLI Framework**: Typer
- **Interactive Prompts**: Rich
- **Templating**: Jinja2
- **Logging**: Rich RichHandler (dev) / JSON structured (prod)
- **Package Manager**: uv (both for DevStart itself and generated projects)

## Project Structure

```
DevStart/
├── src/
│   └── devstart/
│       ├── __init__.py
│       ├── cli/
│       │   ├── __init__.py
│       │   └── main.py              # Typer CLI entry point
│       ├── generators/
│       │   ├── __init__.py
│       │   └── project.py           # Orchestrates project generation
│       ├── prompts/
│       │   ├── __init__.py
│       │   └── interactive.py       # Rich-based interactive prompts
│       ├── defaults.py              # Default values and constants
│       └── templates/               # Jinja2 templates for generated files
│           ├── base/                 # Core project structure + tool config
│           ├── ci/                   # GitHub Actions workflow
│           ├── devcontainer/         # .devcontainer config
│           └── precommit/           # Pre-commit hook config
├── tests/
│   ├── test_cli.py
│   ├── test_generator.py
│   └── test_prompts.py
├── pyproject.toml
├── CLAUDE.md
└── README.md
```

## CLI Entry Point

```
devstart = "devstart.cli.main:app"
```

## CLI Commands

- `devstart new [NAME]` — Scaffold a new project (interactive or flag-driven)
- `devstart --version` — Show version

### Flags for `devstart new`

| Flag | Default | Description |
|---|---|---|
| `[NAME]` | (prompted) | Project name (positional arg) |
| `--description` / `-d` | (prompted) | Project description |
| `--author` / `-a` | (prompted) | Author name |
| `--python` | `3.14` | Python version |
| `--no-ci` | false | Skip GitHub Actions CI |
| `--no-devcontainer` | false | Skip devcontainer setup |
| `--no-precommit` | false | Skip pre-commit hook config |
| `--docker/--no-docker` | true | Include Docker setup |
| `--diagrams/--no-diagrams` | true | Include PlantUML diagram templates |
| `--no-interactive` / `-y` | false | Use defaults, skip all prompts |

Core dev tools (ruff, mypy, debugpy, pytest) are always included — not toggleable.

## Generated Project Layout

Generated projects follow a clean `src/` layout with all dev tooling pre-configured:

```
myproject/
├── src/
│   └── myproject/
│       ├── __init__.py
│       ├── __main__.py
│       └── main.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── .vscode/
│   ├── launch.json
│   └── settings.json
├── .devcontainer/             (optional)
│   └── devcontainer.json
├── .github/                   (optional)
│   └── workflows/ci.yml
├── docker/                    (optional)
│   ├── Dockerfile
│   └── docker-compose.yml
├── .dockerignore              (optional)
├── docs/                      (optional)
│   └── diagrams/
│       └── class_diagram.puml
├── pyproject.toml
├── .pre-commit-config.yaml    (optional)
├── .gitignore
├── .env
├── Makefile
└── README.md
```

## Coding Conventions

- Use `src/` layout for both DevStart and generated projects
- All template files use `.j2` extension (Jinja2)
- Use Rich RichHandler for all CLI output (no raw print statements)
- Follow PEP 8, use type hints throughout
- Tests use pytest
- `pyproject.toml` is the single source of truth for all tool configuration (no `.ruff.toml`, `mypy.ini`, `setup.cfg`, etc.)

## Key Design Rules

- If CLI flags are provided, skip prompts for those values
- If flags are missing and `--no-interactive` is NOT set, prompt for missing values
- If `--no-interactive` is set, use sensible defaults for any missing values
- Conditional generation: CI, devcontainer, pre-commit, Docker, and diagrams are optional
- Always included: ruff, mypy, debugpy, pytest, `.vscode/`
- Support `devstart new .` to scaffold into the current directory (digit-starting dir names get `_` prepended)
- Project names are validated: must be valid Python identifiers, not keywords, not dunder names, not stdlib module names
- Description and author values are TOML-escaped before template rendering (handles `"` and `\`)
- Template rendering uses Jinja2 context built from user config
- The generator writes the full directory tree in one pass
- VS Code settings live only in `.vscode/settings.json` — no duplication in `devcontainer.json`

## Dependencies (for DevStart itself)

```
typer>=0.9.0
rich>=13.0.0
jinja2>=3.1.0
```

## Dev Dependencies

```
pytest>=7.0.0
pytest-cov>=4.0.0
ruff>=0.4.0
bandit[toml]>=1.7.0
pre-commit>=3.7.0
mypy>=1.10.0
codespell>=2.3.0
```

## Testing

Run tests with:
```bash
uv run pytest
```

Tests cover:
- CLI invocation (with flags, without flags)
- Project name validation (invalid identifiers, keywords, dunder names, stdlib module names)
- Template rendering correctness
- Directory structure generation
- Conditional generation toggles (CI, devcontainer, pre-commit, Docker)
- Tool configuration correctness in generated `pyproject.toml`
- TOML escaping (descriptions and author names with quotes/backslashes)
- `devstart new .` (scaffold into current directory, including digit-starting directories)
- Edge cases (empty names, special characters, existing directories)

---

## Dev Tool Configuration Rules (Strict Adherence)

These rules apply to **generated project code** — the templates that DevStart produces. All tool configuration lives in `pyproject.toml` unless the tool requires its own file format.

### Ruff (Linting + Formatting)

- Configure under `[tool.ruff]` in `pyproject.toml`
- Set `target-version` to match the chosen Python version
- Line length: 88
- Set `src = ["src"]` for correct import sorting
- Enable a curated rule set: `E`, `F`, `W`, `I`, `N`, `UP`, `B`, `A`, `SIM`, `TC`
- Ruff replaces both a linter and a formatter — no need for black, isort, flake8, or pylint

### mypy (Type Checking)

- Configure under `[tool.mypy]` in `pyproject.toml`
- Set `strict = true` for maximum type safety
- Set `python_version` to match the chosen Python version
- Add `[[tool.mypy.overrides]]` for test files with `disallow_untyped_defs = false` to reduce test boilerplate

### Debugger (debugpy) — generated projects only

- debugpy is included in **generated projects only**, not in DevStart itself
- Generate `.vscode/launch.json` with two configurations:
  - **"Debug Module"**: runs the project as a module (`-m myproject`) using `"type": "debugpy"`
  - **"Debug Current File"**: runs the currently open file using `"type": "debugpy"`
- debugpy is listed as a dev dependency in the generated project

### pytest (Testing)

- Configure under `[tool.pytest.ini_options]` in `pyproject.toml`
- Set `testpaths = ["tests"]`
- Set `pythonpath = ["src"]` for correct import resolution with `src/` layout

### Pre-commit (optional)

- Generate `.pre-commit-config.yaml` with hooks:
  - `pre-commit-hooks`: trailing-whitespace, end-of-file-fixer, check-yaml, check-toml, check-json, check-ast, check-merge-conflict, check-added-large-files, debug-statements, detect-private-key
  - `ruff-pre-commit`: ruff lint (`--fix`) and ruff format
  - `codespell`: spell checking
  - `gitleaks`: secret detection
  - `mypy`: type checking (local hook via `uv run mypy .`, uses project venv so it has access to all dependencies)
  - `pytest`: test runner (local hook via `uv run pytest`, with coverage)
- Pre-commit is the single source of truth for all checks — CI runs `pre-commit/action` instead of duplicating tool steps

### GitHub Actions CI (optional)

- Generate `.github/workflows/ci.yml`
- Trigger: push and pull request to `main`
- Uses `astral-sh/setup-uv` action for uv installation
- CI is the authoritative quality gate — pre-commit is the fast local feedback loop
- **When pre-commit is enabled**: use `pre-commit/action@v3.0.1` to run all checks (ruff, codespell, gitleaks, mypy, pytest) via pre-commit — single source of truth, no version drift. CI is a single step after setup.
- **When pre-commit is disabled**: fall back to explicit steps: `ruff check .`, `ruff format --check .`, `codespell`, `gitleaks/gitleaks-action@v2`, `mypy .`, `pytest`.

### Devcontainer (optional)

- Generate `.devcontainer/devcontainer.json`
- Base image: Python (matching chosen version)
- `postCreateCommand`: `"make setup"` for one-command environment setup (also installs uv)
- VS Code extensions only — no duplicated settings (all VS Code settings live in `.vscode/settings.json`)
- Extensions: Python, debugpy, Ruff, mypy, code-spell-checker, git-graph, gitlens, even-better-toml, errorlens

### Docker (optional)

- Generate `docker/Dockerfile` using a Python slim base image with uv for dependency management
- Generate `docker/docker-compose.yml` with app service configuration
- Generate `.dockerignore` to exclude build artifacts and dev files
- Dockerfile uses multi-step install: copy dependency files first, sync, then copy source for optimal layer caching
- The container runs the project as a module via `uv run python -m <project_name>`

### PlantUML Diagrams (optional)

- Generate `docs/diagrams/` with a starter diagram template
- `class_diagram.puml` — demo UML class diagram showing common PlantUML patterns (abstract classes, interfaces, relationships, package grouping)
- All diagrams use `!theme blueprint` for a clean blue-on-white look
- VS Code settings configure the PlantUML extension for server-side rendering (no local Java needed for preview)
- Makefile targets: `diagrams` (PNG), `diagrams-svg` (SVG), `diagrams-clean` (remove rendered images)
- Generated images (`*.png`, `*.svg`) are git-ignored; only `.puml` source is tracked
- No CI step — diagram rendering is documentation, not a quality gate
- No pre-commit hook — diagrams don't need linting
- Devcontainer includes `jebbs.plantuml` extension when diagrams are enabled

### Makefile

- Generated with the following targets:
  - `help` — list available targets (default)
  - `setup` — full environment setup (`uv sync`, pre-commit install)
  - `sync` — install/sync dependencies (`uv sync`)
  - `lint` — run ruff linter (`uv run ruff check .`)
  - `format` — run ruff formatter (`uv run ruff format .`)
  - `type-check` — run mypy (`uv run mypy .`)
  - `test` — run pytest (`uv run pytest`)
  - `test-cov` — run pytest with coverage (`uv run pytest --cov`)
  - `check` — run full quality gate (lint + format check + type-check + test)
  - `clean` — remove build artifacts, caches, `.venv`
  - `diagrams` — render PlantUML diagrams to PNG (conditional on diagrams enabled)
  - `diagrams-svg` — render PlantUML diagrams to SVG (conditional on diagrams enabled)
  - `diagrams-clean` — remove rendered diagram images (conditional on diagrams enabled)
- All commands use `uv run` to ensure correct virtual environment

## Best Practices Enforced in Generated Projects

- `pyproject.toml` is the single source of truth — no separate `.ruff.toml`, `mypy.ini`, `setup.cfg`, or `tox.ini`
- All dev dependencies pinned with minimum versions
- `src/` layout enforces proper packaging and prevents accidental imports from the project root
- `.vscode/settings.json` enables format-on-save with Ruff and real-time type checking with mypy
- CI is the authoritative quality gate; pre-commit is the fast local feedback loop
- `make check` runs the full quality gate (lint + format + type-check + test) in one command
- Projects are immediately runnable after `make setup`
- `.gitignore` covers Python, venv, IDE, and OS-specific files
- `.env` file included with sensible defaults for local development

## Templates Needed

- **base/**: `pyproject.toml.j2`, `README.md.j2`, `gitignore.j2`, `Makefile.j2`, `env.j2`, `init.py.j2`, `__main__.py.j2`, `main.py.j2`, `test_main.py.j2`, `conftest.py.j2`, `vscode_launch.json.j2`, `vscode_settings.json.j2`
- **ci/**: `ci.yml.j2`
- **devcontainer/**: `devcontainer.json.j2`
- **docker/**: `Dockerfile.j2`, `docker-compose.yml.j2`, `dockerignore.j2`
- **diagrams/**: `class_diagram.puml.j2`
- **precommit/**: `pre-commit-config.yaml.j2`
