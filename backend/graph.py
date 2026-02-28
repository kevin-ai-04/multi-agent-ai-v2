from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from backend.agents import (
    convert_num_to_text, convert_text_to_num, orchestrator_router,
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
    agent_a_enabled: bool
    agent_b_enabled: bool
    agent_email_enabled: bool
    ui_actions: list[dict]
    gatekeeper_results: list[dict]  # per-email compliance results
    order_ids: list[int]            # IDs of created DRAFT orders

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

            # ── Step 4: Compliance checks ──────────────────
            gate = run_gatekeeper_checks(saved)
            explanation = explain_compliance_result(saved, gate)
            gate['email_id'] = email_id
            gate['item_name'] = analysis_data.get('item_name', 'Unknown')
            gate['explanation'] = explanation
            gatekeeper_results.append(gate)

            if gate['passed']:
                steps.append(f"✅ Compliance PASSED: {explanation}")

                # ── Step 5: Create DRAFT order ─────────────
                if item_data and vendor_data:
                    qty = saved.get('item_quantity', 1)
                    amount = saved.get('total_cost', 0) or 0
                    order_id = create_order(
                        item_id=item_data['id'],
                        vendor_id=vendor_data['id'],
                        qty=qty,
                        amount=amount
                    )
                    order_ids.append(order_id)
                    order_count += 1
                    steps.append(
                        f"📋 Order #{order_id} created (DRAFT): {qty}x '{item_data['name']}' "
                        f"from {vendor_data['name']} — ${amount:,.2f}"
                    )
                else:
                    steps.append(f"⚠️ Order skipped: item/vendor not in catalog for email '{email_id}'.")
            else:
                rejected_count += 1
                steps.append(f"❌ Compliance FAILED: {explanation}")

        except Exception as e:
            steps.append(f"Error processing email '{email_id}': {str(e)}")

    summary = (
        f"Pipeline complete — Analyzed: {analyzed_count}, "
        f"Orders created: {order_count}, Rejected: {rejected_count}."
    )
    if order_ids:
        summary += f" Order IDs: {order_ids}. Say 'generate PDF for order #{order_ids[0]}' to create a PO document."

    steps.append(summary)
    return {
        "output_text": summary,
        "steps": steps,
        "gatekeeper_results": gatekeeper_results,
        "order_ids": order_ids
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
                    steps.append(f"📋 Order #{order_id} created (DRAFT) — ${amount:,.2f}")
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
            "priority":    order.get("status", "DRAFT"),
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
def route_decision(state: AgentState) -> Literal["agent_num2text", "agent_text2num", "agent_email", "agent_compliance", "agent_pdf", "unknown", "service_unavailable"]:
    decision = state["routing_decision"]
    agent_enabled_map = {
        "num2text":   state.get("agent_a_enabled", True),
        "text2num":   state.get("agent_b_enabled", True),
        "email":      state.get("agent_email_enabled", True),
        "compliance": state.get("agent_email_enabled", True),
        "pdf":        state.get("agent_email_enabled", True),
    }

    if decision in ["num2text", "text2num", "email", "compliance", "pdf"]:
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
        "agent_num2text":    "agent_num2text",
        "agent_text2num":    "agent_text2num",
        "agent_email":       "agent_email",
        "agent_compliance":  "agent_compliance",
        "agent_pdf":         "agent_pdf",
        "unknown":           "unknown",
        "service_unavailable": "service_unavailable"
    }
)

# Add edges to END
workflow.add_edge("agent_num2text", END)
workflow.add_edge("agent_text2num", END)
workflow.add_edge("agent_email", END)
workflow.add_edge("agent_compliance", END)
workflow.add_edge("agent_pdf", END)
workflow.add_edge("unknown", END)
workflow.add_edge("service_unavailable", END)

# Compile
app = workflow.compile()
