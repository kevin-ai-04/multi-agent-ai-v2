"""
Shared LLM configuration and model instances for all agents.
"""
import os
from dotenv import load_dotenv, set_key
from langchain_ollama import ChatOllama
from functools import lru_cache

# Load environment variables
load_dotenv()

# Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# We keep a cache of instantiated models to avoid re-creating ChatOllama on every call
# but we need to be able to clear or update it.
llm_instances = {}

def get_current_model(agent_name: str) -> str:
    """Gets the configured model name for a specific agent from environment variables."""
    # Ensure fresh load if needed, but os.getenv is generally cached by process.
    # In a dynamic environment we might want to override this or rely on the `.env` state.
    env_keys = {
        "orchestrator": "ORCHESTRATOR_MODEL",
        "email": "EMAIL_MODEL",
        "compliance": "COMPLIANCE_MODEL",
        "po": "PO_MODEL",
        "forecast": "FORECAST_MODEL"
    }
    key = env_keys.get(agent_name, "ORCHESTRATOR_MODEL")
    return os.getenv(key, "mistral")

def get_llm(agent_name: str, format: str = None) -> ChatOllama:
    """
    Returns the ChatOllama instance for the given agent.
    Creates it if it doesn't exist or if the configuration changed.
    """
    model_name = get_current_model(agent_name)
    instance_key = f"{agent_name}_{format or 'default'}_{model_name}"
    
    # If we already created this specific instance, return it
    if instance_key in llm_instances:
        return llm_instances[instance_key]
        
    # Otherwise, create and store it
    llm = ChatOllama(model=model_name, base_url=OLLAMA_BASE_URL, format=format)
    llm_instances[instance_key] = llm
    return llm

def update_agent_model(agent_name: str, model_name: str):
    """
    Updates the model used by a specific agent and persists it to .env
    """
    env_keys = {
        "orchestrator": "ORCHESTRATOR_MODEL",
        "email": "EMAIL_MODEL",
        "compliance": "COMPLIANCE_MODEL",
        "po": "PO_MODEL",
        "forecast": "FORECAST_MODEL"
    }
    key = env_keys.get(agent_name)
    if not key:
        raise ValueError(f"Unknown agent name: {agent_name}")
        
    # Update current process environment
    os.environ[key] = model_name
    
    # Persist to .env file
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
    set_key(dotenv_path, key, model_name)
    
    # Important: We don't need to explicitly delete from llm_instances here,
    # as get_llm will automatically create a new instance with the new model_name.

# For backward compatibility during refactor, we provide helper getters that agent 
# files can use (or they can call get_llm directly).
def get_router_llm(): return get_llm("orchestrator", format="json")
def get_email_analyzer_llm(): return get_llm("email")
def get_compliance_llm(): return get_llm("compliance")
def get_po_llm(): return get_llm("po")
