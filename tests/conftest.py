"""Shared test fixtures for devstart."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any


@pytest.fixture
def tmp_project_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Provide a temporary directory and cd into it for project generation."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def full_config() -> dict[str, Any]:
    """Return a complete project configuration with all features enabled."""
    return {
        "name": "testproject",
        "description": "A test project",
        "author": "Test Author",
        "python": "3.14",
        "ci": True,
        "devcontainer": True,
        "precommit": True,
        "docker": True,
        "diagrams": True,
        "_use_cwd": False,
    }


@pytest.fixture
def minimal_config() -> dict[str, Any]:
    """Return a minimal project configuration with optional features disabled."""
    return {
        "name": "testproject",
        "description": "A test project",
        "author": "Test Author",
        "python": "3.14",
        "ci": False,
        "devcontainer": False,
        "precommit": False,
        "docker": False,
        "diagrams": False,
        "_use_cwd": False,
    }
