import os
import ollama
from dotenv import load_dotenv

# Load environment variables (like OLLAMA_HOST)
load_dotenv()

def generate_report(stats_data):
    """
    Takes the statistical data JSON/dict and sends it to the local Mistral model
    via Ollama. Returns a formatted Markdown string.
    """
    host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    model_name = os.environ.get("OLLAMA_MODEL", "mistral")
    
    try:
        # Default empty/error response from data_analyzer
        if "error" in stats_data:
            return _generate_error_md("Data Analysis Error", stats_data["error"])

        client = ollama.Client(host=host)
        
        system_prompt = (
            "You are an expert Supply Chain Analyst. Your task is to analyze the provided "
            "seasonal trend data and generate a clear, highly readable Markdown report.\n"
            "Requirements:\n"
            "- Use proper Markdown formatting (headers like #, ##, bolding, lists, tables).\n"
            "- The output MUST be ONLY valid Markdown. Do NOT wrap the output in html tags.\n"
            "- Structure the report with a clear header, an executive summary, and a detailed breakdown of the trends.\n"
            "- Do not calculate new statistics, simply present the findings beautifully."
        )
        
        user_prompt = f"Please generate the Markdown report based on the following statistical data:\n\n{stats_data}"
        
        response = client.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        html_content = response['message']['content'].strip()
        print("END", html_content)
        
        return html_content
        
    except Exception as e:
        return _generate_error_html("Ollama Agent Error", f"Could not connect to Ollama at {host} or process prompt. Ensure Ollama is running and the '{model_name}' model is pulled. Details: {str(e)}")

def _generate_error_md(title, message):
    """Helper to generate a styled error block."""
    return f"""
# ❌ {title}

**Error Details:**
{message}
"""
