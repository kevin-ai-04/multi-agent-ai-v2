import os
import re
from dotenv import load_dotenv
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

# Load environment variables
load_dotenv()

# Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
ORCHESTRATOR_MODEL = os.getenv("ORCHESTRATOR_MODEL", "mistral")
NUM2TEXT_MODEL = os.getenv("NUM2TEXT_MODEL", "mistral")
TEXT2NUM_MODEL = os.getenv("TEXT2NUM_MODEL", "mistral")

# Initialize separate LLM instances
router_llm = ChatOllama(model=ORCHESTRATOR_MODEL, base_url=OLLAMA_BASE_URL, format="json")
num2text_llm = ChatOllama(model=NUM2TEXT_MODEL, base_url=OLLAMA_BASE_URL)
text2num_llm = ChatOllama(model=TEXT2NUM_MODEL, base_url=OLLAMA_BASE_URL)

# --- Models ---
class UIAction(BaseModel):
    action_type: Literal["redirect", "set_filter", "popup"] = Field(description="The type of UI action to perform.")
    params: dict = Field(default_factory=dict, description="The parameters for the UI action.")

class OrchestrationResponse(BaseModel):
    decision: Literal["num2text", "text2num", "email", "unknown"] = Field(description="The routing decision for the orchestrator.")
    ui_actions: List[UIAction] = Field(default_factory=list, description="A list of UI actions.")

# --- Agents ---

def convert_num_to_text(input_str: str) -> str:
    """
    Agent A: Converts digits (e.g., '42') to text (e.g., 'forty-two').
    """
    messages = [
        SystemMessage(content="You are a helpful assistant that converts numbers given as digits into their word representation in English. Output ONLY the word representation. Do not add any conversational filler."),
        HumanMessage(content=f"Convert this number to text: {input_str}")
    ]
    try:
        response = num2text_llm.invoke(messages)
        # Use simple cleaning to remove common artifacts
        res = response.content.strip().replace('"', '').replace("'", "")
        return res
    except Exception as e:
        return f"Error processing Num2Text: {str(e)}"

def convert_text_to_num(input_str: str) -> str:
    """
    Agent B: Converts text (e.g., 'one hundred') to digits (e.g., '100').
    Simplified for model reliability.
    """
    messages = [
        SystemMessage(content="""You are a helpful assistant that converts numbers given in English words into their digit representation. 
        Output ONLY the digits. Do not add any conversational filler.
        
        Examples:
        - "one hundred five" -> 105
        - "fifteen hundred" -> 1500
        - "twenty four hundred" -> 2400
        - "two thousand four" -> 2004
        - "three thousand and twenty" -> 3020
        - "one million one" -> 1000001
        - "four thousand three twenty" -> 4320
        - "two fifty" -> 250
        - "twelve hundred fifty" -> 1250
        
        Pay close attention to place values, zeros, and colloquial phrasing where 'hundred' might be omitted.
        """),
        HumanMessage(content=f"Convert this text to number: {input_str}")
    ]
    try:
        response = text2num_llm.invoke(messages)
        content = response.content.strip()
        # Try to parse as integer to format with commas
        try:
            # Remove existing commas if any, just in case
            clean_content = content.replace(",", "").replace(" ", "")
            if clean_content.isdigit():
                val = int(clean_content)
                return f"{val:,}"
            else:
                 # Try float
                try:
                    val = float(clean_content)
                    return f"{val:,}"
                except ValueError:
                    pass
        except ValueError:
            pass # Return original content if not a number
            
        return content
    except Exception as e:
        return f"Error processing Text2Num: {str(e)}"

# --- Orchestration Structured Output ---
from typing import List, Optional, Literal

class UIAction(BaseModel):
    action_type: Literal["redirect", "set_filter", "popup", "trigger_api"] = Field(description="The type of UI action to perform.")
    params: dict = Field(default_factory=dict, description="The parameters for the UI action (e.g., view name for redirect, filter values for set_filter, endpoint and label for trigger_api).")

