import os
from typing import TypedDict, Annotated, Sequence
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from metadata_harvester import get_schema_context

class AgentState(TypedDict):
    messages: Sequence[BaseMessage]
    plan: str
    code: str
    errors: str
    iteration: int

# Initialize LLM
llm = ChatOpenAI(model="openai/gpt-4o", temperature=0, base_url=os.environ.get("OPENAI_BASE_URL", "https://api.meshapi.ai/v1"))
# Note: you may need to adjust the base_url path (e.g. adding /v1) depending on the exact MeshAPI specs.

def architect_node(state: AgentState):
    """The Architect Planner: Creates an execution plan based on the user's question and schema."""
    user_query = state['messages'][-1].content
    schema_context = get_schema_context()
    
    prompt = f"""You are a Senior Data Engineer Architect. Your job is to plan a PySpark job based on the user's request.
    
Here is the schema of our Data Catalog:
{schema_context}

User Request: {user_query}

Provide a step-by-step execution plan. Mention which tables to use, which columns to join on, and how to filter or aggregate.
Do NOT write code, just the plan."""
    
    response = llm.invoke([SystemMessage(content=prompt)])
    return {"plan": response.content, "iteration": state.get('iteration', 0)}

def coder_node(state: AgentState):
    """The Lead Developer Coder: Writes PySpark code based on the plan."""
    plan = state['plan']
    schema_context = get_schema_context()
    errors = state.get('errors', '')
    
    error_context = f"\nPREVIOUS ERRORS TO FIX:\n{errors}\n" if errors else ""
    
    prompt = f"""You are a Senior PySpark Developer. Your job is to write PySpark code based on the Architect's plan.
    
Here is the schema:
{schema_context}

Architect's Plan:
{plan}
{error_context}
Write ONLY the PySpark code. The code should:
1. Initialize a SparkSession.
2. Create dummy DataFrames using the schema structure (since we don't have real HDFS/S3 data).
3. Perform the requested operations.
4. Print the result using .show().

Rules:
- Use broadcast joins for 'small' size tables.
- Use .alias() for joins to avoid ambiguous columns.
- Ensure partition keys are used in filters.

Output ONLY Python code, no markdown wrappers if possible, but if you do, just standard python code."""
    
    response = llm.invoke([SystemMessage(content=prompt)])
    code = response.content.replace("```python", "").replace("```", "").strip()
    return {"code": code}

def reviewer_node(state: AgentState):
    """The QA Engineer Reviewer: Checks for Spark anti-patterns."""
    code = state['code']
    
    prompt = f"""You are a Strict QA Data Engineer. Review the following PySpark code for anti-patterns:
1. Are there any .collect() calls on large DataFrames?
2. Are joins on small tables using broadcast()?
3. Are filters applied before joins?

Code to review:
{code}

If the code is PERFECT and safe for production, reply EXACTLY with "APPROVED".
If there are issues, reply with a description of the issues."""
    
    response = llm.invoke([SystemMessage(content=prompt)])
    review = response.content.strip()
    
    if review == "APPROVED":
        return {"errors": ""}
    else:
        return {"errors": review, "iteration": state.get('iteration', 0) + 1}

def should_continue(state: AgentState):
    if state.get("errors") == "" or state.get("iteration", 0) >= 3:
        return "end"
    return "coder"

# Build Graph
workflow = StateGraph(AgentState)
workflow.add_node("architect", architect_node)
workflow.add_node("coder", coder_node)
workflow.add_node("reviewer", reviewer_node)

workflow.set_entry_point("architect")
workflow.add_edge("architect", "coder")
workflow.add_edge("coder", "reviewer")
workflow.add_conditional_edges("reviewer", should_continue, {"end": END, "coder": "coder"})

app = workflow.compile()
