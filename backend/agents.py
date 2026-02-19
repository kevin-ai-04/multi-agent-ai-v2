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

print(f"🤖 Loading Agents:")
print(f"   - Orchestrator: {ORCHESTRATOR_MODEL}")
print(f"   - Num2Text: {NUM2TEXT_MODEL}")
print(f"   - Text2Num: {TEXT2NUM_MODEL}")

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
        return response.content.strip()
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