class OrchestrationResponse(BaseModel):
    decision: Literal["num2text", "text2num", "email", "unknown"] = Field(description="The routing decision for the orchestrator.")
    ui_actions: List[UIAction] = Field(default_factory=list, description="A list of UI actions to trigger based on user intent.")
    chat_response: Optional[str] = Field(default=None, description="A direct conversational response for greetings or banter.")

def orchestrator_router(input_str: str) -> OrchestrationResponse:
    """
    Orchestrator: Analyzed input to decide routing and UI actions.
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
    - 'decision': For ORDER or COMPLIANCE requests by ITEM NAME (e.g. "order mud flap set", "compliance for lithium battery"):
        - Set to 'unknown' and return TWO trigger_api actions in sequence:
          1. compliance: POST /procurement/compliance-by-item  payload: {{"item_name": "<extracted item name>"}}  label: "1. Run Compliance – <item name>"
          2. order:      POST /procurement/order-by-item       payload: {{"item_name": "<extracted item name>"}}  label: "2. Generate Order – <item name>"
        - chat_response should say: "Run compliance first, then generate the order."
    - 'decision': For navigation/viewing (show, list, open, go to inbox, display), use 'unknown' + ui_actions redirect.
    - 'decision': For greetings/banter/capability questions, use 'unknown' + chat_response.
    
    EXAMPLES:
    - User: "analyze emails": {{"decision": "email", "chat_response": "Starting extraction pipeline...", "ui_actions": []}}
    - User: "check compliance for 14": {{"decision": "unknown", "chat_response": "Triggering compliance for email 14.", "ui_actions": [{{"action_type": "trigger_api", "params": {{"endpoint": "/procurement/14/compliance", "method": "POST", "label": "Run Compliance (14)"}}}}]}}
    - User: "generate pdf for order 14": {{"decision": "unknown", "chat_response": "Click below to generate the PDF for order 14.", "ui_actions": [{{"action_type": "trigger_api", "params": {{"endpoint": "/orders/14/generate-pdf", "method": "POST", "label": "Generate PDF (Order 14)"}}}}]}}
    - User: "order mud flap set": {{"decision": "unknown", "chat_response": "Run compliance first, then generate the order.", "ui_actions": [{{"action_type": "trigger_api", "params": {{"endpoint": "/procurement/compliance-by-item", "method": "POST", "payload": {{"item_name": "mud flap set"}}, "label": "1. Run Compliance – Mud Flap Set"}}}}, {{"action_type": "trigger_api", "params": {{"endpoint": "/procurement/order-by-item", "method": "POST", "payload": {{"item_name": "mud flap set"}}, "label": "2. Generate Order – Mud Flap Set"}}}}]}}
    - User: "order lithium battery": {{"decision": "unknown", "chat_response": "Run compliance first, then generate the order.", "ui_actions": [{{"action_type": "trigger_api", "params": {{"endpoint": "/procurement/compliance-by-item", "method": "POST", "payload": {{"item_name": "lithium battery"}}, "label": "1. Run Compliance – Lithium Battery"}}}}, {{"action_type": "trigger_api", "params": {{"endpoint": "/procurement/order-by-item", "method": "POST", "payload": {{"item_name": "lithium battery"}}, "label": "2. Generate Order – Lithium Battery"}}}}]}}
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
        import json
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

# --- Email Analysis Feature ---
import json

class EmailExtraction(BaseModel):
    item_name: str = Field(description="The name or description of the requested product/item.")
    quantity: int = Field(description="The numeric quantity requested.")
    days_available: int = Field(description="The number of days within which the items are needed.")
    priority: str = Field(description="Priority: 'High' (within 7 days), 'Medium' (7-30 days), or 'Low' (after 30 days)")
    summary: str = Field(description="A brief 1-sentence summary of the request.")

email_analyzer_llm = ChatOllama(model=ORCHESTRATOR_MODEL, base_url=OLLAMA_BASE_URL)
# For older ollama versions or models that don't support structured output perfectly, we'll ask for JSON
# But Langchain's with_structured_output is preferred if the model supports tool calling. 
# Mistral supports tool calling, but we can also use JSON mode. Let's try with_structured_output.
structured_email_analyzer = email_analyzer_llm.with_structured_output(EmailExtraction, method="json_mode")

def analyze_email_content(body: str) -> dict:
    """
    Extracts structured procurement data from an email body using the LLM.
    Priority logic: High (<= 7 days), Medium (7-30 days), Low (> 30 days).
    """
    system_prompt = """You are a procurement analysis agent. Extract order details from the following email.
