"""
Orchestrator: Analyzes input to decide routing and UI actions.
"""
import json

from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.config import get_router_llm
from backend.agents.models import OrchestrationResponse


def orchestrator_router(input_str: str) -> OrchestrationResponse:
    """
    Orchestrator: Analyzes input to decide routing and UI actions.
    Simplified for Mistral reliability using native JSON mode.
    """
    prompt = f"""You are an AI orchestrator.
    Respond exclusively in valid JSON format corresponding to this schema:
    {{
      "decision": "email" | "compliance" | "pdf" | "unknown",
      "reasoning": "<short string>",
      "ui_actions": [
        {{ "action_type": "redirect" | "set_filter" | "popup" | "trigger_api" | "open_inline_procurement", "params": {{ "view": "...", "search": "...", "priority": "High"|"Medium"|"Low", "sort": "newest"|"oldest", "endpoint": "...", "method": "POST", "label": "...", "item_name": "...", "mode": "manual" }} }}
      ],
      "chat_response": "string or null"
    }}

    Guidelines:
    - Use 'email' if the user wants to analyze emails.
    - Use 'compliance' if the user wants to run or check policies.
    - Use 'pdf' if the user wants to generate, download, or create a purchase order or PDF document.
    - Use 'unknown' if it doesn't clearly map to these.

    RULES:
    - 'decision': Set to 'email' ONLY for active processing: ANALYZE ALL, PROCESS, SCAN emails for data. Keywords: analyze, analyse, process, scan inbox.
    - 'decision': IMPORTANT — For 'email', set ui_actions to [] (background pipeline, no navigation).
    - 'decision': For COMPLIANCE or ORDER by numeric ID, set to 'unknown' + trigger_api:
        - Endpoint for compliance by email id: "/procurement/<id>/compliance"
        - Endpoint for order PDF by order id: "/orders/<id>/generate-pdf"
        - If ID is missing, ask the user via chat_response.
    - 'decision': For ORDER or COMPLIANCE requests by ITEM NAME (e.g. "order mud flap set", "compliance for lithium battery") or manual orders:
        - Set 'decision' to 'unknown'.
        - Set 'ui_actions' to: [{{ "action_type": "open_inline_procurement", "params": {{ "item_name": "<extracted item name>", "mode": "manual" }} }}]
        - 'chat_response' should say: "I can help you with that order. Please review the details below."
    - 'decision': For navigation/viewing (show, list, open, go to inbox, display), use 'unknown' + ui_actions redirect.
    - 'decision': For greetings/banter/capability questions, use 'unknown' + chat_response.

    EXAMPLES:
    - User: "analyze emails": {{"decision": "email", "reasoning": "User wants to analyze emails", "chat_response": "Starting extraction pipeline...", "ui_actions": []}}
    - User: "check compliance for 14": {{"decision": "unknown", "reasoning": "Compliance check by ID", "chat_response": "Triggering compliance for email 14.", "ui_actions": [{{"action_type": "trigger_api", "params": {{"endpoint": "/procurement/14/compliance", "method": "POST", "label": "Run Compliance (14)"}}}}]}}
    - User: "generate pdf for order 14": {{"decision": "unknown", "reasoning": "PDF generation by order ID", "chat_response": "Click below to generate the PDF for order 14.", "ui_actions": [{{"action_type": "trigger_api", "params": {{"endpoint": "/orders/14/generate-pdf", "method": "POST", "label": "Generate PDF (Order 14)"}}}}]}}
    - User: "order mud flap set": {{"decision": "unknown", "reasoning": "Manual order by item name", "chat_response": "I can help you with that order. Please review the details below.", "ui_actions": [{{"action_type": "open_inline_procurement", "params": {{"item_name": "mud flap set", "mode": "manual"}}}}]}}
    - User: "order lithium battery": {{"decision": "unknown", "reasoning": "Manual order by item name", "chat_response": "I can help you with that order. Please review the details below.", "ui_actions": [{{"action_type": "open_inline_procurement", "params": {{"item_name": "lithium battery", "mode": "manual"}}}}]}}
    - User: "show me high priority emails": {{"decision": "unknown", "reasoning": "Navigation/filtering request", "chat_response": null, "ui_actions": [{{"action_type": "redirect", "params": {{"view": "emails"}}}}, {{"action_type": "set_filter", "params": {{"priority": "High"}}}}]}}

    User Input: "{input_str}"
    """

    messages = [
        SystemMessage(content="You are a JSON-only orchestrator. You only output valid JSON matching the requested schema."),
        HumanMessage(content=prompt)
    ]

    try:
        response = get_router_llm().invoke(messages)
        data = json.loads(response.content)

        # Robust mapping back to our preferred schema if LLM hallucinated keys
        if "decision" not in data:
            if "action" in data: data["decision"] = data["action"]
            elif "intent" in data: data["decision"] = data["intent"]
            else: data["decision"] = "unknown"

        # Mapping ui_actions
        if "ui_actions" not in data:
            data["ui_actions"] = []
            for key in ["actions", "ui_hints", "hints"]:
                if key in data and isinstance(data[key], list):
                    data["ui_actions"] = data[key]
                    break

        valid_decisions = ["email", "compliance", "pdf", "unknown"]
        if data.get("decision") not in valid_decisions:
            # Simple fallback heuristic
            if "pdf" in str(data.get("decision", "")).lower():
                data["decision"] = "pdf"
            elif "email" in str(data.get("decision", "")).lower():
                data["decision"] = "email"
            elif "compliance" in str(data.get("decision", "")).lower():
                data["decision"] = "compliance"
            else:
                data["decision"] = "unknown"

        print(f"Orchestrator Input: '{input_str}' -> Final Data: {data}\n")
        return OrchestrationResponse(**data)
    except Exception as e:
        print(f"Error in simplified orchestrator: {e}")
        return OrchestrationResponse(decision="unknown", ui_actions=[])
