import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

# Load environment variables
load_dotenv()

# Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
ORCHESTRATOR_MODEL = os.getenv("ORCHESTRATOR_MODEL", "mistral")
NUM2TEXT_MODEL = os.getenv("NUM2TEXT_MODEL", "mistral")
TEXT2NUM_MODEL = os.getenv("TEXT2NUM_MODEL", "mistral")

# Logging configuration could be set up here instead of usage of print requests.

# Initialize separate LLM instances
router_llm = ChatOllama(model=ORCHESTRATOR_MODEL, base_url=OLLAMA_BASE_URL)
num2text_llm = ChatOllama(model=NUM2TEXT_MODEL, base_url=OLLAMA_BASE_URL)
text2num_llm = ChatOllama(model=TEXT2NUM_MODEL, base_url=OLLAMA_BASE_URL)

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
        return response.content.strip()
    except Exception as e:
        return f"Error processing Num2Text: {str(e)}"

def convert_text_to_num(input_str: str) -> str:
    """
    Agent B: Converts text (e.g., 'one hundred') to digits (e.g., '100').
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
                val = float(clean_content)
                return f"{val:,}"
        except ValueError:
            pass # Return original content if not a number
            
        return content
    except Exception as e:
        return f"Error processing Text2Num: {str(e)}"

def orchestrator_router(input_str: str) -> str:
    """
    Orchestrator: Analyzes input to decide routing.
    Returns: 'num2text', 'text2num', or 'unknown'
    """
    messages = [
        SystemMessage(content="""You are an orchestration agent. Your job is to classify the user input into one of two categories:
        1. 'num2text': The input consists primarily of digits (e.g., '42', '1050').
        2. 'text2num': The input consists primarily of number words (e.g., 'forty-two', 'one hundred').
        
        Return ONLY 'num2text' or 'text2num'. If it is unclear, default to 'unknown'.
        """),
        HumanMessage(content=f"Classify this input: {input_str}")
    ]
    try:
        response = router_llm.invoke(messages)
        content = response.content.strip().lower()
        if "num2text" in content:
            return "num2text"
        elif "text2num" in content:
            return "text2num"
        else:
            return "unknown"
    except Exception as e:
        return "unknown"

# --- Email Analysis Feature ---
from pydantic import BaseModel, Field
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
