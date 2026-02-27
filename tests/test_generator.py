"""Tests for devstart project generator."""

from __future__ import annotations

import json
import tomllib
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any

from devstart.generators.project import generate_project


class TestDirectoryStructure:
    def test_full_project_structure(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"

        # Core files always present
        assert (root / "pyproject.toml").is_file()
        assert (root / "README.md").is_file()
        assert (root / ".gitignore").is_file()
        assert (root / "Makefile").is_file()
        assert (root / ".env").is_file()

        # Source tree
        assert (root / "src" / "testproject" / "__init__.py").is_file()
        assert (root / "src" / "testproject" / "__main__.py").is_file()
        assert (root / "src" / "testproject" / "main.py").is_file()
        # Tests
        assert (root / "tests" / "__init__.py").is_file()
        assert (root / "tests" / "conftest.py").is_file()
        assert (root / "tests" / "test_main.py").is_file()

        # VSCode
        assert (root / ".vscode" / "launch.json").is_file()
        assert (root / ".vscode" / "settings.json").is_file()

        # Continue
        assert (root / ".continue" / "config.yaml").is_file()

        # Diagrams
        assert (root / "docs" / "diagrams" / "class_diagram.puml").is_file()

    def test_minimal_project_structure(
        self, tmp_project_dir: Path, minimal_config: dict[str, Any]
    ):
        generate_project(minimal_config)
        root = tmp_project_dir / "testproject"

        # Core files still present
        assert (root / "pyproject.toml").is_file()
        assert (root / "src" / "testproject" / "main.py").is_file()
        assert (root / ".vscode" / "launch.json").is_file()
        assert (root / ".vscode" / "settings.json").is_file()

        # Optional files should NOT exist
        assert not (root / ".github").exists()
        assert not (root / ".devcontainer").exists()
        assert not (root / ".pre-commit-config.yaml").exists()
        assert not (root / "docker").exists()
        assert not (root / ".dockerignore").exists()
        assert not (root / "docs").exists()
        assert not (root / ".continue").exists()


class TestConditionalGeneration:
    def test_ci_generated_when_enabled(
        self, tmp_project_dir: Path, minimal_config: dict[str, Any]
    ):
        minimal_config["ci"] = True
        generate_project(minimal_config)
        root = tmp_project_dir / "testproject"
        assert (root / ".github" / "workflows" / "ci.yml").is_file()

    def test_ci_skipped_when_disabled(
        self, tmp_project_dir: Path, minimal_config: dict[str, Any]
    ):
        generate_project(minimal_config)
        root = tmp_project_dir / "testproject"
        assert not (root / ".github").exists()

    def test_devcontainer_generated_when_enabled(
        self, tmp_project_dir: Path, minimal_config: dict[str, Any]
    ):
        minimal_config["devcontainer"] = True
        generate_project(minimal_config)
        root = tmp_project_dir / "testproject"
        assert (root / ".devcontainer" / "devcontainer.json").is_file()

    def test_devcontainer_skipped_when_disabled(
        self, tmp_project_dir: Path, minimal_config: dict[str, Any]
    ):
        generate_project(minimal_config)
        root = tmp_project_dir / "testproject"
        assert not (root / ".devcontainer").exists()

    def test_precommit_generated_when_enabled(
        self, tmp_project_dir: Path, minimal_config: dict[str, Any]
    ):
        minimal_config["precommit"] = True
        generate_project(minimal_config)
        root = tmp_project_dir / "testproject"
        assert (root / ".pre-commit-config.yaml").is_file()

    def test_precommit_skipped_when_disabled(
        self, tmp_project_dir: Path, minimal_config: dict[str, Any]
    ):
        generate_project(minimal_config)
        root = tmp_project_dir / "testproject"
        assert not (root / ".pre-commit-config.yaml").exists()

    def test_docker_generated_when_enabled(
        self, tmp_project_dir: Path, minimal_config: dict[str, Any]
    ):
        minimal_config["docker"] = True
        generate_project(minimal_config)
        root = tmp_project_dir / "testproject"
        assert (root / "docker" / "Dockerfile").is_file()
        assert (root / "docker" / "docker-compose.yml").is_file()
        assert (root / ".dockerignore").is_file()

    def test_docker_skipped_when_disabled(
        self, tmp_project_dir: Path, minimal_config: dict[str, Any]
    ):
        generate_project(minimal_config)
        root = tmp_project_dir / "testproject"
        assert not (root / "docker").exists()
        assert not (root / ".dockerignore").exists()

    def test_diagrams_generated_when_enabled(
        self, tmp_project_dir: Path, minimal_config: dict[str, Any]
    ):
        minimal_config["diagrams"] = True
        generate_project(minimal_config)
        root = tmp_project_dir / "testproject"
        assert (root / "docs" / "diagrams" / "class_diagram.puml").is_file()

    def test_diagrams_skipped_when_disabled(
        self, tmp_project_dir: Path, minimal_config: dict[str, Any]
    ):
        generate_project(minimal_config)
        root = tmp_project_dir / "testproject"
        assert not (root / "docs").exists()

    def test_continue_generated_when_enabled(
        self, tmp_project_dir: Path, minimal_config: dict[str, Any]
    ):
        minimal_config["continue"] = True
        generate_project(minimal_config)
        root = tmp_project_dir / "testproject"
        assert (root / ".continue" / "config.yaml").is_file()

    def test_continue_skipped_when_disabled(
        self, tmp_project_dir: Path, minimal_config: dict[str, Any]
    ):
        generate_project(minimal_config)
        root = tmp_project_dir / "testproject"
        assert not (root / ".continue").exists()


class TestTemplateRendering:
    def test_pyproject_contains_project_name(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / "pyproject.toml").read_text()
        assert 'name = "testproject"' in content

    def test_pyproject_contains_description(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / "pyproject.toml").read_text()
        assert 'description = "A test project"' in content

    def test_pyproject_contains_author(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / "pyproject.toml").read_text()
        assert 'authors = [{ name = "Test Author" }]' in content

    def test_pyproject_contains_python_version(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / "pyproject.toml").read_text()
        assert 'requires-python = ">=3.14"' in content

    def test_pyproject_ruff_config(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / "pyproject.toml").read_text()
        assert "[tool.ruff]" in content
        assert 'target-version = "py314"' in content
        assert "line-length = 88" in content
        assert '"TC"' in content

    def test_pyproject_mypy_strict(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / "pyproject.toml").read_text()
        assert "[tool.mypy]" in content
        assert "strict = true" in content

    def test_pyproject_pytest_config(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / "pyproject.toml").read_text()
        assert "[tool.pytest.ini_options]" in content
        assert 'testpaths = ["tests"]' in content
        assert 'pythonpath = ["src"]' in content

    def test_pyproject_contains_rich_dependency(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / "pyproject.toml").read_text()
        assert '"rich>=13.0.0"' in content

    def test_readme_contains_project_name(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / "README.md").read_text()
        assert "# testproject" in content

    def test_readme_docker_section_when_enabled(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / "README.md").read_text()
        assert "## Docker" in content

    def test_readme_no_docker_section_when_disabled(
        self, tmp_project_dir: Path, minimal_config: dict[str, Any]
    ):
        generate_project(minimal_config)
        root = tmp_project_dir / "testproject"
        content = (root / "README.md").read_text()
        assert "## Docker" not in content

    def test_vscode_launch_json(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".vscode" / "launch.json").read_text()
        assert '"Debug Module"' in content
        assert '"Debug Current File"' in content
        assert '"debugpy"' in content
        assert '"testproject"' in content

    def test_ci_uses_precommit_action_when_precommit_enabled(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".github" / "workflows" / "ci.yml").read_text()
        assert "pre-commit/action@v3.0.1" in content
        # No explicit tool steps — everything runs via pre-commit
        assert "ruff check" not in content
        assert "ruff format --check" not in content
        assert "codespell" not in content
        assert "gitleaks" not in content
        assert "uv run mypy" not in content
        assert "uv run pytest" not in content

    def test_ci_uses_explicit_steps_when_precommit_disabled(
        self, tmp_project_dir: Path, minimal_config: dict[str, Any]
    ):
        minimal_config["ci"] = True
        generate_project(minimal_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".github" / "workflows" / "ci.yml").read_text()
        assert "pre-commit/action" not in content
        assert "ruff check" in content
        assert "ruff format --check" in content
        assert "codespell" in content
        assert "gitleaks" in content
        assert "mypy" in content
        assert "pytest" in content

    def test_precommit_all_checks_via_ci(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        """When precommit is enabled, all checks (including mypy and pytest)
        run via pre-commit — CI just calls pre-commit/action."""
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        ci = (root / ".github" / "workflows" / "ci.yml").read_text()
        precommit = (root / ".pre-commit-config.yaml").read_text()
        assert "pre-commit/action" in ci
        assert "id: mypy" in precommit
        assert "id: pytest" in precommit

    def test_ci_all_checks_without_precommit(
        self, tmp_project_dir: Path, minimal_config: dict[str, Any]
    ):
        """When precommit is disabled, CI has explicit steps for everything."""
        minimal_config["ci"] = True
        generate_project(minimal_config)
        root = tmp_project_dir / "testproject"
        ci = (root / ".github" / "workflows" / "ci.yml").read_text()
        assert "uv run mypy" in ci
        assert "uv run pytest" in ci

    def test_precommit_hooks(self, tmp_project_dir: Path, full_config: dict[str, Any]):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".pre-commit-config.yaml").read_text()
        assert "trailing-whitespace" in content
        assert "check-json" in content
        assert "check-merge-conflict" in content
        assert "check-added-large-files" in content
        assert "detect-private-key" in content
        assert "ruff" in content
        assert "codespell" in content
        assert "gitleaks" in content
        assert "mirrors-mypy" not in content

    def test_precommit_mypy_local_hook(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        """Mypy is a local hook using uv run, not mirrors-mypy."""
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".pre-commit-config.yaml").read_text()
        assert "id: mypy" in content
        assert "entry: uv run mypy ." in content
        assert "language: system" in content
        assert "pass_filenames: false" in content

    def test_precommit_pytest_local_hook(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        """Pytest is a local hook using uv run with coverage."""
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".pre-commit-config.yaml").read_text()
        assert "id: pytest" in content
        assert "uv run pytest" in content
        assert "--cov=src/testproject" in content
        assert "language: system" in content
        assert "pass_filenames: false" in content

    def test_makefile_targets(self, tmp_project_dir: Path, full_config: dict[str, Any]):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / "Makefile").read_text()
        assert "setup:" in content
        assert "lint:" in content
        assert "format:" in content
        assert "type-check:" in content
        assert "test:" in content
        assert "check:" in content
        assert "clean:" in content

    def test_makefile_precommit_install_when_enabled(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / "Makefile").read_text()
        assert "pre-commit install" in content

    def test_makefile_no_precommit_install_when_disabled(
        self, tmp_project_dir: Path, minimal_config: dict[str, Any]
    ):
        generate_project(minimal_config)
        root = tmp_project_dir / "testproject"
        content = (root / "Makefile").read_text()
        assert "pre-commit install" not in content

    def test_makefile_diagrams_targets_when_enabled(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / "Makefile").read_text()
        assert "diagrams:" in content
        assert "diagrams-svg:" in content
        assert "diagrams-clean:" in content

    def test_makefile_no_diagrams_targets_when_disabled(
        self, tmp_project_dir: Path, minimal_config: dict[str, Any]
    ):
        generate_project(minimal_config)
        root = tmp_project_dir / "testproject"
        content = (root / "Makefile").read_text()
        assert "diagrams:" not in content
        assert "diagrams-svg:" not in content
        assert "diagrams-clean:" not in content

    def test_readme_diagrams_section_when_enabled(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / "README.md").read_text()
        assert "## Diagrams" in content

    def test_readme_no_diagrams_section_when_disabled(
        self, tmp_project_dir: Path, minimal_config: dict[str, Any]
    ):
        generate_project(minimal_config)
        root = tmp_project_dir / "testproject"
        content = (root / "README.md").read_text()
        assert "## Diagrams" not in content

    def test_gitignore_diagrams_entries_when_enabled(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".gitignore").read_text()
        assert "docs/diagrams/*.png" in content
        assert "docs/diagrams/*.svg" in content

    def test_gitignore_no_diagrams_entries_when_disabled(
        self, tmp_project_dir: Path, minimal_config: dict[str, Any]
    ):
        generate_project(minimal_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".gitignore").read_text()
        assert "docs/diagrams/*.png" not in content
        assert "docs/diagrams/*.svg" not in content

    def test_pyproject_uses_dynamic_version(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / "pyproject.toml").read_text()
        assert 'dynamic = ["version"]' in content
        assert 'version = "0.1.0"' not in content

    def test_pyproject_has_hatch_version_config(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / "pyproject.toml").read_text()
        assert "[tool.hatch.version]" in content
        assert 'path = "src/testproject/__init__.py"' in content

    def test_init_exports_version(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / "src" / "testproject" / "__init__.py").read_text()
        assert '__version__ = "0.1.0"' in content

    def test_init_exports_app_name(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / "src" / "testproject" / "__init__.py").read_text()
        assert '__app_name__ = "testproject"' in content

    def test_different_python_version(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        full_config["python"] = "3.13"
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        pyproject = (root / "pyproject.toml").read_text()
        assert 'requires-python = ">=3.13"' in pyproject
        assert 'target-version = "py313"' in pyproject


class TestScaffoldIntoCwd:
    def test_use_cwd_creates_in_current_dir(
        self,
        tmp_project_dir: Path,
        full_config: dict[str, Any],
        monkeypatch: pytest.MonkeyPatch,
    ):
        empty_dir = tmp_project_dir / "workdir"
        empty_dir.mkdir()
        monkeypatch.chdir(empty_dir)
        full_config["_use_cwd"] = True
        generate_project(full_config)
        assert (empty_dir / "pyproject.toml").is_file()
        assert (empty_dir / "src" / "testproject" / "main.py").is_file()

    def test_use_cwd_non_empty_raises(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        (tmp_project_dir / "somefile.txt").write_text("hello")
        full_config["_use_cwd"] = True
        with pytest.raises(FileExistsError):
            generate_project(full_config)


class TestGeneratedFileContent:
    def test_pyproject_has_debugpy_dev_dependency(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / "pyproject.toml").read_text()
        assert "debugpy" in content

    def test_vscode_settings_content(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".vscode" / "settings.json").read_text()
        assert '"editor.formatOnSave": true' in content
        assert '"charliermarsh.ruff"' in content
        assert '"mypy-type-checker.args"' in content
        assert '"python.testing.pytestEnabled": true' in content

    def test_devcontainer_extensions(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".devcontainer" / "devcontainer.json").read_text()
        expected_extensions = [
            "ms-python.python",
            "ms-python.debugpy",
            "charliermarsh.ruff",
            "streetsidesoftware.code-spell-checker",
            "ms-python.mypy-type-checker",
            "mhutchie.git-graph",
            "eamodio.gitlens",
            "tamasfe.even-better-toml",
            "usernamehw.errorlens",
            "continue.continue",
        ]
        for ext in expected_extensions:
            assert ext in content, f"Missing extension: {ext}"

    def test_devcontainer_run_args(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".devcontainer" / "devcontainer.json").read_text()
        assert "host.docker.internal:host-gateway" in content

    def test_continue_config_content(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".continue" / "config.yaml").read_text()
        assert "qwen2.5-coder:7b" in content
        assert "qwen2.5-coder:1.5b" in content
        assert "nomic-embed-text" in content
        assert "provider: ollama" in content
        assert "provider: codebase" in content

    def test_devcontainer_docker_in_docker_when_docker_enabled(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".devcontainer" / "devcontainer.json").read_text()
        assert "docker-in-docker" in content
        assert "ms-azuretools.vscode-docker" in content

    def test_devcontainer_no_docker_when_docker_disabled(
        self, tmp_project_dir: Path, minimal_config: dict[str, Any]
    ):
        minimal_config["devcontainer"] = True
        generate_project(minimal_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".devcontainer" / "devcontainer.json").read_text()
        assert "docker-in-docker" not in content
        assert "ms-azuretools.vscode-docker" not in content

    def test_class_diagram_puml_content(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / "docs" / "diagrams" / "class_diagram.puml").read_text()
        assert "@startuml" in content
        assert "@enduml" in content
        assert "testproject" in content
        assert "abstract class BaseService" in content
        assert "interface Repository" in content
        assert "BaseService <|-- AppService" in content

    def test_vscode_settings_plantuml_when_enabled(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".vscode" / "settings.json").read_text()
        assert "plantuml.render" in content
        assert "plantuml.server" in content

    def test_vscode_settings_no_plantuml_when_disabled(
        self, tmp_project_dir: Path, minimal_config: dict[str, Any]
    ):
        generate_project(minimal_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".vscode" / "settings.json").read_text()
        assert "plantuml" not in content

    def test_devcontainer_plantuml_extension_when_enabled(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".devcontainer" / "devcontainer.json").read_text()
        assert "jebbs.plantuml" in content

    def test_devcontainer_no_plantuml_extension_when_disabled(
        self, tmp_project_dir: Path, minimal_config: dict[str, Any]
    ):
        minimal_config["devcontainer"] = True
        generate_project(minimal_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".devcontainer" / "devcontainer.json").read_text()
        assert "jebbs.plantuml" not in content

    def test_devcontainer_continue_extension_when_enabled(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".devcontainer" / "devcontainer.json").read_text()
        assert "continue.continue" in content

    def test_devcontainer_no_continue_extension_when_disabled(
        self, tmp_project_dir: Path, minimal_config: dict[str, Any]
    ):
        minimal_config["devcontainer"] = True
        generate_project(minimal_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".devcontainer" / "devcontainer.json").read_text()
        assert "continue.continue" not in content

    def test_dockerfile_content(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / "docker" / "Dockerfile").read_text()
        # Multi-step build: copy deps first, then source + README
        assert "COPY pyproject.toml" in content
        assert "COPY README.md" in content
        assert "COPY src/" in content
        # Python version matches config
        assert "python:3.14-slim" in content
        # Runs as module
        assert '"testproject"' in content
        # Runs as non-root user
        assert "USER appuser" in content

    def test_docker_compose_content(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / "docker" / "docker-compose.yml").read_text()
        assert "env_file" in content


class TestGeneratedFilesParseable:
    def test_pyproject_is_valid_toml(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / "pyproject.toml").read_bytes()
        parsed = tomllib.loads(content.decode())
        assert parsed["project"]["name"] == "testproject"

    def test_launch_json_is_valid_json(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".vscode" / "launch.json").read_text()
        parsed = json.loads(content)
        assert "configurations" in parsed

    def test_pyproject_includes_precommit_dep_when_enabled(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        content = (root / "pyproject.toml").read_text()
        assert "pre-commit" in content

    def test_pyproject_dynamic_version_valid_toml(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        raw = (root / "pyproject.toml").read_bytes()
        parsed = tomllib.loads(raw.decode())
        assert "version" in parsed["project"]["dynamic"]
        assert "version" not in parsed["project"]
        hatch_path = parsed["tool"]["hatch"]["version"]["path"]
        assert hatch_path == "src/testproject/__init__.py"

    def test_pyproject_excludes_precommit_dep_when_disabled(
        self, tmp_project_dir: Path, minimal_config: dict[str, Any]
    ):
        generate_project(minimal_config)
        root = tmp_project_dir / "testproject"
        content = (root / "pyproject.toml").read_text()
        assert "pre-commit" not in content


class TestTomlEscaping:
    def test_description_with_quotes_produces_valid_toml(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        full_config["description"] = 'A "cool" project'
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        raw = (root / "pyproject.toml").read_bytes()
        parsed = tomllib.loads(raw.decode())
        assert parsed["project"]["description"] == 'A "cool" project'

    def test_author_with_quotes_produces_valid_toml(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        full_config["author"] = 'O\'Brien "Bob"'
        generate_project(full_config)
        root = tmp_project_dir / "testproject"
        raw = (root / "pyproject.toml").read_bytes()
        parsed = tomllib.loads(raw.decode())
        assert parsed["project"]["authors"][0]["name"] == 'O\'Brien "Bob"'


class TestEdgeCases:
    def test_existing_directory_raises(
        self, tmp_project_dir: Path, full_config: dict[str, Any]
    ):
        (tmp_project_dir / "testproject").mkdir()
        with pytest.raises(FileExistsError):
            generate_project(full_config)
