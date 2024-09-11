"""Pydantic models for chat messages."""

from enum import StrEnum, auto
from typing import Self

from langchain.schema.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from pydantic import BaseModel


class PromptType(StrEnum):
    """Type of prompt."""

    system = auto()
    user = auto()


class Role(StrEnum):
    """Role of the message sender."""

    assistant = auto()
    system = auto()
    user = auto()


class Message(BaseModel):
    """A single chat message."""

    role: Role
    content: str

    def to_langchain_message(self: Self) -> BaseMessage:
        """Get LangChain message type from Role.

        This is a workaround for the fact that LangChain's message types do not coincide
        with the Role enum.

        :param content: content of the message.
        :raises RoleError: if the role is not in the Role enum.
        :return: LangChain message type for this role.
        """
        match self.role:
            case Role.assistant:
                return AIMessage(content=self.content)
            case Role.system:
                return SystemMessage(content=self.content)
            case Role.user:
                return HumanMessage(content=self.content)
