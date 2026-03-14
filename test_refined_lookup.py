import sys
import os
import re
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path.cwd()))

from backend.database import get_item_by_name

def test_lookup():
    test_cases = [
        "Air Conditioning Unit Model X (SKU: AC-EV-X)",
        "AC-EV-X",
        "SKU: AC-EV-X",
        "Air Conditioning Unit",
    ]
    
    print("Testing refined lookup logic...")
    for query in test_cases:
        item = get_item_by_name(query)
        if item:
            print(f"Query: '{query}'")
            print(f"  ✅ Found: '{item['name']}' (SKU: {item['sku']}, ID: {item['id']})")
        else:
            print(f"Query: '{query}' -> ❌ NOT FOUND")

if __name__ == "__main__":
    test_lookup()
