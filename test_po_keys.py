import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path.cwd()))

from backend.agents import generate_po_content

def test_po_content_keys():
    print("Testing PO Content Key Matching...")
    
    # Case 1: Database keys (qty, amount)
    db_order = {
        "order_id": 123,
        "item_name": "Test Item",
        "qty": 5,
        "amount": 500.0,
        "unit_price": 100.0,
        "vendor_name": "Test Vendor",
        "vendor_email": "test@example.com",
        "created_at": "2026-03-06"
    }
    
    # Case 2: Manual keys (quantity, total_cost)
    manual_order = {
        "order_id": 456,
        "item_name": "Another Item",
        "quantity": 10,
        "total_cost": 1000.0,
        "unit_price": 100.0,
        "vendor_name": "Another Vendor",
        "vendor_email": "another@example.com",
        "created_at": "2026-03-06"
    }
    
    print("\n--- Test Case 1: Database Keys (qty/amount) ---")
    content1 = generate_po_content(db_order)
    print(content1)
    if "5 units" in content1 and "$500.00" in content1:
        print("✅ SUCCESS: Database keys matched.")
    else:
        print("❌ FAILURE: Database keys NOT matched.")
        
    print("\n--- Test Case 2: Manual Keys (quantity/total_cost) ---")
    content2 = generate_po_content(manual_order)
    print(content2)
    if "10 units" in content2 and "$1,000.00" in content2:
        print("✅ SUCCESS: Manual keys matched.")
    else:
        print("❌ FAILURE: Manual keys NOT matched.")

if __name__ == "__main__":
    test_po_content_keys()
