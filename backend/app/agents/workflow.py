from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.nodes import architect_node, coder_node, reviewer_node, router_node, chat_node

def should_continue(state: AgentState):
    if state.get("errors") == "" or state.get("iteration", 0) >= 3:
        return "end"
    return "coder"

def route_initial(state: AgentState):
    if state.get("is_data_query"):
        return "architect"
    else:
        return "chat_node"

def create_workflow():
    workflow = StateGraph(AgentState)
    workflow.add_node("router", router_node)
    workflow.add_node("chat_node", chat_node)
    workflow.add_node("architect", architect_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("reviewer", reviewer_node)

    workflow.set_entry_point("router")
    workflow.add_conditional_edges("router", route_initial, {"architect": "architect", "chat_node": "chat_node"})
    workflow.add_edge("chat_node", END)
    workflow.add_edge("architect", "coder")
    workflow.add_edge("coder", "reviewer")
    workflow.add_conditional_edges("reviewer", should_continue, {"end": END, "coder": "coder"})

    return workflow.compile()
