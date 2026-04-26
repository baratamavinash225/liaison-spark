from langchain_core.messages import SystemMessage
from app.agents.state import AgentState
from app.agents.nodes.base import BaseNode

class RouterNode(BaseNode):
    async def __call__(self, state: AgentState) -> dict:
        user_query = state["messages"][-1].content
        prompt = f"""You are an intent classifier for an AI Data Analyst agent.
Determine if the user is asking for a PySpark script, a data query, or data insights (DATA) OR if they are just making conversation, saying hello, or asking non-data related questions (CHAT).
User query: {user_query}
Reply with ONLY 'DATA' or 'CHAT'."""
        
        response = await self.llm_service.get_llm().ainvoke([SystemMessage(content=prompt)])
        response_text = response.content.strip()
        return {"is_data_query": response_text == "DATA"}