You must extract the item name, numerical quantity, and the number of days the item is needed within.
Also provide a 1-sentence summary.

Determine the Priority based strictly on the number of days:
- 'High' if needed within 7 days (or 7 days exactly).
- 'Medium' if needed between 8 and 30 days.
- 'Low' if needed after 30 days.

Respond ONLY with a valid JSON object matching the requested schema.
"""
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Email Body:\n{body}")
    ]
    try:
        # Since we initialized with method="json_mode", we rely on the schema being passed.
        # However, some ChatOllama setups require the schema as tools. 
        # For safety and backward compatibility, we will just prompt for JSON and parse it if structured output fails.
        response = email_analyzer_llm.invoke([
            SystemMessage(content=system_prompt + "\nSchema: {\"item_name\": \"str\", \"quantity\": int, \"days_available\": int, \"priority\": \"str\", \"summary\": \"str\"}\nReturn strictly raw JSON."),
            HumanMessage(content=body)
        ])
        content = response.content.strip()
        # Remove markdown code blocks if present
        if content.startswith("```json"):
             content = content[7:-3]
        elif content.startswith("```"):
             content = content[3:-3]
             
        data = json.loads(content)
        # Validate and return
        extracted = EmailExtraction(**data)
        return extracted.model_dump()
    except Exception as e:
        print(f"Error extracting email data: {e}. Raw response: {response.content if 'response' in locals() else 'None'}")
        return None


# ─────────────────────────────────────────────
# COMPLIANCE / GATEKEEPER
# ─────────────────────────────────────────────

def run_gatekeeper_checks(analysis: dict) -> dict:
    """
    Rule-based compliance checks against inventory, budgets, and policies.
    Returns: { 'passed': bool, 'failures': [str], 'warnings': [str] }
    """
    from backend.database import get_db_connection

    failures, warnings = [], []
    item_id    = analysis.get('item_id')
    vendor_id  = analysis.get('vendor_id')
    total_cost = analysis.get('total_cost', 0) or 0
    quantity   = analysis.get('quantity', 0) or 0
    item_name  = analysis.get('item_name', 'Unknown Item')

    conn = get_db_connection()
    c = conn.cursor()
    try:
        # ── Check 1: Inventory ──────────────────────────
        if item_id:
            c.execute("SELECT qty_on_hand, min_qty, max_capacity FROM inventory WHERE item_id = ?", (item_id,))
            inv = c.fetchone()
            if inv:
                if inv['qty_on_hand'] > inv['min_qty']:
                    warnings.append(
                        f"Inventory: Stock for '{item_name}' is {inv['qty_on_hand']} units "
                        f"(above min threshold of {inv['min_qty']}). Order may not be urgent."
                    )
                projected = inv['qty_on_hand'] + quantity
                if inv['max_capacity'] > 0 and projected > inv['max_capacity']:
                    failures.append(
                        f"Inventory: Ordering {quantity} units would exceed max capacity "
                        f"({projected} > {inv['max_capacity']})."
                    )
            else:
                warnings.append(f"Inventory: No record found for item_id={item_id}.")
        else:
            warnings.append("Inventory: Item not found in catalog — check skipped.")

        # ── Check 2: Budget ─────────────────────────────
        c.execute("SELECT dept, period, limit_amount, used_amount FROM budgets ORDER BY period DESC LIMIT 1")
        budget = c.fetchone()
        if budget:
            remaining = budget['limit_amount'] - budget['used_amount']
            if total_cost > remaining:
                failures.append(
                    f"Budget: Order cost ${total_cost:,.2f} exceeds remaining budget "
                    f"${remaining:,.2f} for dept '{budget['dept']}' ({budget['period']})."
                )
            else:
                warnings.append(
                    f"Budget: ${total_cost:,.2f} within budget. Remaining after order: "
                    f"${remaining - total_cost:,.2f} ({budget['dept']}, {budget['period']})."
                )
        else:
            warnings.append("Budget: No budget record found — check skipped.")

        # ── Check 3: Policies ───────────────────────────
        c.execute("SELECT value FROM policies WHERE key = 'max_single_order_amount'")
        row = c.fetchone()
        if row and total_cost > float(row['value']):
            failures.append(
                f"Policy: Order amount ${total_cost:,.2f} exceeds single-order limit of ${float(row['value']):,.2f}."
            )

        c.execute("SELECT value FROM policies WHERE key = 'min_vendor_score'")
        row = c.fetchone()
        if row and vendor_id:
            min_score = float(row['value'])
            c.execute("SELECT name, ext_score, approved FROM vendors WHERE id = ?", (vendor_id,))
            vendor = c.fetchone()
            if vendor:
                if not vendor['approved']:
                    failures.append(f"Policy: Vendor '{vendor['name']}' is not approved.")
                if vendor['ext_score'] < min_score:
                    failures.append(
                        f"Policy: Vendor '{vendor['name']}' score {vendor['ext_score']} "
                        f"is below minimum {min_score}."
                    )
    finally:
        conn.close()

    return {'passed': len(failures) == 0, 'failures': failures, 'warnings': warnings}


# LLM instance for compliance explanation
compliance_llm = ChatOllama(model=ORCHESTRATOR_MODEL, base_url=OLLAMA_BASE_URL)

def explain_compliance_result(analysis: dict, gate_result: dict) -> str:
    """
    Uses LLM to explain compliance result in plain English with recommendations.
    Returns a user-friendly narrative string.
    """
    passed     = gate_result['passed']
    failures   = gate_result.get('failures', [])
    warnings   = gate_result.get('warnings', [])
    item_name  = analysis.get('item_name', 'the requested item')
    total_cost = analysis.get('total_cost', 0) or 0
    priority   = analysis.get('priority', 'Unknown')

    status_str = "PASSED" if passed else "FAILED"
    failures_str = "\n".join(f"- {f}" for f in failures) if failures else "None"
    warnings_str = "\n".join(f"- {w}" for w in warnings) if warnings else "None"

    prompt = f"""You are a procurement compliance officer. 
