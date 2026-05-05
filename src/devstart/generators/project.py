"""Project generator — orchestrates Python project scaffolding."""

import stat
from pathlib import Path
from typing import TYPE_CHECKING

from jinja2 import Environment, PackageLoader, select_autoescape

from devstart.defaults import RECOMMENDED_VSCODE_EXTENSIONS

if TYPE_CHECKING:
    from devstart.config import ProjectConfig

TEMPLATE_ENV = Environment(
    loader=PackageLoader("devstart", "templates"),
    autoescape=select_autoescape(),
    keep_trailing_newline=True,
)


def generate_project(config: ProjectConfig) -> list[Path]:
    """Generate a complete Python project with dev tooling.

    Returns:
        List of relative paths to all created files.
    """
    project_root: Path = _resolve_project_root(config)
    package_root: Path = project_root / "src" / config.project_name
    template_context: dict[str, str | bool | list[str]] = {
        **config.to_template_context(),
        "recommended_extensions": RECOMMENDED_VSCODE_EXTENSIONS,
    }
    created_paths: list[Path] = []

    _generate_source_tree(
        package_root,
        template_context,
        project_root=project_root,
        created_paths=created_paths,
    )
    _generate_tests(project_root, template_context, created_paths=created_paths)
    _generate_root_files(project_root, template_context, created_paths=created_paths)
    _generate_vscode(project_root, template_context, created_paths=created_paths)
    _generate_docker(project_root, template_context, created_paths=created_paths)
    _generate_ci(project_root, template_context, created_paths=created_paths)
    _generate_devcontainer(project_root, template_context, created_paths=created_paths)
    _generate_precommit(project_root, template_context, created_paths=created_paths)
    _generate_diagrams(project_root, template_context, created_paths=created_paths)

    return created_paths


def _resolve_project_root(config: ProjectConfig) -> Path:
    """Determine and validate the project root directory."""
    if config.should_use_cwd:
        return _resolve_cwd_as_project_root()
    return _resolve_named_subdirectory_as_project_root(config.project_name)


def _resolve_cwd_as_project_root() -> Path:
    """Use the current directory as the root, requiring it to be empty."""
    cwd: Path = Path.cwd()
    if _directory_has_user_content(cwd):
        raise FileExistsError(
            f"Current directory '{cwd}' is not empty. "
            "Use '.' only in an empty directory."
        )
    return cwd


def _resolve_named_subdirectory_as_project_root(project_name: str) -> Path:
    """Use a new subdirectory of cwd as the root, requiring it not to exist."""
    project_root: Path = Path.cwd() / project_name
    if project_root.exists():
        raise FileExistsError(
            f"Directory '{project_name}' already exists. "
            "Remove it or choose a different name."
        )
    return project_root


def _directory_has_user_content(directory: Path) -> bool:
    """Return True if the directory contains anything other than a .git folder."""
    return any(entry for entry in directory.iterdir() if entry.name != ".git")


def _generate_source_tree(
    package_root: Path,
    template_context: dict[str, str | bool | list[str]],
    *,
    project_root: Path,
    created_paths: list[Path],
) -> None:
    """Generate the src/<project>/ directory tree."""
    _render_template_to_file(
        package_root / "__init__.py",
        "base/init.py.j2",
        template_context,
        project_root=project_root,
        created_paths=created_paths,
    )
    _render_template_to_file(
        package_root / "__main__.py",
        "base/__main__.py.j2",
        template_context,
        project_root=project_root,
        created_paths=created_paths,
    )
    _render_template_to_file(
        package_root / "main.py",
        "base/main.py.j2",
        template_context,
        project_root=project_root,
        created_paths=created_paths,
    )
    _write_file(
        package_root / "py.typed",
        "",
        project_root=project_root,
        created_paths=created_paths,
    )


def _generate_tests(
    project_root: Path,
    template_context: dict[str, str | bool | list[str]],
    *,
    created_paths: list[Path],
) -> None:
    """Generate the test directory structure."""
    tests_dir: Path = project_root / "tests"
    _write_empty_init(tests_dir, project_root=project_root, created_paths=created_paths)
    _render_template_to_file(
        tests_dir / "conftest.py",
        "base/conftest.py.j2",
        template_context,
        project_root=project_root,
        created_paths=created_paths,
    )
    _render_template_to_file(
        tests_dir / "test_main.py",
        "base/test_main.py.j2",
        template_context,
        project_root=project_root,
        created_paths=created_paths,
    )


def _generate_root_files(
    project_root: Path,
    template_context: dict[str, str | bool | list[str]],
    *,
    created_paths: list[Path],
) -> None:
    """Generate root-level project files."""
    _render_template_to_file(
        project_root / "pyproject.toml",
        "base/pyproject.toml.j2",
        template_context,
        project_root=project_root,
        created_paths=created_paths,
    )
    _render_template_to_file(
        project_root / "README.md",
        "base/README.md.j2",
        template_context,
        project_root=project_root,
        created_paths=created_paths,
    )
    _render_template_to_file(
        project_root / ".gitignore",
        "base/gitignore.j2",
        template_context,
        project_root=project_root,
        created_paths=created_paths,
    )
    _render_template_to_file(
        project_root / "Makefile",
        "base/Makefile.j2",
        template_context,
        project_root=project_root,
        created_paths=created_paths,
    )
    _render_template_to_file(
        project_root / ".env",
        "base/env.j2",
        template_context,
        project_root=project_root,
        created_paths=created_paths,
    )
    _render_template_to_file(
        project_root / ".env.example",
        "base/env.example.j2",
        template_context,
        project_root=project_root,
        created_paths=created_paths,
    )
    _render_template_to_file(
        project_root / ".python-version",
        "base/python-version.j2",
        template_context,
        project_root=project_root,
        created_paths=created_paths,
    )


