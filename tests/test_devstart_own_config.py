"""Lock DevStart's own infra files to the constants used for generated projects.

The generated devcontainer template pulls from `RECOMMENDED_VSCODE_EXTENSIONS`
in `devstart.defaults`. DevStart's own `.devcontainer/devcontainer.json` is a
static, hand-edited file — this test fails if anyone edits it without keeping
it aligned with the Python source of truth.
"""

import json
import re
from pathlib import Path

from devstart.defaults import RECOMMENDED_VSCODE_EXTENSIONS

REPO_ROOT: Path = Path(__file__).resolve().parent.parent


class TestExtensionListsAreSingleSource:
    def test_devcontainer_extensions_match(self):
        text = (REPO_ROOT / ".devcontainer" / "devcontainer.json").read_text()
        match = re.search(r'"extensions":\s*(\[[^\]]*\])', text, re.DOTALL)
        assert match is not None, "devcontainer.json missing extensions array"
        assert json.loads(match.group(1)) == RECOMMENDED_VSCODE_EXTENSIONS
