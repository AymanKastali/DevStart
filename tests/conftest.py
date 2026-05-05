"""Shared test fixtures for devstart."""

from typing import TYPE_CHECKING

import pytest

from devstart.config import ProjectConfig

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def tmp_project_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Provide a temporary directory and cd into it for project generation."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def default_config() -> ProjectConfig:
    """Return a default project configuration."""
    return ProjectConfig(
        project_name="testproject",
        workspace_dir_name="testproject",
        description="A test project",
        author="Test Author",
        python_version="3.14",
        python_version_full="3.14.2",
        should_use_cwd=False,
    )