Explain the compliance result for a purchase request clearly and professionally.

REQUEST DETAILS:
- Item: {item_name}
- Total Cost: ${total_cost:,.2f}
- Priority: {priority}

COMPLIANCE STATUS: {status_str}
FAILURES:
{failures_str}
WARNINGS:
{warnings_str}

Write a concise 2-4 sentence explanation:
1. State whether the request passed or failed, and why.
2. If failed, give a clear recommendation (e.g., split order, switch vendor, request budget override).
3. If passed with warnings, briefly mention them.
Keep it professional and direct. Do NOT use bullet points."""

    try:
        response = compliance_llm.invoke([
            SystemMessage(content="You are a professional procurement compliance officer. Respond in plain English only, no JSON, no bullet points."),
            HumanMessage(content=prompt)
        ])
        return response.content.strip()
    except Exception as e:
        # Fallback to raw summary if LLM fails
        if passed:
            return f"Compliance passed for '{item_name}'. {' '.join(warnings)}"
        else:
            return f"Compliance failed for '{item_name}': {' '.join(failures)}"


# ─────────────────────────────────────────────
# PDF PURCHASE ORDER GENERATION
# ─────────────────────────────────────────────

po_llm = ChatOllama(model=ORCHESTRATOR_MODEL, base_url=OLLAMA_BASE_URL)

def generate_po_content(order: dict) -> str:
    """
    Uses LLM to generate the formal text content of a Purchase Order.
    order dict should contain: item_name, quantity, unit_price, total_cost,
                               vendor_name, vendor_email, order_id, priority, created_at
    """
    prompt = f"""You are a professional procurement officer. Write a formal Purchase Order document.

