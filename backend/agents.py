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
    action_type: Literal["redirect", "set_filter", "popup"] = Field(description="The type of UI action to perform.")
    params: dict = Field(default_factory=dict, description="The parameters for the UI action (e.g., view name for redirect, filter values for set_filter).")

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
        {{ "action_type": "redirect" | "set_filter" | "popup", "params": {{ "view": "...", "search": "...", "priority": "High"|"Medium"|"Low", "sort": "newest"|"oldest" }} }}
      ],
      "chat_response": "string or null"
    }}
    
    RULES:
    - 'decision': If input is about numbers:
        - Use 'num2text' if input has DIGITS (e.g. '42').
        - Use 'text2num' if input has WORDS (e.g. 'forty two').
    - 'decision': Only set to 'email' if the user wants to ANALYZE, SUMMARIZE, or CHECK for specific email content.
    - 'decision': For anything else (searching emails, greetings, banter, navigation, or questions about capabilities), use 'unknown'.
    - 'chat_response': If the user is just engaging in general conversation, greetings, banter, or asking what you can do, provide a helpful and friendly reply here.
    - UI Actions:
        - DO NOT include `ui_actions` for general greetings, banter, or meta-questions (like "what can you do?").
        - For viewing/searching: use 'redirect' with view: 'emails'.
        - For specific sorting/filtering: use 'set_filter' with params 'search', 'priority', or 'sort'.
    
    EXAMPLES:
    - User: "show me high priority emails": {{"decision": "unknown", "chat_response": null, "ui_actions": [{{"action_type": "redirect", "params": {{"view": "emails"}}}}, {{"action_type": "set_filter", "params": {{"priority": "High"}}}} ]}}
    - User: "what can you do?": {{"decision": "unknown", "chat_response": "I can help with email analysis and number conversion...", "ui_actions": []}}
    - User: "general conversation": {{"decision": "unknown", "chat_response": "I am your procurement assistant. How can I help you today?", "ui_actions": []}}
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
        valid_decisions = ["num2text", "text2num", "email", "unknown"]
        if data["decision"] not in valid_decisions:
            if "email" in str(data["decision"]).lower(): data["decision"] = "email"
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
