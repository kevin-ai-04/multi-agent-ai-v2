"""
Email Analysis Agent: Extracts structured procurement data from email bodies.
"""
import json

from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.config import get_email_analyzer_llm
from backend.agents.models import EmailExtraction


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
    try:
        response = get_email_analyzer_llm().invoke([
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
