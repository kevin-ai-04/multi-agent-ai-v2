from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from backend.agents import convert_num_to_text, convert_text_to_num, orchestrator_router, analyze_email_content
from backend.database import get_unanalyzed_emails, get_item_by_name, get_vendor, save_email_analysis

# 1. Define State
class AgentState(TypedDict):
    input_text: str
    routing_decision: str
    output_text: str
    steps: list[str]
    agent_a_enabled: bool
    agent_b_enabled: bool
    agent_email_enabled: bool
    ui_actions: list[dict]

# 2. Define Nodes
def orchestrator_node(state: AgentState):
    """
    Analyzes input and decides where to route.
    """
    input_text = state.get("input_text", "")
    orchestration = orchestrator_router(input_text)
    decision = orchestration.decision
    ui_actions = [action.model_dump() for action in orchestration.ui_actions]
    chat_response = orchestration.chat_response
    
    steps = list(state.get("steps", []))
    steps.append(f"Orchestrator: Analyzed input. Routing to {decision}.")
    
    return {
        "routing_decision": decision, 
        "ui_actions": ui_actions,
        "output_text": chat_response if chat_response else state.get("output_text", ""),
        "steps": steps
    }

def agent_num2text_node(state: AgentState):
    """
    Executes Num2Text conversion.
    """
    result = convert_num_to_text(state["input_text"])
    steps = list(state.get("steps", []))
    steps.append(f"Agent A (Num2Text): Converted '{state['input_text']}' to '{result}'.")
    return {
        "output_text": result,
        "steps": steps
    }

def agent_text2num_node(state: AgentState):
    """
    Executes Text2Num conversion.
    """
    result = convert_text_to_num(state["input_text"])
    steps = list(state.get("steps", []))
    steps.append(f"Agent B (Text2Num): Converted '{state['input_text']}' to '{result}'.")
    return {
        "output_text": result,
        "steps": steps
    }

def agent_email_node(state: AgentState):
    """
    Executes Email Agent batch analysis.
    """
    steps = state.get("steps", []) + ["Email Agent: Analyzing inbox..."]
    
    unanalyzed = get_unanalyzed_emails()
    if not unanalyzed:
        return {
            "output_text": "No new emails to analyze right now.",
            "steps": steps + ["Email Agent: No unanalyzed emails found."]
        }
    
    count = 0
    for email in unanalyzed:
        try:
            email_id = email['id']
            body = email['body']
            analysis_data = analyze_email_content(body)
            if not analysis_data:
                continue
            
            item_data = None
            vendor_data = None
            if analysis_data.get('item_name'):
                item_data = get_item_by_name(analysis_data['item_name'])
                
            if item_data and item_data.get('default_vendor_id'):
                vendor_data = get_vendor(item_data['default_vendor_id'])
                
            save_email_analysis(email_id, analysis_data, item_data, vendor_data)
            steps.append(f"Email Agent: Analyzed email '{email_id}' -> {analysis_data.get('item_name', 'Unknown Item')}")
            count += 1
        except Exception as e:
            steps.append(f"Email Agent: Failed to analyze email '{email_id}'. Error: {str(e)}")
            pass
            
    steps.append(f"Email Agent: Processed {count} emails.")
    return {
        "output_text": f"Successfully analyzed {count} new email(s).",
        "steps": steps
    }

def unknown_node(state: AgentState):
    """
    Handles unclear input or pure UI navigation requests.
    """
    steps = list(state.get("steps", []))
    output_text = state.get("output_text", "")
    
    # If orchestrator provided a chat response, use it
    if isinstance(output_text, str) and output_text and not output_text.startswith("I'm sorry, I couldn't determine"):
        steps.append("Orchestrator: Direct response provided.")
        return {
            "output_text": output_text,
            "steps": steps
        }
        
    ui_actions = state.get("ui_actions", [])
    if ui_actions:
        steps.append("Orchestrator: Performed UI actions. Request fulfilled.")
        return {
            "output_text": "I've updated your view based on your request.",
            "steps": steps
        }
    
    steps.append("Orchestrator: Could not determine intent. Execution stopped.")
    return {
        "output_text": "I'm sorry, I couldn't determine the intent. Please try asking about your inbox or converting a number.",
        "steps": steps
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
def route_decision(state: AgentState) -> Literal["agent_num2text", "agent_text2num", "agent_email", "unknown", "service_unavailable"]:
    decision = state["routing_decision"]
    agent_enabled_map = {
        "num2text": state.get("agent_a_enabled", True),
        "text2num": state.get("agent_b_enabled", True),
        "email": state.get("agent_email_enabled", True)
    }

    if decision in ["num2text", "text2num", "email"]:
        if agent_enabled_map[decision]:
            return f"agent_{decision}"
        else:
            return "service_unavailable"
    
    return "unknown"

# 4. Build Graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("agent_num2text", agent_num2text_node)
workflow.add_node("agent_text2num", agent_text2num_node)
workflow.add_node("agent_email", agent_email_node)
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
        "agent_email": "agent_email",
        "unknown": "unknown",
        "service_unavailable": "service_unavailable"
    }
)

# Add edges to END
workflow.add_edge("agent_num2text", END)
workflow.add_edge("agent_text2num", END)
workflow.add_edge("agent_email", END)
workflow.add_edge("unknown", END)
workflow.add_edge("service_unavailable", END)

# Compile
app = workflow.compile()
