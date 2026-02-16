from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from backend.agents import convert_num_to_text, convert_text_to_num, orchestrator_router, llm

# 1. Define State
class AgentState(TypedDict):
    input_text: str
    routing_decision: str
    output_text: str
    steps: list[str]
    agent_a_enabled: bool
    agent_b_enabled: bool

# 2. Define Nodes
def orchestrator_node(state: AgentState):
    """
    Analyzes input and decides where to route.
    """
    decision = orchestrator_router(state["input_text"])
    return {
        "routing_decision": decision, 
        "steps": state.get("steps", []) + [f"Orchestrator: Analyzed input. Routing to {decision}."]
    }

def agent_num2text_node(state: AgentState):
    """
    Executes Num2Text conversion.
    """
    result = convert_num_to_text(state["input_text"])
    return {
        "output_text": result,
        "steps": state.get("steps", []) + [f"Agent A (Num2Text): Converted '{state['input_text']}' to '{result}'."]
    }

def agent_text2num_node(state: AgentState):
    """
    Executes Text2Num conversion.
    """
    result = convert_text_to_num(state["input_text"])
    return {
        "output_text": result,
        "steps": state.get("steps", []) + [f"Agent B (Text2Num): Converted '{state['input_text']}' to '{result}'."]
    }

def unknown_node(state: AgentState):
    """
    Handles unclear input.
    """
    return {
        "output_text": "I'm sorry, I couldn't determine if that was a number or text. Please try again.",
        "steps": state.get("steps", []) + ["Orchestrator: Could not determine type. Execution stopped."]
    }

def service_unavailable_node(state: AgentState):
    """
    Handles disabled agents.
    """
    return {
        "output_text": "Service Unavailable: The required agent is currently disabled.",
        "steps": state.get("steps", []) + ["Orchestrator: Agent disabled. Service unavailable."]
    }

# 3. Define Conditional Logic
def route_decision(state: AgentState) -> Literal["agent_num2text", "agent_text2num", "unknown", "service_unavailable"]:
    decision = state["routing_decision"]
    
    if decision == "num2text":
        if state.get("agent_a_enabled", True):
            return "agent_num2text"
        else:
            return "service_unavailable"
    elif decision == "text2num":
        if state.get("agent_b_enabled", True):
            return "agent_text2num"
        else:
            return "service_unavailable"
    else:
        return "unknown"

# 4. Build Graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("agent_num2text", agent_num2text_node)
workflow.add_node("agent_text2num", agent_text2num_node)
workflow.add_node("unknown", unknown_node)
workflow.add_node("service_unavailable", service_unavailable_node)

# Set entry point
workflow.set_entry_point("orchestrator")

# Add conditional edges
workflow.add_conditional_edges(
    "orchestrator",
    route_decision,
    {
        "agent_num2text": "agent_num2text",
        "agent_text2num": "agent_text2num",
        "unknown": "unknown",
        "service_unavailable": "service_unavailable"
    }
)

# Add edges to END
workflow.add_edge("agent_num2text", END)
workflow.add_edge("agent_text2num", END)
workflow.add_edge("unknown", END)
workflow.add_edge("service_unavailable", END)

# Compile
app = workflow.compile()
