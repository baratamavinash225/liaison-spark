from langchain_core.messages import SystemMessage
from app.agents.state import AgentState
from app.agents.nodes.base import BaseNode

class ChatNode(BaseNode):
    async def __call__(self, state: AgentState) -> dict:
        user_query = state["messages"][-1].content
        prompt = f"""You are Liaison-Spark, a helpful Autonomous Big Data Analyst assistant.
The user said: {user_query}
Respond conversationally. Do not write any PySpark code. If they ask about your capabilities, mention you can analyze Data Lakes and generate optimized PySpark jobs."""
        
        response = await self.llm_service.get_llm().ainvoke([SystemMessage(content=prompt)])
        return {"chat_response": response.content.strip()}