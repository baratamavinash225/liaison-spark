import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from app.agents.state import AgentState
from app.domain.metadata import get_schema_context

def get_llm():
    return ChatOpenAI(
        model="openai/gpt-4o", 
        temperature=0, 
        base_url=os.environ.get("OPENAI_BASE_URL", "https://api.meshapi.ai/v1")
    )

def architect_node(state: AgentState):
    user_query = state["messages"][-1].content
    schema_context = get_schema_context()
    
    prompt = f"""You are a Senior Data Engineer Architect. Your job is to plan a PySpark job based on the user's request.
    
Here is the schema of our Data Catalog:
{schema_context}

User Request: {user_query}

Provide a step-by-step execution plan. Mention which tables to use, which columns to join on, and how to filter or aggregate.
Do NOT write code, just the plan."""
    
    response = get_llm().invoke([SystemMessage(content=prompt)])
    return {"plan": response.content, "iteration": state.get("iteration", 0)}

def coder_node(state: AgentState):
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

Rules:
- Use broadcast joins for 'small' size tables.
- Use .alias() for joins to avoid ambiguous columns.
- Ensure partition keys are used in filters.

Output ONLY Python code, no markdown wrappers if possible."""
    
    response = get_llm().invoke([SystemMessage(content=prompt)])
    code = response.content.replace("```python", "").replace("```", "").strip()
    return {"code": code}

def reviewer_node(state: AgentState):
    code = state["code"]
    
    prompt = f"""You are a Strict QA Data Engineer. Review the following PySpark code for anti-patterns:
1. Are there any .collect() calls on large DataFrames?
2. Are joins on small tables using broadcast()?
3. Are filters applied before joins?

Code to review:
{code}

If the code is PERFECT and safe for production, reply EXACTLY with "APPROVED".
If there are issues, reply with a description of the issues."""
    
    response = get_llm().invoke([SystemMessage(content=prompt)])
    review = response.content.strip()
    
    if review == "APPROVED":
        return {"errors": ""}
    else:
        return {"errors": review, "iteration": state.get("iteration", 0) + 1}


def router_node(state: AgentState):
    user_query = state["messages"][-1].content
    prompt = f"""You are an intent classifier for an AI Data Analyst agent.
Determine if the user is asking for a PySpark script, a data query, or data insights (DATA) OR if they are just making conversation, saying hello, or asking non-data related questions (CHAT).
User query: {user_query}
Reply with ONLY 'DATA' or 'CHAT'."""
    response = get_llm().invoke([SystemMessage(content=prompt)]).content.strip()
    return {"is_data_query": response == "DATA"}

def chat_node(state: AgentState):
    user_query = state["messages"][-1].content
    prompt = f"""You are Liaison-Spark, a helpful Autonomous Big Data Analyst assistant.
The user said: {user_query}
Respond conversationally. Do not write any PySpark code. If they ask about your capabilities, mention you can analyze Data Lakes and generate optimized PySpark jobs."""
    response = get_llm().invoke([SystemMessage(content=prompt)]).content.strip()
    return {"chat_response": response}
