import sys
import os

# Add current directory to path
# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.graph import app as workflow

def run_test(name, inputs, expected_output_contains, expected_step_contains):
    print(f"Running Test: {name}")
    print(f"Inputs: {inputs}")
    
    try:
        result = workflow.invoke(inputs)
        output = result.get("output_text", "")
        steps = result.get("steps", [])
        
        print(f"Output: {output}")
        # print(f"Steps: {steps}")
        
        # Check output
        if expected_output_contains.lower() in output.lower():
            print("[PASS] Output Check Passed")
        else:
            print(f"[FAIL] Output Check Failed. Expected '{expected_output_contains}' in '{output}'")
            
        # Check steps
        step_passed = False
        for step in steps:
            if expected_step_contains.lower() in step.lower():
                step_passed = True
                break
        
        if step_passed:
             print("[PASS] Step Check Passed")
        else:
             print(f"[FAIL] Step Check Failed. Expected '{expected_step_contains}' in steps.")
             
    except Exception as e:
        print(f"[FAIL] Exception: {e}")
    
    print("-" * 30)

if __name__ == "__main__":
    print("Starting Backend Verification...\n")
    
    # Test 1: Num2Text
    run_test(
        name="Num2Text (42)",
        inputs={"input_text": "42", "agent_a_enabled": True, "agent_b_enabled": True},
        expected_output_contains="forty-two",
        expected_step_contains="Agent A"
    )
    
    # Test 2: Text2Num
    run_test(
        name="Text2Num (one hundred)",
        inputs={"input_text": "one hundred", "agent_a_enabled": True, "agent_b_enabled": True},
        expected_output_contains="100",
        expected_step_contains="Agent B"
    )
    
    # Test 3: Unknown
    run_test(
        name="Unknown (random)",
        inputs={"input_text": "potato salad", "agent_a_enabled": True, "agent_b_enabled": True},
        expected_output_contains="could not determine",
        expected_step_contains="unknown"
    )
    
    # Test 4: Service Unavailable (Agent A disabled)
    run_test(
        name="Service Unavailable (Agent A disabled)",
        inputs={"input_text": "42", "agent_a_enabled": False, "agent_b_enabled": True},
        expected_output_contains="Service Unavailable",
        expected_step_contains="Agent disabled"
    )
