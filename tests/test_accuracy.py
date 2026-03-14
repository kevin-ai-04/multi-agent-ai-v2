import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.agents import convert_text_to_num

def test_text2num_accuracy():
    test_cases = [
        ("two thousand four", "2,004"),
        ("one hundred five", "105"),
        ("three thousand and twenty", "3,020"),
        ("one million one", "1,000,001"),
        ("twenty four hundred", "2,400")
    ]
    
    print("Testing Text2Num Accuracy...\n")
    
    for input_text, expected in test_cases:
        result = convert_text_to_num(input_text)
        if result == expected:
            print(f"✅ Input: '{input_text}' -> Output: '{result}' (PASS)")
        else:
            print(f"❌ Input: '{input_text}' -> Output: '{result}' (FAIL, Expected: '{expected}')")

if __name__ == "__main__":
    test_text2num_accuracy()
