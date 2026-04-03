"""Tests for devstart interactive prompt logic."""

from unittest.mock import patch

from devstart.defaults import (
    DEFAULT_AUTHOR,
    DEFAULT_DESCRIPTION,
    DEFAULT_PROJECT_NAME,
)
from devstart.prompts.interactive import prompt_for_config


class TestPromptSkipsProvidedValues:
    @patch("devstart.prompts.interactive._StyledPrompt.ask")
    @patch("devstart.prompts.interactive._select_from_list")
    def test_no_prompts_when_all_values_provided(self, mock_select, mock_prompt):
        config: dict[str, str | bool | None] = {
            "name": "myapp",
            "description": "My app",
            "author": "Author",
            "python": "3.14",
        }
        result = prompt_for_config(config)
        mock_prompt.assert_not_called()
        mock_select.assert_not_called()
        assert result["name"] == "myapp"

    @patch("devstart.prompts.interactive._select_from_list")
    @patch(
        "devstart.prompts.interactive._StyledPrompt.ask",
        return_value="prompted_value",
    )
    def test_prompts_for_missing_name(self, mock_prompt, mock_select):
        config: dict[str, str | bool | None] = {
            "name": None,
            "description": "desc",
            "author": "auth",
            "python": "3.14",
        }
        result = prompt_for_config(config)
        assert result["name"] == "prompted_value"
        mock_prompt.assert_called_once()
        mock_select.assert_not_called()


class TestPromptDefaults:
    @patch(
        "devstart.prompts.interactive._select_from_list",
        return_value="3.14",
    )
    @patch("devstart.prompts.interactive._StyledPrompt.ask")
    def test_prompt_uses_correct_defaults(self, mock_prompt, mock_select):
        mock_prompt.side_effect = [
            DEFAULT_PROJECT_NAME,
            DEFAULT_DESCRIPTION,
            DEFAULT_AUTHOR,
        ]
        config: dict[str, str | bool | None] = {
            "name": None,
            "description": None,
            "author": None,
            "python": None,
        }
        result = prompt_for_config(config)

        calls = mock_prompt.call_args_list
        assert calls[0].kwargs.get("default") == DEFAULT_PROJECT_NAME
        assert calls[1].kwargs.get("default") == DEFAULT_DESCRIPTION
        assert calls[2].kwargs.get("default") == DEFAULT_AUTHOR

        mock_select.assert_called_once()

        assert result["name"] == DEFAULT_PROJECT_NAME
        assert result["description"] == DEFAULT_DESCRIPTION
        assert result["author"] == DEFAULT_AUTHOR
        assert result["python"] == "3.14"


class TestPythonVersionSelector:
    @patch(
        "devstart.prompts.interactive._select_from_list",
        return_value="3.13",
    )
    def test_python_version_selected_via_dropdown(self, mock_select):
        config: dict[str, str | bool | None] = {
            "name": "myapp",
            "description": "desc",
            "author": "auth",
            "python": None,
        }
        result = prompt_for_config(config)
        assert result["python"] == "3.13"
        mock_select.assert_called_once()

    def test_python_version_skipped_when_provided(self):
        with patch("devstart.prompts.interactive._select_from_list") as mock_select:
            config: dict[str, str | bool | None] = {
                "name": "myapp",
                "description": "desc",
                "author": "auth",
                "python": "3.15",
            }
            result = prompt_for_config(config)
            assert result["python"] == "3.15"
            mock_select.assert_not_called()
