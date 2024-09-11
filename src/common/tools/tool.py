"""Protocol for tools."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, runtime_checkable

import yaml
from jinja2 import Environment, StrictUndefined
from typing_extensions import Protocol

from configs.tools import CHAT_CONFIG_DIRECTORY

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from pathlib import Path

    from src.common.models.message import PromptType
    from src.common.constants import Tools


@runtime_checkable
class Tool(Protocol):
    """Protocol for tools."""

    name: Tools

    @classmethod
    async def arun(
        cls: type[Tool],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Use the tool asynchronously.

        :return: Tool output.
        """


def get_tool_config_path(tool: Tools) -> Path:
    """Return the path to the tool's config file based on the tool's name.

    The expected path is: configs/tools/<tool_name>/main.yaml.

    :tool: Tool to get the config path for.
    :return: Path to the tool's config file.
    """
    return CHAT_CONFIG_DIRECTORY / f"{tool}" / "main.yaml"


def get_hydrated_prompt(
    template_path: Path,
    prompt_type: PromptType,
    **kwargs: Any,
) -> str:
    """Return tool's prompts hydrated with context data.

    :param template_path: path to the YAML file containing the prompts.
    :param prompt_type: type of prompt to hydrate.
    :return: A Box configuration with the tool's prompts.
    """
    # Read the YAML file
    prompt_templates = yaml.safe_load(template_path.read_text())
    prompt_template = prompt_templates[prompt_type]

    # Initialize the Jinja2 environment
    # (raise error when undefined and escape special characters).
    environment = Environment(undefined=StrictUndefined, autoescape=True)

    # Render the Jinja2 template.
    jinja_template = environment.from_string(prompt_template)
    return jinja_template.render(**kwargs)


MISSING_VALUE_SENTINEL = object()


def get_kwarg(kwargs: dict[str, Any], key: str) -> Any:
    """Extract given keyword argument from kwargs.

    This class is useful to silence mypy warnings.

    :param kwargs: Keyword arguments.
    :param key: Key to extract from kwargs.
    :return: Value of the given key in kwargs.
    """
    value = kwargs.get(key, MISSING_VALUE_SENTINEL)
    if value is MISSING_VALUE_SENTINEL:
        msg = f"Missing required keyword argument: {key}"
        raise ValueError(msg)
    return value
