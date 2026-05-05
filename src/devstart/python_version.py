"""Resolve a minor Python version (e.g. 'X.Y') to its full patch (e.g. 'X.Y.Z')."""

import re
import shutil
import subprocess

_MINOR_VERSION_PATTERN: re.Pattern[str] = re.compile(r"^\d+\.\d+$")
_PATCH_VERSION_PATTERN: re.Pattern[str] = re.compile(r"^\d+\.\d+\.\d+$")

_FIND_TIMEOUT_SECONDS: int = 10
_VERSION_TIMEOUT_SECONDS: int = 5


def resolve_patch_version(minor_version: str) -> str:
    """Return the full patch version for a given minor (e.g. 'X.Y' → 'X.Y.Z').

    Resolution path:
        1. Validate ``minor_version`` matches ``X.Y`` (else return it unchanged).
        2. Find ``uv`` on PATH (else return ``minor_version``).
        3. Ask uv for the resolved interpreter path for that minor.
        4. Run ``<interpreter> --version`` and parse the patch.

    Any failure along the way returns ``minor_version`` unchanged. Never raises.
    """
    if not _MINOR_VERSION_PATTERN.match(minor_version):
        return minor_version
    uv_executable_path: str | None = shutil.which("uv")
    if uv_executable_path is None:
        return minor_version
    interpreter_path: str | None = _find_uv_managed_interpreter(
        uv_executable_path, minor_version
    )
    if interpreter_path is None:
        return minor_version
    return _read_interpreter_patch_version(interpreter_path) or minor_version


def _find_uv_managed_interpreter(
    uv_executable_path: str, minor_version: str
) -> str | None:
    """Return the absolute path to a uv-resolved interpreter, or None on failure."""
    try:
        completed_process = subprocess.run(
            [uv_executable_path, "python", "find", minor_version],
            capture_output=True,
            text=True,
            timeout=_FIND_TIMEOUT_SECONDS,
            check=True,
        )
    except subprocess.SubprocessError:
        return None
    except OSError:
        return None
    interpreter_path: str = completed_process.stdout.strip()
    return interpreter_path or None


def _read_interpreter_patch_version(interpreter_path: str) -> str | None:
    """Run ``<python> --version`` and return the parsed ``X.Y.Z`` string, or None."""
    try:
        completed_process = subprocess.run(
            [interpreter_path, "--version"],
            capture_output=True,
            text=True,
            timeout=_VERSION_TIMEOUT_SECONDS,
            check=True,
        )
    except subprocess.SubprocessError:
        return None
    except OSError:
        return None
    reported_version: str = (
        completed_process.stdout.strip().removeprefix("Python ").strip()
    )
    if _PATCH_VERSION_PATTERN.match(reported_version):
        return reported_version
    return None
