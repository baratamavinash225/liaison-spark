from langchain_core.messages import SystemMessage
from app.agents.state import AgentState
from app.domain.metadata import get_schema_context
from app.agents.nodes.base import BaseNode

class CoderNode(BaseNode):
    async def __call__(self, state: AgentState) -> dict:
        plan = state["plan"]
        schema_context = get_schema_context()
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
        
        response = await self.llm_service.get_llm().ainvoke([SystemMessage(content=prompt)])
        code = response.content.replace("```python", "").replace("```", "").strip()
        return {"code": code}