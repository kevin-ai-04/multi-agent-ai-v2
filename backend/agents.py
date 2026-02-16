import os
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

# Initialize the Ollama model (mistral)
llm = ChatOllama(model="mistral")

def convert_num_to_text(input_str: str) -> str:
    """
    Agent A: Converts digits (e.g., '42') to text (e.g., 'forty-two').
    """
    messages = [
        SystemMessage(content="You are a helpful assistant that converts numbers given as digits into their word representation in English. Output ONLY the word representation. Do not add any conversational filler."),
        HumanMessage(content=f"Convert this number to text: {input_str}")
    ]
    try:
        response = llm.invoke(messages)
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
        
        Pay close attention to place values and zeros.
        """),
        HumanMessage(content=f"Convert this text to number: {input_str}")
    ]
    try:
        response = llm.invoke(messages)
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
        response = llm.invoke(messages)
        content = response.content.strip().lower()
        if "num2text" in content:
            return "num2text"
        elif "text2num" in content:
            return "text2num"
        else:
            return "unknown"
    except Exception as e:
        return "unknown"
