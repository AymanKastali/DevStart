"""Tests for the patch-version resolver."""

import subprocess
from typing import TYPE_CHECKING

from devstart import python_version as resolver_module
from devstart.python_version import resolve_patch_version

if TYPE_CHECKING:
    import pytest


class TestResolvePatchVersion:
    def test_invalid_minor_falls_back(self):
        assert resolve_patch_version("not-a-version") == "not-a-version"
        assert resolve_patch_version("3.14.2") == "3.14.2"
        assert resolve_patch_version("") == ""

    def test_missing_uv_falls_back(self, monkeypatch: "pytest.MonkeyPatch"):
        monkeypatch.setattr(resolver_module.shutil, "which", lambda _name: None)
        assert resolve_patch_version("3.14") == "3.14"

    def test_uv_find_failure_falls_back(self, monkeypatch: "pytest.MonkeyPatch"):
        monkeypatch.setattr(
            resolver_module.shutil, "which", lambda _name: "/usr/bin/uv"
        )

        def _raise_subprocess_error(*_args: object, **_kwargs: object) -> None:
            raise subprocess.CalledProcessError(returncode=2, cmd=["uv"])

        monkeypatch.setattr(
            resolver_module.subprocess, "run", _raise_subprocess_error
        )
        assert resolve_patch_version("3.14") == "3.14"

    def test_resolves_full_patch_from_interpreter(
        self, monkeypatch: "pytest.MonkeyPatch"
    ):
        monkeypatch.setattr(
            resolver_module.shutil, "which", lambda _name: "/usr/bin/uv"
        )

        def _stub_subprocess_run(
            args: list[str], **_kwargs: object
        ) -> subprocess.CompletedProcess[str]:
            if args[0] == "/usr/bin/uv":
                return subprocess.CompletedProcess(args, 0, "/opt/python/3.14.2\n", "")
            return subprocess.CompletedProcess(args, 0, "Python 3.14.2\n", "")

        monkeypatch.setattr(resolver_module.subprocess, "run", _stub_subprocess_run)
        assert resolve_patch_version("3.14") == "3.14.2"

    def test_unparseable_version_falls_back(
        self, monkeypatch: "pytest.MonkeyPatch"
    ):
        monkeypatch.setattr(
            resolver_module.shutil, "which", lambda _name: "/usr/bin/uv"
        )

        def _stub_subprocess_run(
            args: list[str], **_kwargs: object
        ) -> subprocess.CompletedProcess[str]:
            if args[0] == "/usr/bin/uv":
                return subprocess.CompletedProcess(args, 0, "/opt/python\n", "")
            return subprocess.CompletedProcess(args, 0, "weird output\n", "")

        monkeypatch.setattr(resolver_module.subprocess, "run", _stub_subprocess_run)
        assert resolve_patch_version("3.14") == "3.14"