def _generate_vscode(
    project_root: Path,
    template_context: dict[str, str | bool | list[str]],
    *,
    created_paths: list[Path],
) -> None:
    """Generate .vscode configuration files."""
    vscode_dir: Path = project_root / ".vscode"
    _render_template_to_file(
        vscode_dir / "launch.json",
        "base/vscode_launch.json.j2",
        template_context,
        project_root=project_root,
        created_paths=created_paths,
    )
    _render_template_to_file(
        vscode_dir / "settings.json",
        "base/vscode_settings.json.j2",
        template_context,
        project_root=project_root,
        created_paths=created_paths,
    )


def _generate_docker(
    project_root: Path,
    template_context: dict[str, str | bool | list[str]],
    *,
    created_paths: list[Path],
) -> None:
    """Generate Docker and Docker Compose files."""
    docker_dir: Path = project_root / "docker"
    _render_template_to_file(
        docker_dir / "Dockerfile",
        "docker/Dockerfile.j2",
        template_context,
        project_root=project_root,
        created_paths=created_paths,
    )
    _render_template_to_file(
        docker_dir / "docker-compose.yml",
        "docker/docker-compose.yml.j2",
        template_context,
        project_root=project_root,
        created_paths=created_paths,
    )
    _render_template_to_file(
        docker_dir / "docker-compose.prod.yml",
        "docker/docker-compose.prod.yml.j2",
        template_context,
        project_root=project_root,
        created_paths=created_paths,
    )
    _render_template_to_file(
        project_root / ".dockerignore",
        "docker/dockerignore.j2",
        template_context,
        project_root=project_root,
        created_paths=created_paths,
    )


def _generate_ci(
    project_root: Path,
    template_context: dict[str, str | bool | list[str]],
    *,
    created_paths: list[Path],
) -> None:
    """Generate GitHub Actions CI workflow."""
    workflows_dir: Path = project_root / ".github" / "workflows"
    _render_template_to_file(
        workflows_dir / "ci.yml",
        "ci/ci.yml.j2",
        template_context,
        project_root=project_root,
        created_paths=created_paths,
    )


def _generate_devcontainer(
    project_root: Path,
    template_context: dict[str, str | bool | list[str]],
    *,
    created_paths: list[Path],
) -> None:
    """Generate devcontainer configuration."""
    devcontainer_dir: Path = project_root / ".devcontainer"
    _render_template_to_file(
        devcontainer_dir / "devcontainer.json",
        "devcontainer/devcontainer.json.j2",
        template_context,
        project_root=project_root,
        created_paths=created_paths,
    )
    _render_template_to_file(
        devcontainer_dir / "docker-compose.yml",
        "devcontainer/docker-compose.yml.j2",
        template_context,
        project_root=project_root,
        created_paths=created_paths,
    )


def _generate_precommit(
    project_root: Path,
    template_context: dict[str, str | bool | list[str]],
    *,
    created_paths: list[Path],
) -> None:
    """Generate pre-commit configuration and the executable git hook wrapper."""
    _render_template_to_file(
        project_root / ".pre-commit-config.yaml",
        "precommit/pre-commit-config.yaml.j2",
        template_context,
        project_root=project_root,
        created_paths=created_paths,
    )
    hook_path: Path = project_root / ".githooks" / "pre-commit"
    _render_template_to_file(
        hook_path,
        "precommit/pre-commit-hook.j2",
        template_context,
        project_root=project_root,
        created_paths=created_paths,
    )
    _make_file_executable(hook_path)


def _generate_diagrams(
    project_root: Path,
    template_context: dict[str, str | bool | list[str]],
    *,
    created_paths: list[Path],
) -> None:
    """Generate PlantUML diagram templates."""
    diagrams_dir: Path = project_root / "docs" / "diagrams"
    _render_template_to_file(
        diagrams_dir / "class_diagram.puml",
        "diagrams/class_diagram.puml.j2",
        template_context,
        project_root=project_root,
        created_paths=created_paths,
    )


def _render_template_to_file(
    destination_path: Path,
    template_path: str,
    template_context: dict[str, str | bool | list[str]],
    *,
    project_root: Path,
    created_paths: list[Path],
) -> None:
    """Render a Jinja2 template and write the result to a file."""
    rendered: str = _render_template(template_path, template_context)
    _write_file(
        destination_path,
        rendered,
        project_root=project_root,
        created_paths=created_paths,
    )


def _render_template(
    template_path: str, template_context: dict[str, str | bool | list[str]]
) -> str:
    """Render a Jinja2 template with the given context."""
    template = TEMPLATE_ENV.get_template(template_path)
    return template.render(**template_context)


def _write_file(
    destination_path: Path,
    content: str,
    *,
    project_root: Path,
    created_paths: list[Path],
) -> None:
    """Write content to a file, creating parent directories as needed."""
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    destination_path.write_text(content)
    created_paths.append(destination_path.relative_to(project_root))


def _write_empty_init(
    directory: Path, *, project_root: Path, created_paths: list[Path]
) -> None:
    """Write an empty __init__.py file inside the given directory."""
    _write_file(
        directory / "__init__.py",
        "",
        project_root=project_root,
        created_paths=created_paths,
    )


def _make_file_executable(path: Path) -> None:
    """Add user/group/other execute bits to an existing file."""
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
