"""Rich-based interactive prompts for project configuration."""

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, InvalidResponse, Prompt
from rich.theme import Theme

from devstart.defaults import (
    DEFAULT_AUTHOR,
    DEFAULT_DESCRIPTION,
    DEFAULT_PROJECT_NAME,
    DEFAULT_PYTHON_VERSION,
)

_theme = Theme(
    {
        "heading": "bold bright_blue",
        "prompt.invalid": "bold red",
    }
)

console = Console(theme=_theme, highlight=False)


class _StyledConfirm(Confirm):
    """Confirm prompt with a styled error message."""

    def on_validate_error(self, value: str, error: InvalidResponse) -> None:
        """Print a styled error showing the invalid value."""
        self.console.print(
            f'  [bold red]✘[/bold red] [red]"{value}"[/red]'
            " is not valid — expected"
            " [bold]y[/bold] (yes) or [bold]n[/bold] (no)"
        )


class _StyledPrompt(Prompt):
    """Text prompt with a styled error for empty input."""

    def on_validate_error(self, value: str, error: InvalidResponse) -> None:
        """Print a styled error and let the prompt re-ask."""
        self.console.print("[bold red]✘[/bold red] Please enter a value")


def prompt_for_config(config: dict[str, Any]) -> dict[str, Any]:
    """Prompt for any missing configuration values using Rich prompts.

    Only prompts for values not already provided via CLI flags.
    """
    console.print()
    console.print(
        Panel.fit(
            "[heading]devstart[/heading] [dim]—[/dim] Project Setup",
            border_style="bright_blue",
            padding=(0, 2),
        )
    )
    console.print()

    if config.get("name") is None:
        config["name"] = _StyledPrompt.ask(
            "  [bold]Project name[/bold]",
            default=DEFAULT_PROJECT_NAME,
        )

    if config.get("description") is None:
        config["description"] = _StyledPrompt.ask(
            "  [bold]Project description[/bold]",
            default=DEFAULT_DESCRIPTION,
        )

    if config.get("author") is None:
        config["author"] = _StyledPrompt.ask(
            "  [bold]Author name[/bold]",
            default=DEFAULT_AUTHOR,
        )

    if config.get("python") is None:
        config["python"] = _StyledPrompt.ask(
            "  [bold]Python version[/bold]",
            default=DEFAULT_PYTHON_VERSION,
        )

    console.print()

    if config.get("ci") is None:
        config["ci"] = _StyledConfirm.ask(
            "  [bold]Include GitHub Actions CI?[/bold]",
            default=True,
        )

    if config.get("devcontainer") is None:
        config["devcontainer"] = _StyledConfirm.ask(
            "  [bold]Include devcontainer setup?[/bold]",
            default=True,
        )

    if config.get("precommit") is None:
        config["precommit"] = _StyledConfirm.ask(
            "  [bold]Include pre-commit hooks?[/bold]",
            default=True,
        )

    if config.get("docker") is None:
        config["docker"] = _StyledConfirm.ask(
            "  [bold]Include Docker setup?[/bold]",
            default=True,
        )

    if config.get("diagrams") is None:
        config["diagrams"] = _StyledConfirm.ask(
            "  [bold]Include PlantUML diagram templates?[/bold]",
            default=True,
        )

    return config
