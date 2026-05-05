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


def prompt_for_config(
    config: dict[str, str | bool | None],
) -> dict[str, str | bool | None]:
    """Prompt for any missing configuration values using Rich prompts.

    Only prompts for values not already provided via CLI flags.
    """
    _print_setup_header()

    if config.get("name") is None:
        config["name"] = _prompt_for_text("Project name", DEFAULT_PROJECT_NAME)

    if config.get("description") is None:
        config["description"] = _prompt_for_text(
            "Project description", DEFAULT_DESCRIPTION
        )

    if config.get("author") is None:
        config["author"] = _prompt_for_text("Author name", DEFAULT_AUTHOR)

    if config.get("python") is None:
        config["python"] = _select_with_arrow_keys(
            "Python version", SUPPORTED_PYTHON_VERSIONS
        )

    return config


def _print_setup_header() -> None:
    """Print the framed devstart header above the interactive prompts."""
    console.print()
    console.print(
        Panel.fit(
            "[heading]devstart[/heading] [dim]—[/dim] Project Setup",
            border_style="bright_blue",
            padding=(0, 2),
        )
    )
    console.print()


def _prompt_for_text(label: str, default_value: str) -> str:
    """Ask the user for a text value with the given label and default."""
    return _StyledPrompt.ask(f"  [bold]{label}[/bold]", default=default_value)


def _select_with_arrow_keys(label: str, options: list[str]) -> str:
    """Display an arrow-key navigable selector and return the chosen value."""
    console.print(f"  [bold]{label}[/bold]  [dim](↑/↓ navigate, Enter select)[/dim]")
    selected_index: int = 0
    _draw_options(options, selected_index)

    saved_terminal_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        while True:
            keypress: str = _read_keypress()
            if _keypress_confirms_selection(keypress):
                break
            if keypress == _ARROW_UP and selected_index > 0:
                selected_index -= 1
            elif keypress == _ARROW_DOWN and selected_index < len(options) - 1:
                selected_index += 1
            elif keypress == _CTRL_C:
                raise KeyboardInterrupt
            else:
                continue
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, saved_terminal_settings)
            _clear_options(len(options))
            _draw_options(options, selected_index)
            tty.setraw(sys.stdin.fileno())
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, saved_terminal_settings)

    return options[selected_index]


def _keypress_confirms_selection(keypress: str) -> bool:
    """Return True if the keypress is Enter (carriage return or newline)."""
    return keypress in {"\r", "\n"}


def _read_keypress() -> str:
    """Read a single keypress, handling multi-byte escape sequences."""
    char: str = sys.stdin.read(1)
    if char == _ESCAPE:
        char += sys.stdin.read(1)
        char += sys.stdin.read(1)
    return char


def _draw_options(options: list[str], selected_index: int) -> None:
    """Render the option list with the selected item highlighted."""
    for index, option in enumerate(options):
        if index == selected_index:
            console.print(f"    [bold cyan]→ {option}[/bold cyan]")
        else:
            console.print(f"      [dim]{option}[/dim]")


def _clear_options(option_count: int) -> None:
    """Move cursor up and clear lines to redraw options."""
    for _ in range(option_count):
        sys.stdout.write("\033[A\033[K")
    sys.stdout.flush()


_ESCAPE: str = "\x1b"
_ARROW_UP: str = "\x1b[A"
_ARROW_DOWN: str = "\x1b[B"
_CTRL_C: str = "\x03"


class _StyledPrompt(Prompt):
    """Text prompt with a styled error for empty input."""

    def on_validate_error(self, value: str, error: InvalidResponse) -> None:
        """Print a styled error and let the prompt re-ask."""
        self.console.print("[bold red]✘[/bold red] Please enter a value")
