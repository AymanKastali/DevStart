"""Centralized default values for devstart CLI configuration."""

DEFAULT_PROJECT_NAME: str = "myproject"
DEFAULT_DESCRIPTION: str = "A Python project"
DEFAULT_AUTHOR: str = "Author"
DEFAULT_PYTHON_VERSION: str = "3.14"
SUPPORTED_PYTHON_VERSIONS: list[str] = ["3.12", "3.13", "3.14"]

MIN_PYTHON_VERSION: str = SUPPORTED_PYTHON_VERSIONS[0]
MAX_PYTHON_VERSION: str = SUPPORTED_PYTHON_VERSIONS[-1]


def is_supported_python_version(version: str) -> bool:
    """Check whether a Python version string is within the supported range."""
    if version == "latest":
        return True
    return version in SUPPORTED_PYTHON_VERSIONS
