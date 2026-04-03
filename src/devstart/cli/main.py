"""Typer CLI entry point for devstart."""

import keyword
import re
import sys
from pathlib import Path
from typing import Annotated

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


def version_callback(value: bool) -> None:
    """Print version and exit when --version flag is passed."""
    if value:
        console.print(f"[heading]{__app_name__}[/heading] [dim]v{__version__}[/dim]")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-v",
            help="Show version and exit.",
            callback=version_callback,
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
        name, description, author, python, no_interactive,
    )
    _validate_project_name(config.project_name)
    _print_config_summary(config)
    created: list[Path] = _generate_with_status(config)
    _print_file_tree(config.project_name, created)
    _print_success(config)


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
        resolved_name, should_use_cwd = _resolve_cwd_project_name()

    partial: dict[str, str | bool | None] = {
        "name": resolved_name,
        "description": description,
        "author": author,
        "python": python,
    }

    if is_non_interactive:
        partial = _apply_non_interactive_defaults(partial)
    else:
        partial = prompt_for_config(partial)

    return _partial_to_config(partial, should_use_cwd)


def _resolve_cwd_project_name() -> tuple[str, bool]:
    """Derive a valid project name from the current directory."""
    cwd: Path = Path.cwd()
    converted: str = re.sub(r"[^a-zA-Z0-9_]", "_", cwd.name)
    if not converted:
        converted = DEFAULT_PROJECT_NAME
    elif converted[0].isdigit():
        converted = f"_{converted}"
    return converted, True


def _apply_non_interactive_defaults(
    partial: dict[str, str | bool | None],
) -> dict[str, str | bool | None]:
    """Fill missing values with sensible defaults."""
    partial["name"] = partial["name"] or DEFAULT_PROJECT_NAME
    partial["description"] = partial["description"] or DEFAULT_DESCRIPTION
    partial["author"] = partial["author"] or DEFAULT_AUTHOR
    return partial


def _partial_to_config(
    partial: dict[str, str | bool | None],
    should_use_cwd: bool,
) -> ProjectConfig:
    """Convert a fully-populated partial dict into a ProjectConfig."""
    project_name: str | bool | None = partial["name"]
    if not isinstance(project_name, str):
        console.print("\n[error]✘ Project name is required.[/error]")
        raise typer.Exit(code=1)

    python_version: str | bool | None = partial["python"]
    if not isinstance(python_version, str):
        console.print("\n[error]✘ Python version is required (use --python).[/error]")
        raise typer.Exit(code=1)

    return ProjectConfig(
        project_name=project_name,
        description=str(partial["description"]),
        author=str(partial["author"]),
        python_version=python_version,
        should_use_cwd=should_use_cwd,
    )


def _generate_with_status(config: ProjectConfig) -> list[Path]:
    """Run project generation with a Rich spinner and error handling."""
    console.print()
    try:
        with console.status(
            "[heading]Generating project...[/heading]",
            spinner="dots",
        ):
            return generate_project(config)
    except FileExistsError as error:
        console.print(f"\n[error]  ✘ {error}[/error]")
        raise typer.Exit(code=1) from error
    except OSError as error:
        console.print(f"\n[error]  ✘ {error}[/error]")
        raise typer.Exit(code=1) from error


def _print_config_summary(config: ProjectConfig) -> None:
    """Print a Rich table summarising the project configuration."""
    console.print()
    console.rule("[heading]Configuration[/heading]")
    console.print()

    table: Table = _build_config_table(config)
    console.print(table)


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


def _print_file_tree(project_name: str, created: list[Path]) -> None:
    """Print a Rich tree of all generated files."""
    console.print()
    console.rule("[heading]Project Structure[/heading]")
    console.print()

    tree = Tree(
        f"[bold bright_blue]{project_name}/[/bold bright_blue]",
        guide_style="bright_blue",
    )

    nodes: dict[str, Tree] = {}
    for path in sorted(created):
        parts: tuple[str, ...] = path.parts
        current: Tree = tree
        for index, part in enumerate(parts):
            key: str = "/".join(parts[: index + 1])
            if key not in nodes:
                is_file: bool = index == len(parts) - 1
                label: str = f"[green]{part}[/green]" if is_file else f"[bold]{part}/[/bold]"
                nodes[key] = current.add(label)
            current = nodes[key]

    console.print(tree)


def _print_success(config: ProjectConfig) -> None:
    """Print the success panel with next-steps instructions."""
    console.print()

    cd_cmd: str = f"cd {config.project_name}" if not config.should_use_cwd else ""
    steps_lines: list[str] = []
    if cd_cmd:
        steps_lines.append(f"  [bold]$[/bold] {cd_cmd}")
    steps_lines.append("  [bold]$[/bold] make setup")
    steps_lines.append(f"  [bold]$[/bold] uv run python -m {config.project_name}")
    steps: str = "\n".join(steps_lines)

    console.print(
        Panel(
            f"[success]✔ Project [bold]'{config.project_name}'[/bold]"
            f" created successfully![/success]"
            f"\n\n[dim]Next steps:[/dim]\n{steps}",
            border_style="green",
            padding=(1, 2),
            expand=False,
        )
    )


_RESERVED_NAMES: set[str] = {
    "__init__",
    "__main__",
    "__pycache__",
    "test",
    "tests",
    "setup",
    "site",
}


def _validate_project_name(name: str) -> None:
    """Validate that the project name is a valid Python identifier."""
    _reject_invalid_identifier(name)
    _reject_python_keyword(name)
    _reject_dunder_name(name)
    _reject_reserved_name(name)


def _reject_invalid_identifier(name: str) -> None:
    """Exit if name is not a valid Python identifier."""
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name):
        suggestion: str = re.sub(r"[^a-zA-Z0-9_]", "_", name)
        console.print(
            f"\n[error]✘ Invalid project name '{name}'.[/error]"
            f" Only letters, digits, and underscores"
            f" are allowed (cannot start with a digit)."
            f" Hint: try [bold]'{suggestion}'[/bold]."
        )
        raise typer.Exit(code=1)


def _reject_python_keyword(name: str) -> None:
    """Exit if name is a Python keyword."""
    if keyword.iskeyword(name):
        console.print(
            f"\n[error]✘ Invalid project name '{name}'.[/error]"
            f" Python keywords are not allowed."
        )
        raise typer.Exit(code=1)


def _reject_dunder_name(name: str) -> None:
    """Exit if name is a dunder name."""
    if name.startswith("__") and name.endswith("__"):
        console.print(
            f"\n[error]✘ Invalid project name '{name}'.[/error]"
            f" Dunder names are reserved by Python."
        )
        raise typer.Exit(code=1)


def _reject_reserved_name(name: str) -> None:
    """Exit if name conflicts with stdlib or reserved names."""
    if name in _RESERVED_NAMES or name in sys.stdlib_module_names:
        console.print(
            f"\n[error]✘ Invalid project name '{name}'.[/error]"
            f" This name conflicts with a Python"
            f" standard library module or reserved name."
        )
        raise typer.Exit(code=1)
