"""Project configuration value object."""

from dataclasses import dataclass


def _escape_toml_string(value: str) -> str:
    """Escape backslashes and double quotes for TOML basic strings."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


@dataclass(frozen=True, slots=True)
class ProjectConfig:
    """Immutable project configuration used across the scaffolding pipeline."""

    project_name: str
    description: str
    author: str
    python_version: str
    should_use_cwd: bool

    def to_template_context(self) -> dict[str, str | bool]:
        """Return the dict expected by Jinja2 templates."""
        return {
            "project_name": self.project_name,
            "description": _escape_toml_string(self.description),
            "author": _escape_toml_string(self.author),
            "python_version": self.python_version,
        }