ORDER DETAILS:
- PO Number: {order.get('order_id', 'N/A')}
- Date: {order.get('created_at', 'Today')}
- Item: {order.get('item_name', 'N/A')}
- Quantity: {order.get('quantity', 'N/A')} units
- Unit Price: ${order.get('unit_price', 0):,.2f}
- Total Amount: ${order.get('total_cost', 0):,.2f}
- Vendor: {order.get('vendor_name', 'N/A')}
- Vendor Email: {order.get('vendor_email', 'N/A')}
- Priority: {order.get('priority', 'Standard')}
- Company: Aurora Industries

Write the body of a professional Purchase Order letter addressed to the vendor.
Include: greeting, order specifics, expected delivery urgency based on priority, payment terms (Net 30), and a closing.
Keep it formal, concise, and ready to send. Do NOT add any JSON or formatting tags."""

    try:
        response = po_llm.invoke([
            SystemMessage(content="You are a procurement officer writing formal business documents."),
            HumanMessage(content=prompt)
        ])
        return response.content.strip()
    except Exception as e:
        # Fallback plain text
        return (
            f"PURCHASE ORDER #{order.get('order_id', 'N/A')}\n\n"
            f"To: {order.get('vendor_name', 'N/A')} ({order.get('vendor_email', 'N/A')})\n\n"
            f"We hereby place an order for {order.get('quantity')} units of "
            f"{order.get('item_name')} at ${order.get('unit_price', 0):,.2f} per unit, "
            f"totalling ${order.get('total_cost', 0):,.2f}.\n\n"
            f"Payment terms: Net 30.\n\nRegards,\nAurora Industries Procurement"
        )


def sanitize_text(text: str) -> str:
    """Replace Unicode characters that Helvetica can't render with ASCII equivalents."""
    replacements = {
        "\u2014": "--",   # em dash
        "\u2013": "-",    # en dash
        "\u2018": "'",    # left single quote
        "\u2019": "'",    # right single quote / apostrophe
        "\u201c": '"',    # left double quote
        "\u201d": '"',    # right double quote
        "\u2026": "...",  # ellipsis
        "\u00a0": " ",    # non-breaking space
        "\u00ae": "(R)",  # registered trademark
        "\u00a9": "(C)",  # copyright
        "\u2122": "(TM)", # trademark
        "\u20ac": "EUR",  # euro sign
        "\u00b0": " deg", # degree sign
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    # Final safety: drop any remaining non-latin1 characters
    return text.encode("latin-1", errors="replace").decode("latin-1")


def generate_order_pdf(order: dict, output_dir: str = "orders") -> str:
    """
    Generates a PDF Purchase Order using fpdf2.
    Returns the path to the saved PDF file.
    """
    from fpdf import FPDF
    import os
    from datetime import datetime

    os.makedirs(output_dir, exist_ok=True)
    order_id  = order.get('order_id') or order.get('id', 'unknown')
    file_path = os.path.join(output_dir, f"order_{order_id}.pdf")

    # Generate PO content via LLM and sanitize Unicode characters
    po_body = sanitize_text(generate_po_content(order))

    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)

    # ── Header ──────────────────────────────────
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 10, "PURCHASE ORDER", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"PO Number: #{order_id}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Date: {order.get('created_at', datetime.now().strftime('%Y-%m-%d'))}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(6)

    # ── Summary Table ───────────────────────────
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(30, 30, 30)
    fields = [
        ("Item",          order.get('item_name', 'N/A')),
        ("Quantity",      str(order.get('quantity', 'N/A'))),
        ("Unit Price",    f"${order.get('unit_price', 0):,.2f}"),
        ("Total Amount",  f"${order.get('total_cost', 0):,.2f}"),
        ("Vendor",        order.get('vendor_name', 'N/A')),
        ("Vendor Email",  order.get('vendor_email', 'N/A')),
        ("Priority",      order.get('priority', 'Standard')),
    ]
    for label, value in fields:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(50, 7, label + ":", new_x="RIGHT", new_y="TOP")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, str(value), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(6)

    # ── LLM-Generated PO Body ───────────────────
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "Purchase Order Details", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 6, po_body)
    pdf.ln(6)

    # ── Footer ──────────────────────────────────
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(130, 130, 130)
    pdf.cell(0, 6, "Aurora Industries -- Procurement Department", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "This is a system-generated Purchase Order.", align="C")

    pdf.output(file_path)
    return file_path
