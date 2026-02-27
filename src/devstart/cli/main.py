"""Typer CLI entry point for devstart."""

import keyword
import re
import sys
from pathlib import Path
from typing import Annotated, Any

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme
from rich.tree import Tree

from devstart import __app_name__, __version__
from devstart.defaults import (
    DEFAULT_AUTHOR,
    DEFAULT_DESCRIPTION,
    DEFAULT_PROJECT_NAME,
    DEFAULT_PYTHON_VERSION,
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
        str, typer.Option("--python", help="Python version")
    ] = DEFAULT_PYTHON_VERSION,
    ci: Annotated[
        bool | None,
        typer.Option("--ci/--no-ci", help="Include GitHub Actions CI"),
    ] = None,
    devcontainer: Annotated[
        bool | None,
        typer.Option(
            "--devcontainer/--no-devcontainer",
            help="Include devcontainer setup",
        ),
    ] = None,
    precommit: Annotated[
        bool | None,
        typer.Option(
            "--precommit/--no-precommit",
            help="Include pre-commit hooks config",
        ),
    ] = None,
    docker: Annotated[
        bool | None,
        typer.Option("--docker/--no-docker", help="Include Docker setup"),
    ] = None,
    diagrams: Annotated[
        bool | None,
        typer.Option(
            "--diagrams/--no-diagrams",
            help="Include PlantUML diagram templates",
        ),
    ] = None,
    continue_: Annotated[
        bool | None,
        typer.Option(
            "--continue/--no-continue",
            help="Include Continue local AI config",
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
    config = {
        "name": name,
        "description": description,
        "author": author,
        "python": python,
        "ci": ci,
        "devcontainer": devcontainer,
        "precommit": precommit,
        "docker": docker,
        "diagrams": diagrams,
        "continue": continue_,
    }

    # Handle "." — scaffold into the current directory
    if config["name"] == ".":
        cwd = Path.cwd()
        converted = re.sub(r"[^a-zA-Z0-9_]", "_", cwd.name)
        if not converted:
            converted = DEFAULT_PROJECT_NAME
        elif converted[0].isdigit():
            converted = f"_{converted}"
        config["name"] = converted
        config["_use_cwd"] = True
    else:
        config["_use_cwd"] = False

    if no_interactive:
        config["name"] = config["name"] or DEFAULT_PROJECT_NAME
        config["description"] = config["description"] or DEFAULT_DESCRIPTION
        config["author"] = config["author"] or DEFAULT_AUTHOR
        if config["ci"] is None:
            config["ci"] = True
        if config["devcontainer"] is None:
            config["devcontainer"] = True
        if config["precommit"] is None:
            config["precommit"] = True
        if config["docker"] is None:
            config["docker"] = True
        if config["diagrams"] is None:
            config["diagrams"] = True
        if config["continue"] is None:
            config["continue"] = True
    else:
        config = prompt_for_config(config)

    if not isinstance(config["name"], str):
        console.print("\n[error]✘ Project name is required.[/error]")
        raise typer.Exit(code=1)
    project_name: str = config["name"]
    _validate_project_name(project_name)
    _validate_python_version(str(config["python"]))

    # --- Config summary ---
    _print_config_summary(config)

    # --- Generate ---
    console.print()
    try:
        with console.status(
            "[heading]Generating project...[/heading]",
            spinner="dots",
        ):
            created = generate_project(config)
    except FileExistsError as e:
        console.print(f"\n[error]  ✘ {e}[/error]")
        raise typer.Exit(code=1) from e
    except OSError as e:
        console.print(f"\n[error]  ✘ {e}[/error]")
        raise typer.Exit(code=1) from e

    # --- File tree ---
    _print_file_tree(project_name, created)

    # --- Success ---
    _print_success(project_name, config)


def _print_config_summary(config: dict[str, Any]) -> None:
    """Print a Rich table summarising the project configuration."""
    console.print()
    console.rule("[heading]Configuration[/heading]")
    console.print()

    table = Table(
        box=box.SIMPLE,
        show_header=False,
        padding=(0, 2),
        expand=False,
    )
    table.add_column("Setting", style="key")
    table.add_column("Value", style="value")

    table.add_row("Project", f"[bold]{config['name']}[/bold]")
    table.add_row("Description", config["description"])
    table.add_row("Author", config["author"])
    table.add_row("Python", config["python"])

    _yes = "[green]yes[/green]"
    _no = "[dim]no[/dim]"
    table.add_row("CI", _yes if config["ci"] else _no)
    table.add_row("Devcontainer", _yes if config["devcontainer"] else _no)
    table.add_row("Pre-commit", _yes if config["precommit"] else _no)
    table.add_row("Docker", _yes if config["docker"] else _no)
    table.add_row("Diagrams", _yes if config["diagrams"] else _no)
    table.add_row("Continue", _yes if config["continue"] else _no)

    console.print(table)


def _print_file_tree(project_name: str, created: list[Path]) -> None:
    """Print a Rich tree of all generated files."""
    console.print()
    console.rule("[heading]Project Structure[/heading]")
    console.print()

    tree = Tree(
        f"[bold bright_blue]{project_name}/[/bold bright_blue]",
        guide_style="bright_blue",
    )

    # Build nested tree from flat relative paths
    nodes: dict[str, Tree] = {}
    for path in sorted(created):
        parts = path.parts
        current = tree
        for i, part in enumerate(parts):
            key = "/".join(parts[: i + 1])
            if key not in nodes:
                is_file = i == len(parts) - 1
                label = f"[green]{part}[/green]" if is_file else f"[bold]{part}/[/bold]"
                nodes[key] = current.add(label)
            current = nodes[key]

    console.print(tree)


def _print_success(project_name: str, config: dict[str, Any]) -> None:
    """Print the success panel with next-steps instructions."""
    console.print()

    cd_cmd = f"cd {project_name}" if not config.get("_use_cwd") else ""
    steps_lines = []
    if cd_cmd:
        steps_lines.append(f"  [bold]$[/bold] {cd_cmd}")
    steps_lines.append("  [bold]$[/bold] make setup")
    steps_lines.append(f"  [bold]$[/bold] uv run python -m {project_name}")
    steps = "\n".join(steps_lines)

    console.print(
        Panel(
            f"[success]✔ Project [bold]'{project_name}'[/bold]"
            f" created successfully![/success]"
            f"\n\n[dim]Next steps:[/dim]\n{steps}",
            border_style="green",
            padding=(1, 2),
            expand=False,
        )
    )


def _validate_python_version(version: str) -> None:
    """Validate that the Python version is in X.Y format."""
    if not re.match(r"^\d+\.\d+$", version):
        console.print(
            f"\n[error]✘ Invalid Python version"
            f" '{version}'.[/error]"
            f" Expected format: X.Y (e.g. 3.14)."
        )
        raise typer.Exit(code=1)


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
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name):
        suggestion = re.sub(r"[^a-zA-Z0-9_]", "_", name)
        console.print(
            f"\n[error]✘ Invalid project name"
            f" '{name}'.[/error]"
            f" Only letters, digits, and underscores"
            f" are allowed (cannot start with a digit)."
            f" Hint: try [bold]'{suggestion}'[/bold]."
        )
        raise typer.Exit(code=1)
    if keyword.iskeyword(name):
        console.print(
            f"\n[error]✘ Invalid project name"
            f" '{name}'.[/error]"
            f" Python keywords are not allowed."
        )
        raise typer.Exit(code=1)
    if name.startswith("__") and name.endswith("__"):
        console.print(
            f"\n[error]✘ Invalid project name"
            f" '{name}'.[/error]"
            f" Dunder names are reserved by Python."
        )
        raise typer.Exit(code=1)
    if name in _RESERVED_NAMES or name in sys.stdlib_module_names:
        console.print(
            f"\n[error]✘ Invalid project name"
            f" '{name}'.[/error]"
            f" This name conflicts with a Python"
            f" standard library module or reserved name."
        )
        raise typer.Exit(code=1)
