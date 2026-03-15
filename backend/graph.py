from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from backend.agents import (
    orchestrator_router,
    analyze_email_content, run_gatekeeper_checks, explain_compliance_result,
    generate_order_pdf
)
from backend.database import (
    get_unanalyzed_emails, get_item_by_name, get_vendor,
    save_email_analysis, get_email_analysis, get_all_email_analyses,
    create_order, get_order_by_id
)

# 1. Define State
class AgentState(TypedDict):
    input_text: str
    routing_decision: str
    output_text: str
    steps: list[str]
    agent_email_enabled: bool
    agent_compliance_enabled: bool
    agent_pdf_enabled: bool
    agent_forecast_enabled: bool
    ui_actions: list[dict]
    gatekeeper_results: list[dict]
    order_ids: list[int]

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

def agent_email_node(state: AgentState):
    """
    Full pipeline: analyze emails → compliance check → LLM explanation → create DRAFT order.
    """
    steps = list(state.get("steps", [])) + ["Email Agent: Starting email analysis pipeline..."]
    gatekeeper_results = []
    order_ids = []
    analyzed_count = order_count = rejected_count = 0

    unanalyzed = get_unanalyzed_emails()
    if not unanalyzed:
        return {
            "output_text": "No new emails to analyze right now.",
            "steps": steps + ["Email Agent: No unanalyzed emails found."],
            "gatekeeper_results": [],
            "order_ids": []
        }

    for email in unanalyzed:
        email_id = email['id']
        try:
            # ── Step 1: AI extraction ──────────────────────
            analysis_data = analyze_email_content(email['body'])
            if not analysis_data:
                steps.append(f"Email Agent: Could not extract data from '{email_id}'. Skipping.")
                continue

            # ── Step 2: Item & Vendor lookup ───────────────
            item_data = get_item_by_name(analysis_data['item_name']) if analysis_data.get('item_name') else None
            vendor_data = get_vendor(item_data['default_vendor_id']) if item_data and item_data.get('default_vendor_id') else None

            # ── Step 3: Save analysis ──────────────────────
            save_email_analysis(email_id, analysis_data, item_data, vendor_data)
            saved = get_email_analysis(email_id)
            steps.append(
                f"📧 Email '{email_id}': '{analysis_data.get('item_name', '?')}' "
                f"x{analysis_data.get('quantity', '?')} — Priority: {analysis_data.get('priority', '?')}"
            )
            analyzed_count += 1

            if not saved:
                continue

        except Exception as e:
            steps.append(f"Error processing email '{email_id}': {str(e)}")

    summary = f"Pipeline complete — Extractions saved: {analyzed_count}."
    steps.append(summary)
    
    return {
        "output_text": summary,
        "steps": steps,
        "gatekeeper_results": [],
        "order_ids": []
    }


def compliance_node(state: AgentState):
    """
    Standalone compliance node: runs gatekeeper checks on ALL existing
    email_analysis records and returns results to the orchestrator.
    Creates DRAFT orders for analyses that pass and don't have an order yet.
    """
    steps = list(state.get("steps", [])) + ["Compliance Agent: Running gatekeeper checks on all analyzed emails..."]
    gatekeeper_results = []
    order_ids = []
    passed_count = failed_count = order_count = 0

    analyses = get_all_email_analyses()
    if not analyses:
        return {
            "output_text": "No analyzed emails found. Run 'analyze emails' first.",
            "steps": steps + ["Compliance Agent: No email analyses in database."],
            "gatekeeper_results": [],
            "order_ids": []
        }

    for analysis in analyses:
        item_name = analysis.get('item_name', 'Unknown')
        email_id  = analysis.get('email_id', '?')
        try:
            gate = run_gatekeeper_checks(analysis)
            explanation = explain_compliance_result(analysis, gate)
            gate['email_id'] = email_id
            gate['item_name'] = item_name
            gate['explanation'] = explanation
            gatekeeper_results.append(gate)

            if gate['passed']:
                passed_count += 1
                steps.append(f"✅ PASSED  [{item_name}]: {explanation}")

                # Create a DRAFT order if item & vendor are linked
                item_id   = analysis.get('item_id')
                vendor_id = analysis.get('vendor_id')
                amount    = analysis.get('total_cost', 0) or 0
                qty       = analysis.get('item_quantity', 1)
                if item_id and vendor_id and amount > 0:
                    order_id = create_order(
                        item_id=item_id,
                        vendor_id=vendor_id,
                        qty=qty,
                        amount=amount
                    )
                    order_ids.append(order_id)
                    order_count += 1
                    steps.append(f"📋 Order #{order_id} created — ${amount:,.2f}")
            else:
                failed_count += 1
                steps.append(f"❌ FAILED  [{item_name}]: {explanation}")

        except Exception as e:
            steps.append(f"Error checking '{item_name}' (email {email_id}): {str(e)}")

    summary = (
        f"Compliance complete — {len(analyses)} checked, "
        f"✅ {passed_count} passed, ❌ {failed_count} failed, "
        f"📋 {order_count} orders created."
    )
    if order_ids:
        summary += f" New Order IDs: {order_ids}."
    steps.append(summary)

    return {
        "output_text": summary,
        "steps": steps,
        "gatekeeper_results": gatekeeper_results,
        "order_ids": order_ids
    }


