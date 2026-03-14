"""
Agent B: Converts text (e.g., 'one hundred') to digits (e.g., '100').
"""
from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.config import text2num_llm


def convert_text_to_num(input_str: str) -> str:
    """
    Converts text (e.g., 'one hundred') to digits (e.g., '100').
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
        try:
            clean_content = content.replace(",", "").replace(" ", "")
            if clean_content.isdigit():
                val = int(clean_content)
                return f"{val:,}"
            else:
                try:
                    val = float(clean_content)
                    return f"{val:,}"
                except ValueError:
                    pass
        except ValueError:
            pass
            
        return content
    except Exception as e:
        return f"Error processing Text2Num: {str(e)}"
