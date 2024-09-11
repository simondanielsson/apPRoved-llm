from typing import AsyncIterator

from box import Box
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
)

from src.config import config
from src.common.constants import LLMProvider
from src.utils.exceptions import ConfigError


def get_chat_model(
    llm_model: str = config.provider_to_llm[config.llm_provider],
    llm_provider: str = config.llm_provider,
    config: Box = config,
) -> BaseChatModel:
    """Get the chat model."""
    llm_type: type[BaseChatModel]

    match llm_provider:
        case LLMProvider.OPENAI:
            llm_type = ChatOpenAI
        case _:
            message = f"Unknown LLM model: {llm_model}"
            raise ConfigError(message)

    return llm_type(model=llm_model, **(config.llm_config or {}))


async def ask_llm(
    system_prompt: str,
    user_prompt: str,
    memory: list[BaseMessage] | None = None,
    llm_model: str = config.provider_to_llm[config.llm_provider],
) -> AsyncIterator[str]:
    """Ask the LLM for a response.

    :param system_prompt: The system prompt.
    :param user_prompt: The user prompt.
    :return: The LLM response.
    """
    memory = memory or []
    messages = [
        SystemMessage(content=system_prompt),
        *memory,
        HumanMessage(content=user_prompt),
    ]
    chat_model = get_chat_model(llm_model=llm_model)

    answer_iterator = chat_model.astream(input=messages)
    async for answer in answer_iterator:
        yield answer.content
