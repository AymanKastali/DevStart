"""Typer CLI entry point for devstart."""

import keyword
import re
import sys
from pathlib import Path
from typing import Annotated, NoReturn

import click
import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme
from rich.tree import Tree

from devstart import __app_name__, __version__
from devstart.config import ProjectConfig
from devstart.defaults import (
    DEFAULT_AUTHOR,
    DEFAULT_DESCRIPTION,
    DEFAULT_PROJECT_NAME,
    SUPPORTED_PYTHON_VERSIONS,
)
from devstart.generators.project import generate_project
from devstart.prompts.interactive import prompt_for_config

_RESERVED_NAMES: set[str] = {
    "__init__",
    "__main__",
    "__pycache__",
    "test",
    "tests",
    "setup",
    "site",
}

_VALID_IDENTIFIER_PATTERN: re.Pattern[str] = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
_NON_IDENTIFIER_CHARS_PATTERN: re.Pattern[str] = re.compile(r"[^a-zA-Z0-9_]")

_theme = Theme(
    {
        "info": "cyan",
        "success": "bold green",
        "error": "bold red",
        "heading": "bold bright_blue",
        "key": "cyan",
        "value": "white",
        "dim": "dim",
    }
)

console = Console(theme=_theme, highlight=False)

app = typer.Typer(
    name="devstart",
    help="Scaffold Python projects with all dev tooling pre-configured.",
    no_args_is_help=True,
)


def _print_version_and_exit(value: bool) -> None:
    """Print version and exit when --version flag is passed."""
    if value:
        console.print(f"[heading]{__app_name__}[/heading] [dim]v{__version__}[/dim]")
        raise typer.Exit()


def _exit_with_error(message: str, *, prefix: str = "") -> NoReturn:
    """Print an error message and exit with code 1."""
    console.print(f"\n[error]{prefix}✘ {message}[/error]")
    raise typer.Exit(code=1)


