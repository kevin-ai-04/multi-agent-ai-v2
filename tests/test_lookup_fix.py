import sys
import os
from pathlib import Path

# Add current directory to path so we can import backend
sys.path.append(str(Path.cwd()))

from backend.database import get_item_by_name

def test_lookup():
    test_cases = [
        ("AC-EV-X", "Air Conditioning Unit Model X"),
        ("AC-EV", "Air Conditioning Unit Model X"),
        ("Air Conditioning", "Air Conditioning Unit Model X"),
        ("MOTOR-250KW-X", "EV Motor 250kW Model X"),
    ]
    
    for query, expected_name in test_cases:
        item = get_item_by_name(query)
        if item:
            print(f"Query: '{query}' -> Found: '{item['name']}' (ID: {item['id']})")
            if item['name'] == expected_name or expected_name in item['name']:
                print("  ✅ MATCH")
            else:
                print(f"  ❌ MISMATCH (Expected: {expected_name})")
        else:
            print(f"Query: '{query}' -> ❌ NOT FOUND")

if __name__ == "__main__":
    test_lookup()
