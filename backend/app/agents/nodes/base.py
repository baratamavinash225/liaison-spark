from abc import ABC, abstractmethod

from app.agents.state import AgentState
from app.services.llm_service import LLMService


class BaseNode(ABC):
    """Base template for all LangGraph nodes."""

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    @abstractmethod
    async def __call__(self, state: AgentState) -> dict:
        pass
