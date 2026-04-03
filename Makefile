.DEFAULT_GOAL := help

# --- Environment ---

.PHONY: help ensure-uv setup sync install-shell-completion configure-git

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

ensure-uv:
	@command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh

setup: ensure-uv sync install-shell-completion configure-git ## Set up the full dev environment

sync: ## Sync all dependencies
	uv sync --all-groups

install-shell-completion:
	@dpkg -s bash-completion >/dev/null 2>&1 || \
		(sudo apt-get update && sudo apt-get install -y bash-completion && sudo rm -rf /var/lib/apt/lists/*)
	@grep -q 'bash_completion' ~/.bashrc 2>/dev/null || \
		printf '\nif [ -f /etc/bash_completion ]; then\n  . /etc/bash_completion\nfi\n' >> ~/.bashrc

configure-git:
	@if ! git rev-parse --git-dir >/dev/null 2>&1; then \
		git init -b main; \
	fi
	uv run pre-commit install

# --- Quality ---

.PHONY: lint format format-check type-check test test-cov security check

lint: ## Run ruff linter
	uv run ruff check src/ tests/

format: ## Auto-format code with ruff
	uv run ruff format src/ tests/

format-check: ## Check code formatting without modifying
	uv run ruff format --check src/ tests/

type-check: ## Run mypy type checker
	uv run mypy src/

test: ## Run tests
	uv run pytest

test-cov: ## Run tests with coverage report
	uv run pytest --cov=src --cov-report=term-missing

security: ## Run bandit security scan
	uv run bandit -c pyproject.toml -r src/

check: lint format-check type-check security test ## Run all checks

# --- Cleanup ---

.PHONY: clean

clean: ## Remove build artifacts and caches
	rm -rf dist/ build/ .ruff_cache/ .pytest_cache/ .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
