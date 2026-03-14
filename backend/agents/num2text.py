"""
Agent A: Converts digits (e.g., '42') to text (e.g., 'forty-two').
"""
from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.config import num2text_llm


def convert_num_to_text(input_str: str) -> str:
    """
    Converts digits (e.g., '42') to text (e.g., 'forty-two').
    """
    messages = [
        SystemMessage(content="You are a helpful assistant that converts numbers given as digits into their word representation in English. Output ONLY the word representation. Do not add any conversational filler."),
        HumanMessage(content=f"Convert this number to text: {input_str}")
    ]
    try:
        response = num2text_llm.invoke(messages)
        res = response.content.strip().replace('"', '').replace("'", "")
        return res
    except Exception as e:
        return f"Error processing Num2Text: {str(e)}"
