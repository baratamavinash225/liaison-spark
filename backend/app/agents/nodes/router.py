from typing import Literal
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from app.agents.state import AgentState
from app.agents.nodes.base import BaseNode

class RouterOutput(BaseModel):
    # This field acts as "Chain of Thought" reasoning
    reasoning: str = Field(description="Brief explanation of why this route was chosen.")
    next_node: Literal["architect", "chat_node"] = Field(
        description="Route to 'architect' for data/PySpark tasks, or 'chat_node' for general conversation."
    )

class RouterNode(BaseNode):
    async def __call__(self, state: AgentState) -> dict:
        user_query = state["messages"][-1].content
        
        system_prompt = "You are an intent classifier for an AI Data Analyst agent."
        user_prompt = f"Determine the next node for this query: {user_query}"
        
        structured_llm = self.llm_service.get_llm().with_structured_output(RouterOutput)
        
        response = await structured_llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        # Handle the rare case where the LLM fails to return the structured object
        if not response:
            return {"next_node": "chat_node"}
            
        return {"next_node": response.next_node, "routing_reasoning": response.reasoning}