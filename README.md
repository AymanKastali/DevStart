# DevStart

[![PyPI version](https://img.shields.io/pypi/v/devstart)](https://pypi.org/project/devstart/)
[![Python](https://img.shields.io/pypi/pyversions/devstart)](https://pypi.org/project/devstart/)
[![License: MIT](https://img.shields.io/pypi/l/devstart)](https://github.com/AymanKastali/DevStart/blob/main/LICENSE)
[![Coverage](https://codecov.io/gh/AymanKastali/DevStart/branch/main/graph/badge.svg)](https://codecov.io/gh/AymanKastali/DevStart)

**A zero-config Python project scaffolder.** One command, and you get a production-ready project with linting, type checking, tests, Docker, CI, pre-commit hooks, and a dev container — all wired up, all consistent with each other, all ready to use.

---

## Why DevStart?

Starting a Python project is repetitive and error-prone. You pick a directory layout, write `pyproject.toml` from scratch, configure ruff and mypy and pytest individually, write a `Dockerfile` and `docker-compose.yml`, set up GitHub Actions, add a devcontainer, and then spend an hour making sure all of those agree with each other.

DevStart does it in one command. The result is a project that:

- Runs `make check` (the full pre-commit suite: lint + format + type-check + secret scan + security scan + spell check + tests) cleanly the moment it's created.
- Uses **one source of truth** for tool config (`pyproject.toml`) and **one source of truth** for code-quality checks (`pre-commit`, which CI also runs — no version drift).
- Follows modern Python packaging conventions: `src/` layout, hatch dynamic versioning, PEP 561 typed marker.

---

## Installation

Recommended:

```bash
uv tool install devstart
```

Or with pip:

```bash
pip install devstart
```

DevStart itself requires **Python 3.14+**. Generated projects can target **3.12**, **3.13**, or **3.14**.

---

## Quick Start

```bash
# Interactive — prompts for missing values
devstart new myproject

# Non-interactive — skip prompts, use defaults
devstart new myproject -y

# Scaffold into the current directory
mkdir myproject && cd myproject
devstart new . -y
```

After scaffolding:

```bash
cd myproject
make setup        # install uv, sync deps, register git hooks
make check        # run the full pre-commit suite (canonical quality gate)
make dev          # run the project: uv run python -m myproject
```

That's it — the project is fully configured and ready to develop in.

---

## CLI Reference

```
devstart new [NAME] [OPTIONS]
devstart --version
```

| Flag | Default | Description |
|---|---|---|
| `[NAME]` | (prompted) | Project name. Use `.` to scaffold into the current directory. |
| `--description`, `-d` | (prompted) | One-line project description |
| `--author`, `-a` | (prompted) | Author name |
| `--python` | `3.14` | Target Python version. Allowed: `3.12`, `3.13`, `3.14`. |
| `--no-interactive`, `-y` | `false` | Skip all prompts and fill missing values with defaults |

### Project name rules

- Must be a valid Python identifier (letters, digits, underscores; cannot start with a digit).
- Cannot be a Python keyword (`class`, `def`, …), a dunder name (`__init__`), or a stdlib module name (`json`, `re`, …).
- Hyphens are not allowed in explicit names — `devstart new my-project` is rejected.
- When using `devstart new .`, the directory name is kept verbatim for things that depend on the host path (devcontainer mount, compose volume target). Non-identifier characters are converted to underscores for the Python package name. Example: in `test-proj/`, you get `src/test_proj/` *and* the devcontainer still binds to `/workspaces/test-proj`.

---

## What You Get

Every generated project has this layout:

```
myproject/
├── src/myproject/
│   ├── __init__.py            # __version__ + __app_name__ (single source of truth)
│   ├── __main__.py            # `python -m myproject` entry point
│   ├── main.py
│   └── py.typed               # PEP 561 marker — package ships type info
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_main.py
├── docker/
│   ├── Dockerfile             # uv-based, multi-stage layer caching
│   ├── docker-compose.yml         # dev compose
│   └── docker-compose.prod.yml    # prod overrides
├── docs/diagrams/
│   └── class_diagram.puml         # PlantUML starter
├── .vscode/
│   ├── launch.json            # debugpy: "Debug Module" + "Debug Current File"
│   └── settings.json          # format-on-save (ruff), mypy strict, pytest
├── .devcontainer/
│   ├── devcontainer.json
│   └── docker-compose.yml
├── .github/workflows/
│   └── ci.yml                 # runs pre-commit/action
├── .githooks/
│   └── pre-commit             # executable wrapper, registered by `make setup`
├── .pre-commit-config.yaml
├── pyproject.toml             # all tool config lives here
├── Makefile                   # `make help` lists every target
├── README.md
├── .gitignore
├── .dockerignore
├── .env / .env.example
└── .python-version
```

### Pre-configured tooling

| Tool | Purpose | Configured in |
|---|---|---|
| **ruff** | Lint + format (replaces black, isort, flake8, pylint) | `pyproject.toml` |
| **mypy** | Strict type checking | `pyproject.toml` |
| **pytest** | Test runner, `src/` layout aware | `pyproject.toml` |
| **debugpy** | VS Code debugging | `.vscode/launch.json` |
| **pre-commit** | trailing-whitespace, end-of-file, check-yaml/toml/json/ast, merge-conflict, large-files, debug-statements, detect-private-key, **ruff**, **codespell**, **bandit**, **gitleaks**, **mypy**, **pytest** | `.pre-commit-config.yaml` |
| **GitHub Actions CI** | Runs `pre-commit/action` on push and PR | `.github/workflows/ci.yml` |
| **Docker** | App image + dev/prod compose stacks | `docker/` |
| **Devcontainer** | One-click VS Code container environment | `.devcontainer/` |
| **PlantUML** | Diagram sources + render targets | `docs/diagrams/`, `Makefile` |

Pre-commit is the single source of truth for code-quality checks; CI just runs it. No version drift between your laptop and the build server.

### Test coverage

`make test-cov` runs pytest with coverage and writes two reports:

- a **terminal summary** (`term-missing`) showing which lines are uncovered, and
- **`lcov.info`** at the project root, consumed by the [Coverage Gutters](https://marketplace.visualstudio.com/items?itemName=ryanluker.vscode-coverage-gutters) VS Code extension (included in the recommended extensions).

After running it once, open any source file and run **Coverage Gutters: Display Coverage** (or click *Watch* in the status bar) to render covered/uncovered lines in the gutter. `lcov.info` is git-ignored.

### Makefile targets

`make help` prints every target grouped by section. The full list:

**Environment**
| Target | Description |
|---|---|
| `make setup` | Install uv (if missing), sync deps, register git hooks |
| `make sync` | `uv sync --all-groups` |

**Application**
| Target | Description |
|---|---|
| `make dev` | Run the project (`uv run python -m <project>`) |

**Quality**
| Target | Description |
|---|---|
| `make lint` | Ruff lint |
| `make format` | Ruff format (in place) |
| `make format-check` | Ruff format check (no changes) |
| `make type-check` | mypy strict |
| `make test` | pytest |
| `make test-cov` | pytest with coverage (terminal report + `lcov.info` for Coverage Gutters) |
| `make check` | Run the full pre-commit suite (canonical quality gate — same checks CI runs) |

**Docker (dev)**
| Target | Description |
|---|---|
| `make docker-build` | Build dev images |
| `make docker-up` | Start the dev stack (detached) |
| `make docker-down` | Stop and remove dev containers |
| `make docker-logs` | Tail dev stack logs |
| `make docker-ps` | List dev stack containers |
| `make docker-restart` | Restart the dev stack |

**Docker (prod)**
| Target | Description |
|---|---|
| `make docker-up-prod` | Start the prod stack (detached, with `--build`) |
| `make docker-down-prod` | Stop and remove prod containers |
| `make docker-logs-prod` | Tail prod stack logs |

**Release**
| Target | Description |
|---|---|
| `make tag VERSION=x.y.z` | Create annotated git tag |
| `make release VERSION=x.y.z` | Tag and push a release |

**Diagrams**
| Target | Description |
|---|---|
| `make diagrams` | Render PlantUML diagrams to PNG |
| `make diagrams-svg` | Render PlantUML diagrams to SVG |
| `make diagrams-clean` | Remove rendered diagram images |

**Cleanup**
| Target | Description |
|---|---|
| `make clean` | Remove build artifacts, caches, and `.venv/` |

---

## Design Principles

- **One source of truth, twice.**
  - For *tool configuration*: `pyproject.toml`. No `.ruff.toml`, `mypy.ini`, `setup.cfg`, or `tox.ini`.
  - For *code-quality checks*: pre-commit. CI runs the exact same hooks — what passes locally passes in CI.
- **`src/` layout, always.** Keeps tests honest by preventing accidental imports from the project root.
- **Hatch dynamic versioning.** `__version__` in `src/<project>/__init__.py` is the only place a version number lives. `pyproject.toml` reads from it.
- **Modern Python.** Generated projects target Python 3.12+ and use modern type hints (PEP 695, `type` statements, `|` unions).
- **No raw `print`.** Generated code uses Rich for styled CLI output and structured logging.
- **Devcontainer parity.** The devcontainer's mounted workspace path matches the host directory name even when the host path contains hyphens — so VS Code's "Reopen in Container" just works.

---

## Contributing

```bash
git clone https://github.com/AymanKastali/DevStart.git
cd DevStart
make setup
make check
```

Issues and PRs welcome at <https://github.com/AymanKastali/DevStart/issues>.

---

## License

[MIT](LICENSE)
