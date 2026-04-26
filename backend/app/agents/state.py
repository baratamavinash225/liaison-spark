from collections.abc import Sequence
from typing import TypedDict

from langchain_core.messages import BaseMessage


class AgentState(TypedDict, total=False):
    messages: Sequence[BaseMessage]
    plan: str
    code: str
    errors: str
    iteration: int
    next_node: str
    routing_reasoning: str
    chat_response: str
