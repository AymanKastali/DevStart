"""Rich-based interactive prompts for project configuration."""

import sys
import termios
import tty

from rich.console import Console
from rich.panel import Panel
from rich.prompt import InvalidResponse, Prompt
from rich.theme import Theme

from devstart.defaults import (
    DEFAULT_AUTHOR,
    DEFAULT_DESCRIPTION,
    DEFAULT_PROJECT_NAME,
    SUPPORTED_PYTHON_VERSIONS,
)

_theme = Theme(
    {
        "heading": "bold bright_blue",
        "prompt.invalid": "bold red",
    }
)

console = Console(theme=_theme, highlight=False)


class _StyledPrompt(Prompt):
    """Text prompt with a styled error for empty input."""

    def on_validate_error(self, value: str, error: InvalidResponse) -> None:
        """Print a styled error and let the prompt re-ask."""
        self.console.print("[bold red]✘[/bold red] Please enter a value")


def _read_keypress() -> str:
    """Read a single keypress, handling multi-byte escape sequences."""
    char: str = sys.stdin.read(1)
    if char == "\x1b":
        char += sys.stdin.read(1)
        char += sys.stdin.read(1)
    return char


def _draw_options(options: list[str], selected: int) -> None:
    """Render the option list with the selected item highlighted."""
    for index, option in enumerate(options):
        if index == selected:
            console.print(f"    [bold cyan]→ {option}[/bold cyan]")
        else:
            console.print(f"      [dim]{option}[/dim]")


def _clear_options(count: int) -> None:
    """Move cursor up and clear lines to redraw options."""
    for _ in range(count):
        sys.stdout.write("\033[A\033[K")
    sys.stdout.flush()


def _select_from_list(label: str, options: list[str]) -> str:
    """Display an arrow-key navigable selector and return the chosen value."""
    console.print(f"  [bold]{label}[/bold]  [dim](↑/↓ navigate, Enter select)[/dim]")
    selected: int = 0
    _draw_options(options, selected)

    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        while True:
            key: str = _read_keypress()
            if key == "\r" or key == "\n":
                break
            if key == "\x1b[A" and selected > 0:
                selected -= 1
            elif key == "\x1b[B" and selected < len(options) - 1:
                selected += 1
            elif key == "\x03":
                raise KeyboardInterrupt
            else:
                continue
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            _clear_options(len(options))
            _draw_options(options, selected)
            tty.setraw(sys.stdin.fileno())
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    return options[selected]


def prompt_for_config(
    config: dict[str, str | bool | None],
) -> dict[str, str | bool | None]:
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
        config["python"] = _select_from_list(
            "Python version",
            SUPPORTED_PYTHON_VERSIONS,
        )

    return config
