from typing import TypedDict, Sequence
from langchain_core.messages import BaseMessage

class AgentState(TypedDict, total=False):
    messages: Sequence[BaseMessage]
    plan: str
    code: str
    errors: str
    iteration: int
    is_data_query: bool
    chat_response: str
