"""Tests for devstart CLI invocation."""

from typing import TYPE_CHECKING

from typer.testing import CliRunner

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

from devstart import __version__
from devstart.cli.main import app

runner = CliRunner()


class TestVersion:
    def test_version_flag(self):
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert __version__ in result.output

    def test_version_short_flag(self):
        result = runner.invoke(app, ["-v"])
        assert result.exit_code == 0
        assert __version__ in result.output


class TestNewWithFlags:
    def test_new_with_all_flags(self, tmp_project_dir: Path):
        result = runner.invoke(
            app,
            [
                "new",
                "myapp",
                "-d",
                "My app description",
                "-a",
                "John Doe",
                "--python",
                "3.13",
                "-y",
            ],
        )
        assert result.exit_code == 0
        project_dir = tmp_project_dir / "myapp"
        assert project_dir.is_dir()
        assert (project_dir / "pyproject.toml").is_file()
        assert (project_dir / "src" / "myapp" / "main.py").is_file()

    def test_new_no_interactive_defaults(self, tmp_project_dir: Path):
        result = runner.invoke(app, ["new", "--python", "3.14", "-y"])
        assert result.exit_code == 0
        project_dir = tmp_project_dir / "myproject"
        assert project_dir.is_dir()

    def test_new_with_name_only_no_interactive(self, tmp_project_dir: Path):
        result = runner.invoke(app, ["new", "coolproject", "--python", "3.14", "-y"])
        assert result.exit_code == 0
        project_dir = tmp_project_dir / "coolproject"
        assert project_dir.is_dir()

    def test_new_generates_all_components(self, tmp_project_dir: Path):
        result = runner.invoke(app, ["new", "myapp", "--python", "3.14", "-y"])
        assert result.exit_code == 0
        project_dir = tmp_project_dir / "myapp"
        assert (project_dir / "docs" / "diagrams" / "class_diagram.puml").is_file()
        assert (project_dir / ".github" / "workflows" / "ci.yml").is_file()
        assert (project_dir / ".devcontainer" / "devcontainer.json").is_file()
        assert (project_dir / ".pre-commit-config.yaml").is_file()
        assert (project_dir / "docker" / "Dockerfile").is_file()

    def test_new_no_interactive_without_python_fails(self, tmp_project_dir: Path):
        result = runner.invoke(app, ["new", "myapp", "-y"])
        assert result.exit_code == 1


class TestProjectNameValidation:
    def test_invalid_name_starts_with_digit(self, tmp_project_dir: Path):
        result = runner.invoke(app, ["new", "123bad", "--python", "3.14", "-y"])
        assert result.exit_code == 1

    def test_invalid_name_has_hyphen(self, tmp_project_dir: Path):
        result = runner.invoke(app, ["new", "my-project", "--python", "3.14", "-y"])
        assert result.exit_code == 1

    def test_invalid_name_has_spaces(self, tmp_project_dir: Path):
        result = runner.invoke(app, ["new", "my project", "--python", "3.14", "-y"])
        assert result.exit_code == 1

    def test_python_keyword_rejected(self, tmp_project_dir: Path):
        result = runner.invoke(app, ["new", "class", "--python", "3.14", "-y"])
        assert result.exit_code == 1

    def test_valid_name_with_underscores(self, tmp_project_dir: Path):
        result = runner.invoke(app, ["new", "my_project", "--python", "3.14", "-y"])
        assert result.exit_code == 0

    def test_valid_name_starting_with_underscore(self, tmp_project_dir: Path):
        result = runner.invoke(app, ["new", "_private", "--python", "3.14", "-y"])
        assert result.exit_code == 0

    def test_empty_name_uses_default(self, tmp_project_dir: Path):
        result = runner.invoke(app, ["new", "--python", "3.14", "-y"])
        assert result.exit_code == 0
        assert (tmp_project_dir / "myproject").is_dir()


class TestPythonVersionValidation:
    def test_valid_python_version(self, tmp_project_dir: Path):
        result = runner.invoke(app, ["new", "myapp", "--python", "3.13", "-y"])
        assert result.exit_code == 0

    def test_invalid_python_version_rejected(self, tmp_project_dir: Path):
        result = runner.invoke(app, ["new", "myapp", "--python", "3.11", "-y"])
        assert result.exit_code != 0


class TestReservedNameValidation:
    def test_dunder_name_rejected(self, tmp_project_dir: Path):
        result = runner.invoke(app, ["new", "__init__", "--python", "3.14", "-y"])
        assert result.exit_code == 1

    def test_stdlib_module_name_rejected(self, tmp_project_dir: Path):
        result = runner.invoke(app, ["new", "json", "--python", "3.14", "-y"])
        assert result.exit_code == 1

    def test_non_stdlib_name_accepted(self, tmp_project_dir: Path):
        result = runner.invoke(app, ["new", "myapp", "--python", "3.14", "-y"])
        assert result.exit_code == 0


class TestScaffoldIntoCwd:
    def test_new_dot_uses_cwd(
        self, tmp_project_dir: Path, monkeypatch: pytest.MonkeyPatch
    ):
        empty_dir = tmp_project_dir / "scaffold_here"
        empty_dir.mkdir()
        monkeypatch.chdir(empty_dir)
        result = runner.invoke(app, ["new", ".", "--python", "3.14", "-y"])
        assert result.exit_code == 0
        assert (empty_dir / "pyproject.toml").is_file()
        assert (empty_dir / "src").is_dir()

    def test_new_dot_digit_directory_prepends_underscore(
        self, tmp_project_dir: Path, monkeypatch: pytest.MonkeyPatch
    ):
        digit_dir = tmp_project_dir / "2cool"
        digit_dir.mkdir()
        monkeypatch.chdir(digit_dir)
        result = runner.invoke(app, ["new", ".", "--python", "3.14", "-y"])
        assert result.exit_code == 0
        assert (digit_dir / "pyproject.toml").is_file()
        assert (digit_dir / "src" / "_2cool" / "main.py").is_file()

    def test_new_dot_non_empty_fails(self, tmp_project_dir: Path):
        (tmp_project_dir / "existing_file.txt").write_text("hello")
        result = runner.invoke(app, ["new", ".", "--python", "3.14", "-y"])
        assert result.exit_code == 1


class TestExistingDirectory:
    def test_existing_directory_fails(self, tmp_project_dir: Path):
        (tmp_project_dir / "myapp").mkdir()
        result = runner.invoke(app, ["new", "myapp", "--python", "3.14", "-y"])
        assert result.exit_code == 1
