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
    
    # Test 3: Unknown
    run_test(
        name="Unknown (random)",
        inputs={"input_text": "potato salad"},
        expected_output_contains="could not determine",
        expected_step_contains="unknown"
    )
