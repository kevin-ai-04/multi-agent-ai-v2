"""
Shared LLM configuration and model instances for all agents.
"""
import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

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
email_analyzer_llm = ChatOllama(model=ORCHESTRATOR_MODEL, base_url=OLLAMA_BASE_URL)
compliance_llm = ChatOllama(model=ORCHESTRATOR_MODEL, base_url=OLLAMA_BASE_URL)
po_llm = ChatOllama(model=ORCHESTRATOR_MODEL, base_url=OLLAMA_BASE_URL)
