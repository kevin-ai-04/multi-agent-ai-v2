import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from backend.agents.config import get_current_model, get_llm, update_agent_model, llm_instances

def main():
    print("Testing config system...")
    
    # 1. Test get_current_model defaults
    print(f"Default email model: {get_current_model('email')}")
    
    # 2. Test get_llm instantiation
    llm1 = get_llm("email")
    print(f"Instantiated model name: {llm1.model}")
    print(f"Instance cache keys before update: {list(llm_instances.keys())}")
    
    # 3. Update the model
    print("\nUpdating 'email' model to 'llama3.1'...")
    update_agent_model("email", "llama3.1")
    
    # 4. New retrieval
    llm2 = get_llm("email")
    print(f"New instantiated model name: {llm2.model}")
    print(f"Instance cache keys after update: {list(llm_instances.keys())}")
    
    # 5. Reset to mistral to keep .env clean
    update_agent_model("email", "mistral")
    
    print("\nAll tests pass if llama3.1 was shown above!")

if __name__ == "__main__":
    main()
