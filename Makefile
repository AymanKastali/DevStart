.DEFAULT_GOAL := help

VERSION_FILE := src/devstart/__init__.py

##@ Help

.PHONY: help
help: ## Show this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} \
		/^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2 } \
		/^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) }' $(MAKEFILE_LIST)

##@ Environment

.PHONY: setup sync

setup: ## Install uv (if missing), sync deps, register git hooks
	@command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh
	uv sync --all-groups
	@git rev-parse --git-dir >/dev/null 2>&1 && git config core.hooksPath .githooks || true

sync: ## Sync all dependency groups
	uv sync --all-groups

##@ Quality

.PHONY: lint format format-check type-check test test-cov security check

lint: ## Run ruff linter
	uv run ruff check .

format: ## Auto-format code with ruff
	uv run ruff format .

format-check: ## Verify formatting without modifying files
	uv run ruff format --check .

type-check: ## Run mypy strict type checker
	uv run mypy src/

test: ## Run pytest
	uv run pytest

test-cov: ## Run pytest with coverage report
	uv run pytest --cov=src --cov-report=term-missing

security: ## Run bandit security scan on src/
	uv run bandit -c pyproject.toml -r src/

check: lint format-check type-check security test ## Full quality gate (lint + format + type + security + test)

##@ Release

.PHONY: bump-version changelog build tag release publish

bump-version: ## Bump __version__ (VERSION=x.y.z)
	@test -n "$(VERSION)" || (echo "ERROR: pass VERSION=x.y.z (e.g. make bump-version VERSION=0.3.0)" && exit 1)
	@sed -i.bak 's/__version__ = ".*"/__version__ = "$(VERSION)"/' $(VERSION_FILE) && rm -f $(VERSION_FILE).bak
	@echo "Bumped __version__ → $(VERSION)"

changelog: ## Print commits since the last tag
	@LAST_TAG=$$(git describe --tags --abbrev=0 2>/dev/null); \
	if [ -z "$$LAST_TAG" ]; then \
		echo "## All commits"; git log --oneline --no-merges; \
	else \
		echo "## Changes since $$LAST_TAG"; git log $$LAST_TAG..HEAD --oneline --no-merges; \
	fi

build: clean ## Build wheel and sdist into dist/
	uv build

tag: ## Create annotated git tag (VERSION=x.y.z)
	@test -n "$(VERSION)" || (echo "ERROR: pass VERSION=x.y.z (e.g. make tag VERSION=0.3.0)" && exit 1)
	git tag -a "v$(VERSION)" -m "Release v$(VERSION)"
	@echo "Tagged v$(VERSION)"

release: check bump-version build tag ## Full release pipeline (VERSION=x.y.z): check → bump → build → tag
	@echo "Release v$(VERSION) prepared. Run 'make publish' to upload to PyPI."

publish: ## Publish dist/* to PyPI
	uv publish

##@ Cleanup

.PHONY: clean

clean: ## Remove build artifacts and caches
	rm -rf dist/ build/ .ruff_cache/ .pytest_cache/ .mypy_cache/ .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
