"""File to store global constants.

Do not put constants related to a single part of the app here.
"""

from enum import StrEnum


class Tools(StrEnum):
    """Tools accomplish steps in a chain."""

    REVIEW_PULL_REQUEST = "review_pull_request"


class LLMProvider(StrEnum):
    """LLM providers."""

    OPENAI = "openai"
