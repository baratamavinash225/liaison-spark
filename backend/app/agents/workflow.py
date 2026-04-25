from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.nodes import architect_node, coder_node, reviewer_node

def should_continue(state: AgentState):
    if state.get("errors") == "" or state.get("iteration", 0) >= 3:
        return "end"
    return "coder"

def create_workflow():
    workflow = StateGraph(AgentState)
    workflow.add_node("architect", architect_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("reviewer", reviewer_node)

    workflow.set_entry_point("architect")
    workflow.add_edge("architect", "coder")
    workflow.add_edge("coder", "reviewer")
    workflow.add_conditional_edges("reviewer", should_continue, {"end": END, "coder": "coder"})

    return workflow.compile()