@app.callback()
def main(
    version: Annotated[  # noqa: ARG001 — handled by eager callback
        bool | None,
        typer.Option(
            "--version",
            "-v",
            help="Show version and exit.",
            callback=_print_version_and_exit,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """devstart — scaffold Python projects with dev tooling pre-configured."""


@app.command()
def new(
    name: Annotated[str | None, typer.Argument(help="Project name")] = None,
    description: Annotated[
        str | None,
        typer.Option("--description", "-d", help="Project description"),
    ] = None,
    author: Annotated[
        str | None,
        typer.Option("--author", "-a", help="Author name"),
    ] = None,
    python: Annotated[
        str | None,
        typer.Option(
            "--python",
            help="Python version",
            click_type=click.Choice(SUPPORTED_PYTHON_VERSIONS),
        ),
    ] = None,
    no_interactive: Annotated[
        bool,
        typer.Option(
            "--no-interactive",
            "-y",
            help="Use defaults, skip all prompts",
        ),
    ] = False,
) -> None:
    """Create a new Python project with dev tooling pre-configured."""
    config: ProjectConfig = _build_config(
        name, description, author, python, no_interactive
    )
    _validate_project_name(config.project_name)
    _print_config_summary(config)
    created_paths: list[Path] = _generate_with_spinner(config)
    _print_file_tree(config.project_name, created_paths)
    _print_success(config)


# ── Config building ───────────────────────────────────────────────────────────


def _build_config(
    name: str | None,
    description: str | None,
    author: str | None,
    python: str | None,
    is_non_interactive: bool,
) -> ProjectConfig:
    """Assemble a ProjectConfig from CLI args, prompts, or defaults."""
    resolved_name: str | None = name
    should_use_cwd: bool = False

    if name == ".":
        resolved_name, should_use_cwd = _derive_name_from_cwd()

    partial_config: dict[str, str | bool | None] = {
        "name": resolved_name,
        "description": description,
        "author": author,
        "python": python,
    }

    if is_non_interactive:
        partial_config = _apply_non_interactive_defaults(partial_config)
    else:
        partial_config = prompt_for_config(partial_config)

    return _finalize_config(partial_config, should_use_cwd)


def _derive_name_from_cwd() -> tuple[str, bool]:
    """Derive a valid project name from the current directory."""
    cwd: Path = Path.cwd()
    sanitized: str = _NON_IDENTIFIER_CHARS_PATTERN.sub("_", cwd.name)
    if not sanitized:
        sanitized = DEFAULT_PROJECT_NAME
    elif sanitized[0].isdigit():
        sanitized = f"_{sanitized}"
    return sanitized, True


def _apply_non_interactive_defaults(
    partial_config: dict[str, str | bool | None],
) -> dict[str, str | bool | None]:
    """Fill missing values with sensible defaults."""
    partial_config["name"] = partial_config["name"] or DEFAULT_PROJECT_NAME
    partial_config["description"] = partial_config["description"] or DEFAULT_DESCRIPTION
    partial_config["author"] = partial_config["author"] or DEFAULT_AUTHOR
    return partial_config


def _finalize_config(
    partial_config: dict[str, str | bool | None],
    should_use_cwd: bool,
) -> ProjectConfig:
    """Build a ProjectConfig from a fully-populated partial dict."""
    project_name: str = _require_string_field(
        partial_config, "name", "Project name is required."
    )
    python_version: str = _require_string_field(
        partial_config, "python", "Python version is required (use --python)."
    )
    workspace_dir_name: str = Path.cwd().name if should_use_cwd else project_name
    return ProjectConfig(
        project_name=project_name,
        workspace_dir_name=workspace_dir_name,
        description=str(partial_config["description"]),
        author=str(partial_config["author"]),
        python_version=python_version,
        should_use_cwd=should_use_cwd,
    )


def _require_string_field(
    partial_config: dict[str, str | bool | None],
    field_name: str,
    missing_message: str,
) -> str:
    """Return the string value of a partial-config field, exiting if absent."""
    value: str | bool | None = partial_config[field_name]
    if not isinstance(value, str):
        _exit_with_error(missing_message)
    return value


# ── Validation ────────────────────────────────────────────────────────────────


def _validate_project_name(name: str) -> None:
    """Validate that the project name is a valid Python identifier."""
    _reject_invalid_identifier(name)
    _reject_python_keyword(name)
    _reject_dunder_name(name)
    _reject_reserved_name(name)


def _reject_invalid_identifier(name: str) -> None:
    """Exit if name is not a valid Python identifier."""
    if not _VALID_IDENTIFIER_PATTERN.match(name):
        suggestion: str = _NON_IDENTIFIER_CHARS_PATTERN.sub("_", name)
        _exit_with_error(
            f"Invalid project name '{name}'."
            f" Only letters, digits, and underscores"
            f" are allowed (cannot start with a digit)."
            f" Hint: try [bold]'{suggestion}'[/bold]."
        )


def _reject_python_keyword(name: str) -> None:
    """Exit if name is a Python keyword."""
    if keyword.iskeyword(name):
        _exit_with_error(
            f"Invalid project name '{name}'. Python keywords are not allowed."
        )


def _reject_dunder_name(name: str) -> None:
    """Exit if name is a dunder name."""
    if name.startswith("__") and name.endswith("__"):
        _exit_with_error(
            f"Invalid project name '{name}'. Dunder names are reserved by Python."
        )


def _reject_reserved_name(name: str) -> None:
    """Exit if name conflicts with stdlib or reserved names."""
    if name in _RESERVED_NAMES or name in sys.stdlib_module_names:
        _exit_with_error(
            f"Invalid project name '{name}'."
            f" This name conflicts with a Python"
            f" standard library module or reserved name."
        )


# ── Output: configuration summary ─────────────────────────────────────────────


def _print_config_summary(config: ProjectConfig) -> None:
    """Print a Rich table summarising the project configuration."""
    console.print()
    console.rule("[heading]Configuration[/heading]")
    console.print()
    console.print(_build_config_table(config))


def _build_config_table(config: ProjectConfig) -> Table:
    """Build a Rich table with configuration key-value rows."""
    table = Table(
        box=box.SIMPLE,
        show_header=False,
        padding=(0, 2),
        expand=False,
    )
    table.add_column("Setting", style="key")
    table.add_column("Value", style="value")
    table.add_row("Project", f"[bold]{config.project_name}[/bold]")
    table.add_row("Description", config.description)
    table.add_row("Author", config.author)
    table.add_row("Python", config.python_version)
    return table


# ── Generation with status spinner ────────────────────────────────────────────


def _generate_with_spinner(config: ProjectConfig) -> list[Path]:
    """Run project generation with a Rich spinner and error handling."""
    console.print()
    try:
        with console.status(
            "[heading]Generating project...[/heading]",
            spinner="dots",
        ):
            return generate_project(config)
    except (FileExistsError, OSError) as error:
        _exit_with_error(str(error), prefix="  ✘ ")


# ── Output: file tree ─────────────────────────────────────────────────────────


def _print_file_tree(project_name: str, created_paths: list[Path]) -> None:
    """Print a Rich tree of all generated files."""
    console.print()
    console.rule("[heading]Project Structure[/heading]")
    console.print()
    console.print(_build_file_tree(project_name, created_paths))


def _build_file_tree(project_name: str, created_paths: list[Path]) -> Tree:
    """Build a Rich Tree representation of all created paths."""
    tree = Tree(
        f"[bold bright_blue]{project_name}/[/bold bright_blue]",
        guide_style="bright_blue",
    )
    nodes_by_path_key: dict[str, Tree] = {}
    for path in sorted(created_paths):
        _add_path_to_tree(path, tree, nodes_by_path_key)
    return tree


def _add_path_to_tree(
    path: Path,
    tree_root: Tree,
    nodes_by_path_key: dict[str, Tree],
) -> None:
    """Insert each path component into the tree, reusing existing nodes."""
    current_node: Tree = tree_root
    parts: tuple[str, ...] = path.parts
    for index, part in enumerate(parts):
        path_key: str = "/".join(parts[: index + 1])
        if path_key not in nodes_by_path_key:
            is_leaf: bool = index == len(parts) - 1
            nodes_by_path_key[path_key] = current_node.add(
                _format_tree_label(part, is_leaf=is_leaf)
            )
        current_node = nodes_by_path_key[path_key]


def _format_tree_label(part: str, *, is_leaf: bool) -> str:
    """Return a styled label for a tree node based on whether it is a file."""
    if is_leaf:
        return f"[green]{part}[/green]"
    return f"[bold]{part}/[/bold]"


# ── Output: success panel ─────────────────────────────────────────────────────


def _print_success(config: ProjectConfig) -> None:
    """Print the success panel with next-steps instructions."""
    console.print()
    console.print(_build_success_panel(config))


def _build_success_panel(config: ProjectConfig) -> Panel:
    """Build the success panel summarising completion and next steps."""
    next_steps: str = _format_next_steps(config)
    body: str = (
        f"[success]✔ Project [bold]'{config.project_name}'[/bold]"
        f" created successfully![/success]"
        f"\n\n[dim]Next steps:[/dim]\n{next_steps}"
    )
    return Panel(
        body,
        border_style="green",
        padding=(1, 2),
        expand=False,
    )


def _format_next_steps(config: ProjectConfig) -> str:
    """Return the indented, newline-joined list of next-step shell commands."""
    next_step_lines: list[str] = []
    if not config.should_use_cwd:
        next_step_lines.append(f"  [bold]$[/bold] cd {config.project_name}")
    next_step_lines.append("  [bold]$[/bold] make setup")
    next_step_lines.append(f"  [bold]$[/bold] uv run python -m {config.project_name}")
    return "\n".join(next_step_lines)
