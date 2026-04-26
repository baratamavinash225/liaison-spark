from langchain_core.messages import HumanMessage
from app.agents.state import AgentState
from app.agents.nodes.base import BaseNode
from app.domain.semantic_layer import semantic_layer

class ArchitectNode(BaseNode):
    async def __call__(self, state: AgentState) -> dict:
        user_query = state["messages"][-1].content
        schema_context = semantic_layer.get_context(user_query)
        
        prompt = f"""You are a Senior Data Engineer Architect. Your job is to plan a PySpark job based on the user's request.
        
Here is the schema of our Data Catalog:
{schema_context}

User Request: {user_query}

Provide a step-by-step execution plan. Mention which tables to use, which columns to join on, and how to filter or aggregate.
Do NOT write code, just the plan."""
        
        response = await self.llm_service.get_llm().ainvoke([HumanMessage(content=prompt)])
        return {"plan": response.content, "iteration": state.get("iteration", 0)}