"""Tests for devstart project generator."""

import json
import tomllib
from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from devstart.generators.project import generate_project

if TYPE_CHECKING:
    from pathlib import Path

    from devstart.config import ProjectConfig


class TestDirectoryStructure:
    def test_project_structure(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"

        # Core files
        assert (root / "pyproject.toml").is_file()
        assert (root / "README.md").is_file()
        assert (root / ".gitignore").is_file()
        assert (root / "Makefile").is_file()
        assert (root / ".env").is_file()
        assert (root / ".python-version").is_file()
        assert (root / ".env.example").is_file()

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

        # CI
        assert (root / ".github" / "workflows" / "ci.yml").is_file()

        # Devcontainer
        assert (root / ".devcontainer" / "devcontainer.json").is_file()
        assert (root / ".devcontainer" / "docker-compose.yml").is_file()

        # Pre-commit
        assert (root / ".pre-commit-config.yaml").is_file()

        # Diagrams
        assert (root / "docs" / "diagrams" / "class_diagram.puml").is_file()

        # Docker
        assert (root / "docker" / "Dockerfile").is_file()
        assert (root / "docker" / "docker-compose.yml").is_file()
        assert (root / "docker" / "docker-compose.prod.yml").is_file()
        assert (root / ".dockerignore").is_file()


class TestTemplateRendering:
    def test_pyproject_contains_project_name(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / "pyproject.toml").read_text()
        assert 'name = "testproject"' in content

    def test_pyproject_contains_description(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / "pyproject.toml").read_text()
        assert 'description = "A test project"' in content

    def test_pyproject_contains_author(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / "pyproject.toml").read_text()
        assert 'authors = [{ name = "Test Author" }]' in content

    def test_pyproject_contains_python_version(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / "pyproject.toml").read_text()
        assert 'requires-python = ">=3.14"' in content

    def test_pyproject_ruff_config(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / "pyproject.toml").read_text()
        assert "[tool.ruff]" in content
        assert 'target-version = "py314"' in content
        assert "line-length = 88" in content
        assert '"TC"' in content

    def test_pyproject_mypy_strict(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / "pyproject.toml").read_text()
        assert "[tool.mypy]" in content
        assert "strict = true" in content

    def test_pyproject_pytest_config(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / "pyproject.toml").read_text()
        assert "[tool.pytest.ini_options]" in content
        assert 'testpaths = ["tests"]' in content
        assert 'pythonpath = ["src"]' in content

    def test_pyproject_contains_rich_dependency(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / "pyproject.toml").read_text()
        assert '"rich>=13.0.0"' in content

    def test_pyproject_contains_precommit_dep(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / "pyproject.toml").read_text()
        assert "pre-commit" in content

    def test_readme_contains_project_name(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / "README.md").read_text()
        assert "# testproject" in content

    def test_readme_docker_section(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / "README.md").read_text()
        assert "## Docker" in content

    def test_readme_diagrams_section(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / "README.md").read_text()
        assert "## Diagrams" in content

    def test_readme_release_section(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / "README.md").read_text()
        assert "## Release" in content
        assert "make release VERSION=1.0.0" in content

    def test_readme_docker_commands(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / "README.md").read_text()
        assert "make docker-up" in content
        assert "make docker-up-prod" in content
        assert "make docker-down" in content

    def test_vscode_launch_json(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".vscode" / "launch.json").read_text()
        assert '"Debug Module"' in content
        assert '"Debug Current File"' in content
        assert '"debugpy"' in content
        assert '"testproject"' in content

    def test_ci_uses_precommit_action(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".github" / "workflows" / "ci.yml").read_text()
        assert "pre-commit/action@v3.0.1" in content

    def test_precommit_hooks(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
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

    def test_precommit_mypy_local_hook(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".pre-commit-config.yaml").read_text()
        assert "id: mypy" in content
        assert "entry: uv run mypy src/" in content
        assert "language: system" in content
        assert "pass_filenames: false" in content

    def test_precommit_pytest_local_hook(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".pre-commit-config.yaml").read_text()
        assert "id: pytest" in content
        assert "uv run pytest" in content
        assert "--cov=src/testproject" in content
        assert "language: system" in content
        assert "pass_filenames: false" in content

    def test_different_python_version(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        config = replace(
            default_config, python_version="3.13", python_version_full="3.13.5"
        )
        generate_project(config)
        root = tmp_project_dir / "testproject"
        pyproject = (root / "pyproject.toml").read_text()
        assert 'requires-python = ">=3.13"' in pyproject
        assert 'target-version = "py313"' in pyproject

    def test_makefile_targets(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / "Makefile").read_text()
        assert "setup:" in content
        assert "lint:" in content
        assert "format:" in content
        assert "type-check:" in content
        assert "test:" in content
        assert "check:" in content
        assert "clean:" in content
        assert "dev:" in content
        assert "uv run python -m testproject" in content
        assert "core.hooksPath .githooks" in content

    def test_makefile_docker_targets(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / "Makefile").read_text()
        assert "docker-up:" in content
        assert "docker-down:" in content
        assert "docker-build:" in content
        assert "docker-logs:" in content
        assert "docker-ps:" in content
        assert "docker-up-prod:" in content
        assert "docker-down-prod:" in content

    def test_makefile_diagrams_targets(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / "Makefile").read_text()
        assert "diagrams:" in content
        assert "diagrams-svg:" in content
        assert "diagrams-clean:" in content

    def test_makefile_release_targets(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / "Makefile").read_text()
        assert "release:" in content
        assert "tag:" in content


class TestScaffoldIntoCwd:
    def test_use_cwd_creates_in_current_dir(
        self,
        tmp_project_dir: Path,
        default_config: ProjectConfig,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        empty_dir = tmp_project_dir / "workdir"
        empty_dir.mkdir()
        monkeypatch.chdir(empty_dir)
        config = replace(default_config, should_use_cwd=True)
        generate_project(config)
        assert (empty_dir / "pyproject.toml").is_file()
        assert (empty_dir / "src" / "testproject" / "main.py").is_file()

    def test_use_cwd_non_empty_raises(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        (tmp_project_dir / "somefile.txt").write_text("hello")
        config = replace(default_config, should_use_cwd=True)
        with pytest.raises(FileExistsError):
            generate_project(config)


class TestGeneratedFileContent:
    def test_pyproject_has_debugpy_dev_dependency(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / "pyproject.toml").read_text()
        assert "debugpy" in content

    def test_vscode_settings_content(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".vscode" / "settings.json").read_text()
        assert '"editor.formatOnSave": true' in content
        assert '"charliermarsh.ruff"' in content
        assert '"python.testing.pytestEnabled": true' in content
        assert "plantuml.render" in content
        assert "plantuml.server" in content
        assert '"ruff.importStrategy": "fromEnvironment"' in content
        assert '"mypy-type-checker.importStrategy": "fromEnvironment"' in content

    def test_devcontainer_uses_recommended_extensions(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        import json
        import re

        from devstart.defaults import RECOMMENDED_VSCODE_EXTENSIONS

        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        devcontainer_text = (
            root / ".devcontainer" / "devcontainer.json"
        ).read_text()
        match = re.search(
            r'"extensions":\s*(\[[^\]]*\])', devcontainer_text, re.DOTALL
        )
        assert match is not None, "devcontainer.json missing extensions array"
        assert json.loads(match.group(1)) == RECOMMENDED_VSCODE_EXTENSIONS

    def test_devcontainer_extensions(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
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
            "jebbs.plantuml",
        ]
        for ext in expected_extensions:
            assert ext in content, f"Missing extension: {ext}"

    def test_devcontainer_docker_compose(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".devcontainer" / "devcontainer.json").read_text()
        assert "docker-compose.yml" in content
        assert '"service"' in content

    def test_devcontainer_docker_in_docker(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".devcontainer" / "devcontainer.json").read_text()
        assert "docker-outside-of-docker" in content
        assert "ms-azuretools.vscode-docker" in content

    def test_class_diagram_puml_content(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / "docs" / "diagrams" / "class_diagram.puml").read_text()
        assert "@startuml" in content
        assert "@enduml" in content
        assert "testproject" in content
        assert "abstract class BaseService" in content
        assert "interface Repository" in content
        assert "BaseService <|-- AppService" in content

    def test_dockerfile_content(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / "docker" / "Dockerfile").read_text()
        assert "COPY pyproject.toml" in content
        assert "COPY README.md" in content
        assert "COPY src/" in content
        assert "python:3.14.2-slim" in content
        assert '"testproject"' in content

    def test_python_version_file_uses_patch(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        assert (root / ".python-version").read_text().strip() == "3.14.2"

    def test_docker_compose_prod_has_app_service(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / "docker" / "docker-compose.prod.yml").read_text()
        assert "app:" in content
        assert "env_file" in content

    def test_env_example_generated(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        assert (root / ".env.example").is_file()

    def test_gitignore_diagrams_entries(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".gitignore").read_text()
        assert "docs/diagrams/*.png" in content
        assert "docs/diagrams/*.svg" in content

    def test_pyproject_uses_dynamic_version(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / "pyproject.toml").read_text()
        assert 'dynamic = ["version"]' in content

    def test_pyproject_has_hatch_version_config(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / "pyproject.toml").read_text()
        assert "[tool.hatch.version]" in content
        assert 'path = "src/testproject/__init__.py"' in content

    def test_init_exports_version(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / "src" / "testproject" / "__init__.py").read_text()
        assert '__version__ = "0.1.0"' in content

    def test_init_exports_app_name(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / "src" / "testproject" / "__init__.py").read_text()
        assert '__app_name__ = "testproject"' in content


class TestGeneratedFilesParseable:
    def test_pyproject_is_valid_toml(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / "pyproject.toml").read_bytes()
        parsed = tomllib.loads(content.decode())
        assert parsed["project"]["name"] == "testproject"

    def test_launch_json_is_valid_json(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        content = (root / ".vscode" / "launch.json").read_text()
        parsed = json.loads(content)
        assert "configurations" in parsed

    def test_pyproject_dynamic_version_valid_toml(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        generate_project(default_config)
        root = tmp_project_dir / "testproject"
        raw = (root / "pyproject.toml").read_bytes()
        parsed = tomllib.loads(raw.decode())
        assert "version" in parsed["project"]["dynamic"]
        assert "version" not in parsed["project"]
        hatch_path = parsed["tool"]["hatch"]["version"]["path"]
        assert hatch_path == "src/testproject/__init__.py"


class TestTomlEscaping:
    def test_description_with_quotes_produces_valid_toml(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        config = replace(default_config, description='A "cool" project')
        generate_project(config)
        root = tmp_project_dir / "testproject"
        raw = (root / "pyproject.toml").read_bytes()
        parsed = tomllib.loads(raw.decode())
        assert parsed["project"]["description"] == 'A "cool" project'

    def test_author_with_quotes_produces_valid_toml(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        config = replace(default_config, author='O\'Brien "Bob"')
        generate_project(config)
        root = tmp_project_dir / "testproject"
        raw = (root / "pyproject.toml").read_bytes()
        parsed = tomllib.loads(raw.decode())
        assert parsed["project"]["authors"][0]["name"] == 'O\'Brien "Bob"'


class TestEdgeCases:
    def test_existing_directory_raises(
        self, tmp_project_dir: Path, default_config: ProjectConfig
    ) -> None:
        (tmp_project_dir / "testproject").mkdir()
        with pytest.raises(FileExistsError):
            generate_project(default_config)
