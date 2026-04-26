from langchain_core.messages import HumanMessage
from app.agents.state import AgentState
from app.agents.nodes.base import BaseNode
from app.domain.semantic_layer import semantic_layer

class CoderNode(BaseNode):
    async def __call__(self, state: AgentState) -> dict:
        plan = state["plan"]
        user_query = state["messages"][-1].content
        schema_context = semantic_layer.get_context(user_query)
        errors = state.get("errors", "")
        
        error_context = f"\nPREVIOUS ERRORS TO FIX:\n{errors}\n" if errors else ""
        
        prompt = f"""You are a Senior PySpark Developer. Your job is to write PySpark code based on the Architect's plan.
        
Here is the schema:
{schema_context}

Architect's Plan:
{plan}
{error_context}
Write ONLY the PySpark code. The code should:
1. Initialize a SparkSession.
2. Create dummy DataFrames using the schema structure.
3. Perform the requested operations.
4. Print the result using .show().

Output ONLY Python code, no markdown wrappers if possible."""
        
        response = await self.llm_service.get_llm().ainvoke([HumanMessage(content=prompt)])
        code = response.content.replace("```python", "").replace("```", "").strip()
        return {"code": code}