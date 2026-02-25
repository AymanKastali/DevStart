"""Tests for devstart interactive prompt logic."""

from typing import Any
from unittest.mock import patch

from devstart.defaults import (
    DEFAULT_AUTHOR,
    DEFAULT_DESCRIPTION,
    DEFAULT_PROJECT_NAME,
    DEFAULT_PYTHON_VERSION,
)
from devstart.prompts.interactive import prompt_for_config


class TestPromptSkipsProvidedValues:
    @patch("devstart.prompts.interactive._StyledPrompt.ask")
    @patch("devstart.prompts.interactive._StyledConfirm.ask")
    def test_no_prompts_when_all_values_provided(self, mock_confirm, mock_prompt):
        config: dict[str, Any] = {
            "name": "myapp",
            "description": "My app",
            "author": "Author",
            "python": "3.14",
            "ci": True,
            "devcontainer": True,
            "precommit": True,
            "docker": False,
            "diagrams": True,
            "continue": True,
        }
        result = prompt_for_config(config)
        mock_prompt.assert_not_called()
        mock_confirm.assert_not_called()
        assert result["name"] == "myapp"
        assert result["ci"] is True
        assert result["docker"] is False

    @patch("devstart.prompts.interactive._StyledConfirm.ask", return_value=True)
    @patch(
        "devstart.prompts.interactive._StyledPrompt.ask",
        return_value="prompted_value",
    )
    def test_prompts_for_missing_name(self, mock_prompt, mock_confirm):
        config: dict[str, Any] = {
            "name": None,
            "description": "desc",
            "author": "auth",
            "python": "3.14",
            "ci": True,
            "devcontainer": True,
            "precommit": True,
            "docker": True,
            "diagrams": True,
            "continue": True,
        }
        result = prompt_for_config(config)
        assert result["name"] == "prompted_value"
        mock_prompt.assert_called_once()

    @patch("devstart.prompts.interactive._StyledConfirm.ask", return_value=False)
    @patch("devstart.prompts.interactive._StyledPrompt.ask", return_value="val")
    def test_prompts_for_missing_booleans(self, mock_prompt, mock_confirm):
        config: dict[str, Any] = {
            "name": "myapp",
            "description": "desc",
            "author": "auth",
            "python": "3.14",
            "ci": None,
            "devcontainer": None,
            "precommit": None,
            "docker": None,
            "diagrams": None,
            "continue": None,
        }
        result = prompt_for_config(config)
        assert result["ci"] is False
        assert result["devcontainer"] is False
        assert result["precommit"] is False
        assert result["docker"] is False
        assert result["diagrams"] is False
        assert result["continue"] is False
        assert mock_confirm.call_count == 6


class TestPromptDefaults:
    @patch("devstart.prompts.interactive._StyledConfirm.ask", return_value=True)
    @patch("devstart.prompts.interactive._StyledPrompt.ask")
    def test_prompt_uses_correct_defaults(self, mock_prompt, mock_confirm):
        mock_prompt.side_effect = [
            DEFAULT_PROJECT_NAME,
            DEFAULT_DESCRIPTION,
            DEFAULT_AUTHOR,
            DEFAULT_PYTHON_VERSION,
        ]
        config: dict[str, Any] = {
            "name": None,
            "description": None,
            "author": None,
            "python": None,
            "ci": None,
            "devcontainer": None,
            "precommit": None,
            "docker": None,
            "diagrams": None,
            "continue": None,
        }
        result = prompt_for_config(config)

        # Verify defaults were passed to prompts
        calls = mock_prompt.call_args_list
        assert calls[0].kwargs.get("default") == DEFAULT_PROJECT_NAME
        assert calls[1].kwargs.get("default") == DEFAULT_DESCRIPTION
        assert calls[2].kwargs.get("default") == DEFAULT_AUTHOR
        assert calls[3].kwargs.get("default") == DEFAULT_PYTHON_VERSION

        assert result["name"] == DEFAULT_PROJECT_NAME
        assert result["description"] == DEFAULT_DESCRIPTION
        assert result["author"] == DEFAULT_AUTHOR
        assert result["python"] == DEFAULT_PYTHON_VERSION
        assert result["ci"] is True
        assert result["devcontainer"] is True
        assert result["precommit"] is True
        assert result["docker"] is True
        assert result["diagrams"] is True
        assert result["continue"] is True
