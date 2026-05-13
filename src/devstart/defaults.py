"""Centralized default values for devstart CLI configuration."""

DEFAULT_PROJECT_NAME: str = "myproject"
DEFAULT_DESCRIPTION: str = "A Python project"
DEFAULT_AUTHOR: str = "Author"
DEFAULT_PYTHON_VERSION: str = "3.14"
SUPPORTED_PYTHON_VERSIONS: list[str] = ["3.12", "3.13", "3.14"]

MIN_PYTHON_VERSION: str = SUPPORTED_PYTHON_VERSIONS[0]
MAX_PYTHON_VERSION: str = SUPPORTED_PYTHON_VERSIONS[-1]

RECOMMENDED_VSCODE_EXTENSIONS: list[str] = [
    # Python core
    "ms-python.python",
    "ms-python.debugpy",
    "charliermarsh.ruff",
    "ms-python.mypy-type-checker",
    "ryanluker.vscode-coverage-gutters",
    # Config / file syntax
    "tamasfe.even-better-toml",
    "redhat.vscode-yaml",
    "mikestead.dotenv",
    "streetsidesoftware.code-spell-checker",
    # Editor enhancements
    "usernamehw.errorlens",
    "christian-kohler.path-intellisense",
    "gruntfuggly.todo-tree",
    "rangav.vscode-thunder-client",
    # Git
    "eamodio.gitlens",
    "mhutchie.git-graph",
    "codezombiech.gitignore",
    # Docker / containers
    "ms-azuretools.vscode-docker",
    # Docs / diagrams
    "jebbs.plantuml",
    # GitHub
    "github.vscode-pull-request-github",
    "github.vscode-github-actions",
]


def is_supported_python_version(version: str) -> bool:
    """Check whether a Python version string is within the supported range."""
    if version == "latest":
        return True
    return version in SUPPORTED_PYTHON_VERSIONS
