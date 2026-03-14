"""
Orchestrator: Analyzes input to decide routing and UI actions.
"""
import json

from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.config import router_llm
from backend.agents.models import OrchestrationResponse


def orchestrator_router(input_str: str) -> OrchestrationResponse:
    """
    Orchestrator: Analyzes input to decide routing and UI actions.
    Simplified for Mistral reliability using native JSON mode.
    """
    prompt = f"""You are an AI orchestrator. 
    You MUST respond with a JSON object exactly matching this structure:
    {{
      "decision": "num2text" | "text2num" | "email" | "unknown",
      "ui_actions": [
        {{ "action_type": "redirect" | "set_filter" | "popup" | "trigger_api", "params": {{ "view": "...", "search": "...", "priority": "High"|"Medium"|"Low", "sort": "newest"|"oldest", "endpoint": "...", "method": "POST", "label": "..." }} }}
      ],
      "chat_response": "string or null"
    }}
    
    RULES:
    - 'decision': If input is about numbers:
        - Use 'num2text' if input has DIGITS (e.g. '42').
        - Use 'text2num' if input has WORDS (e.g. 'forty two').
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
    - User: "analyze emails": {{"decision": "email", "chat_response": "Starting extraction pipeline...", "ui_actions": []}}
    - User: "check compliance for 14": {{"decision": "unknown", "chat_response": "Triggering compliance for email 14.", "ui_actions": [{{"action_type": "trigger_api", "params": {{"endpoint": "/procurement/14/compliance", "method": "POST", "label": "Run Compliance (14)"}}}}]}}
    - User: "generate pdf for order 14": {{"decision": "unknown", "chat_response": "Click below to generate the PDF for order 14.", "ui_actions": [{{"action_type": "trigger_api", "params": {{"endpoint": "/orders/14/generate-pdf", "method": "POST", "label": "Generate PDF (Order 14)"}}}}]}}
    - User: "order mud flap set": {{"decision": "unknown", "chat_response": "I can help you with that order. Please review the details below.", "ui_actions": [{{"action_type": "open_inline_procurement", "params": {{"item_name": "mud flap set", "mode": "manual"}}}}]}}
    - User: "order lithium battery": {{"decision": "unknown", "chat_response": "I can help you with that order. Please review the details below.", "ui_actions": [{{"action_type": "open_inline_procurement", "params": {{"item_name": "lithium battery", "mode": "manual"}}}}]}}
    - User: "show me high priority emails": {{"decision": "unknown", "chat_response": null, "ui_actions": [{{"action_type": "redirect", "params": {{"view": "emails"}}}}, {{"action_type": "set_filter", "params": {{"priority": "High"}}}}]}}
    - User: "convert forty two": {{"decision": "text2num", "chat_response": null, "ui_actions": []}}
    
    User Input: "{input_str}"
    """
    
    messages = [
        SystemMessage(content="You are a JSON-only orchestrator. You only output valid JSON matching the requested schema."),
        HumanMessage(content=prompt)
    ]
    
    try:
        response = router_llm.invoke(messages)
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
        
        # Standardize decision values
        valid_decisions = ["num2text", "text2num", "email", "compliance", "pdf", "unknown"]
        if data["decision"] not in valid_decisions:
            if "pdf" in str(data["decision"]).lower(): data["decision"] = "pdf"
            elif "email" in str(data["decision"]).lower(): data["decision"] = "email"
            elif "compliance" in str(data["decision"]).lower(): data["decision"] = "compliance"
            elif "num" in str(data["decision"]).lower(): data["decision"] = "num2text" 
            else: data["decision"] = "unknown"
            
        print(f"Orchestrator Input: '{input_str}' -> Final Data: {data}\n")
        return OrchestrationResponse(**data)
    except Exception as e:
        print(f"Error in simplified orchestrator: {e}")
        return OrchestrationResponse(decision="unknown", ui_actions=[])