def pdf_node(state: AgentState):
    """
    Generates a PDF Purchase Order for a specific order ID extracted from user input.
    User says: 'generate pdf for order 14' → extracts 14 → generates PDF → returns download path.
    """
    import re
    import os
    from backend.database import get_db_connection

    steps = list(state.get("steps", [])) + ["PDF Agent: Starting PDF generation..."]
    input_text = state.get("input_text", "")

    # Extract order ID from input (e.g. 'generate pdf for order 14' → 14)
    numbers = re.findall(r'\d+', input_text)
    if not numbers:
        return {
            "output_text": "Please specify an order ID. Example: 'generate PDF for order 14'",
            "steps": steps + ["PDF Agent: No order ID found in input."]
        }

    order_id = int(numbers[0])
    steps.append(f"PDF Agent: Generating PDF for Order #{order_id}...")

    order = get_order_by_id(order_id)
    if not order:
        return {
            "output_text": f"Order #{order_id} not found. Check 'GET /orders' for valid IDs.",
            "steps": steps + [f"PDF Agent: Order #{order_id} not found in database."]
        }

    try:
        order_context = {
            "order_id":    order_id,
            "item_name":   order.get("item_name", "N/A"),
            "quantity":    order.get("qty", 0),
            "unit_price":  order.get("unit_price", 0),
            "total_cost":  order.get("amount", 0),
            "vendor_name": order.get("vendor_name", "N/A"),
            "vendor_email":order.get("vendor_email", "N/A"),
            "created_at":  order.get("created_at", ""),
        }

        pdf_path = generate_order_pdf(order_context)

        # Update pdf_path in orders table
        conn = get_db_connection()
        conn.execute("UPDATE orders SET pdf_path = ? WHERE id = ?", (pdf_path, order_id))
        conn.commit()
        conn.close()

        abs_path = os.path.abspath(pdf_path)
        steps.append(f"PDF Agent: ✅ PDF generated at '{pdf_path}'")

        return {
            "output_text": (
                f"📄 Purchase Order PDF for Order #{order_id} has been generated!\n"
                f"Item: {order_context['item_name']}\n"
                f"Vendor: {order_context['vendor_name']}\n"
                f"Amount: ${order_context['total_cost']:,.2f}\n"
                f"File saved at: {abs_path}\n"
                f"Or download via: POST /orders/{order_id}/generate-pdf"
            ),
            "steps": steps
        }
    except Exception as e:
        return {
            "output_text": f"Failed to generate PDF for Order #{order_id}: {str(e)}",
            "steps": steps + [f"PDF Agent: Error — {str(e)}"]
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
def route_decision(state: AgentState) -> Literal["agent_email", "agent_compliance", "agent_pdf", "unknown", "service_unavailable"]:
    decision = state["routing_decision"]
    agent_enabled_map = {
        "email":      state.get("agent_email_enabled", True),
        "compliance": state.get("agent_compliance_enabled", True),
        "pdf":        state.get("agent_pdf_enabled", True),
    }

    if decision in ["email", "compliance", "pdf"]:
        if agent_enabled_map[decision]:
            return f"agent_{decision}"
        else:
            return "service_unavailable"
    
    return "unknown"

# Build Graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("agent_email", agent_email_node)
workflow.add_node("agent_compliance", compliance_node)
workflow.add_node("agent_pdf", pdf_node)
workflow.add_node("unknown", unknown_node)
workflow.add_node("service_unavailable", service_unavailable_node)

# Set entry point
workflow.set_entry_point("orchestrator")

# Add conditional edges
workflow.add_conditional_edges(
    "orchestrator",
    route_decision,
    {
        "agent_email":       "agent_email",
        "agent_compliance":  "agent_compliance",
        "agent_pdf":         "agent_pdf",
        "unknown":           "unknown",
        "service_unavailable": "service_unavailable"
    }
)

# Add edges to END
workflow.add_edge("agent_email", END)
workflow.add_edge("agent_compliance", END)
workflow.add_edge("agent_pdf", END)
workflow.add_edge("unknown", END)
workflow.add_edge("service_unavailable", END)

# Compile
app = workflow.compile()
