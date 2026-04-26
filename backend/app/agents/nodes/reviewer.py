from langchain_core.messages import HumanMessage
from app.agents.state import AgentState
from app.agents.nodes.base import BaseNode

class ReviewerNode(BaseNode):
    async def __call__(self, state: AgentState) -> dict:
        code = state["code"]
        
        prompt = f"""You are a Strict QA Data Engineer. Review the following PySpark code for anti-patterns:
1. Are there any .collect() calls on large DataFrames?
2. Are joins on small tables using broadcast()?
3. Are filters applied before joins?

Code to review:
{code}

If the code is PERFECT and safe for production, reply EXACTLY with "APPROVED".
If there are issues, reply with a description of the issues."""
        
        response = await self.llm_service.get_llm().ainvoke([HumanMessage(content=prompt)])
        review = response.content.strip()
        
        if review == "APPROVED":
            return {"errors": ""}
        else:
            return {"errors": review, "iteration": state.get("iteration", 0) + 1}