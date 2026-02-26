"""Project generator — orchestrates Python project scaffolding."""

from pathlib import Path
from typing import Any

from jinja2 import Environment, PackageLoader, select_autoescape

TEMPLATE_ENV = Environment(
    loader=PackageLoader("devstart", "templates"),
    autoescape=select_autoescape(),
    keep_trailing_newline=True,
)


def _escape_toml_string(value: str) -> str:
    """Escape backslashes and double quotes for TOML basic strings."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _render(template_path: str, context: dict[str, Any]) -> str:
    """Render a Jinja2 template with the given context."""
    template = TEMPLATE_ENV.get_template(template_path)
    return template.render(**context)


def _write_file(
    path: Path,
    content: str,
    *,
    root: Path,
    created: list[Path],
) -> None:
    """Write content to a file, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    created.append(path.relative_to(root))


def _write_init(path: Path, *, root: Path, created: list[Path]) -> None:
    """Write an empty __init__.py file."""
    _write_file(path / "__init__.py", "", root=root, created=created)


def generate_project(config: dict[str, Any]) -> list[Path]:
    """Generate a complete Python project with dev tooling.

    Args:
        config: Project configuration dict with keys:
            name, description, author, python, ci,
            devcontainer, precommit, docker

    Returns:
        List of relative paths to all created files.
    """
    name = config["name"]

    if config.get("_use_cwd"):
        root = Path.cwd()
        if any(p for p in root.iterdir() if p.name != ".git"):
            raise FileExistsError(
                f"Current directory '{root}' is not empty. "
                "Use '.' only in an empty directory."
            )
    else:
        root = Path.cwd() / name
        if root.exists():
            raise FileExistsError(
                f"Directory '{name}' already exists. "
                "Remove it or choose a different name."
            )

    src = root / "src" / name
    created: list[Path] = []

    context = {
        "project_name": name,
        "description": _escape_toml_string(config["description"]),
        "author": _escape_toml_string(config["author"]),
        "python_version": config["python"],
        "ci": config["ci"],
        "devcontainer": config["devcontainer"],
        "precommit": config["precommit"],
        "docker": config["docker"],
        "diagrams": config["diagrams"],
        "continue": config["continue"],
    }

    _generate_source_tree(src, context, root=root, created=created)
    _generate_tests(root, context, created=created)
    _generate_root_files(root, context, created=created)
    _generate_vscode(root, context, created=created)
    if config["continue"]:
        _generate_continue(root, context, created=created)

    if config["docker"]:
        _generate_docker(root, context, created=created)

    if config["ci"]:
        _generate_ci(root, context, created=created)

    if config["devcontainer"]:
        _generate_devcontainer(root, context, created=created)

    if config["precommit"]:
        _generate_precommit(root, context, created=created)

    if config["diagrams"]:
        _generate_diagrams(root, context, created=created)

    return created


def _generate_source_tree(
    src: Path,
    context: dict[str, Any],
    *,
    root: Path,
    created: list[Path],
) -> None:
    """Generate the src/<project>/ directory tree."""
    _write_file(
        src / "__init__.py",
        _render("base/init.py.j2", context),
        root=root,
        created=created,
    )
    _write_file(
        src / "__main__.py",
        _render("base/__main__.py.j2", context),
        root=root,
        created=created,
    )
    _write_file(
        src / "main.py",
        _render("base/main.py.j2", context),
        root=root,
        created=created,
    )


def _generate_tests(
    root: Path,
    context: dict[str, Any],
    *,
    created: list[Path],
) -> None:
    """Generate the test directory structure."""
    tests = root / "tests"

    _write_init(tests, root=root, created=created)
    _write_file(
        tests / "conftest.py",
        _render("base/conftest.py.j2", context),
        root=root,
        created=created,
    )
    _write_file(
        tests / "test_main.py",
        _render("base/test_main.py.j2", context),
        root=root,
        created=created,
    )


def _generate_root_files(
    root: Path,
    context: dict[str, Any],
    *,
    created: list[Path],
) -> None:
    """Generate root-level project files."""
    _write_file(
        root / "pyproject.toml",
        _render("base/pyproject.toml.j2", context),
        root=root,
        created=created,
    )
    _write_file(
        root / "README.md",
        _render("base/README.md.j2", context),
        root=root,
        created=created,
    )
    _write_file(
        root / ".gitignore",
        _render("base/gitignore.j2", context),
        root=root,
        created=created,
    )
    _write_file(
        root / "Makefile",
        _render("base/Makefile.j2", context),
        root=root,
        created=created,
    )
    _write_file(
        root / ".env",
        _render("base/env.j2", context),
        root=root,
        created=created,
    )


def _generate_vscode(
    root: Path,
    context: dict[str, Any],
    *,
    created: list[Path],
) -> None:
    """Generate .vscode configuration files."""
    vscode = root / ".vscode"
    _write_file(
        vscode / "launch.json",
        _render("base/vscode_launch.json.j2", context),
        root=root,
        created=created,
    )
    _write_file(
        vscode / "settings.json",
        _render("base/vscode_settings.json.j2", context),
        root=root,
        created=created,
    )


def _generate_continue(
    root: Path,
    context: dict[str, Any],
    *,
    created: list[Path],
) -> None:
    """Generate .continue/config.yaml for local AI assistant."""
    _write_file(
        root / ".continue" / "config.yaml",
        _render("base/continue_config.yaml.j2", context),
        root=root,
        created=created,
    )


def _generate_docker(
    root: Path,
    context: dict[str, Any],
    *,
    created: list[Path],
) -> None:
    """Generate Docker and Docker Compose files."""
    docker = root / "docker"
    _write_file(
        docker / "Dockerfile",
        _render("docker/Dockerfile.j2", context),
        root=root,
        created=created,
    )
    _write_file(
        docker / "docker-compose.yml",
        _render("docker/docker-compose.yml.j2", context),
        root=root,
        created=created,
    )
    _write_file(
        root / ".dockerignore",
        _render("docker/dockerignore.j2", context),
        root=root,
        created=created,
    )


def _generate_ci(
    root: Path,
    context: dict[str, Any],
    *,
    created: list[Path],
) -> None:
    """Generate GitHub Actions CI workflow."""
    ci = root / ".github" / "workflows"
    _write_file(
        ci / "ci.yml",
        _render("ci/ci.yml.j2", context),
        root=root,
        created=created,
    )


def _generate_devcontainer(
    root: Path,
    context: dict[str, Any],
    *,
    created: list[Path],
) -> None:
    """Generate devcontainer configuration."""
    devcontainer = root / ".devcontainer"
    _write_file(
        devcontainer / "devcontainer.json",
        _render("devcontainer/devcontainer.json.j2", context),
        root=root,
        created=created,
    )


def _generate_precommit(
    root: Path,
    context: dict[str, Any],
    *,
    created: list[Path],
) -> None:
    """Generate pre-commit configuration."""
    _write_file(
        root / ".pre-commit-config.yaml",
        _render("precommit/pre-commit-config.yaml.j2", context),
        root=root,
        created=created,
    )


def _generate_diagrams(
    root: Path,
    context: dict[str, Any],
    *,
    created: list[Path],
) -> None:
    """Generate PlantUML diagram templates."""
    diagrams = root / "docs" / "diagrams"
    _write_file(
        diagrams / "class_diagram.puml",
        _render("diagrams/class_diagram.puml.j2", context),
        root=root,
        created=created,
    )
