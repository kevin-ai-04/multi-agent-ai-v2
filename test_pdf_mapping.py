import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path.cwd()))

def test_pdf_fields_mapping():
    print("Testing PDF Fields Mapping Logic...")
    
    # Simulating the logic from generate_order_pdf in agents.py
    def get_fields_sim(order):
        return [
            ("Item",          order.get('item_name', 'N/A')),
            ("Quantity",      str(order.get('qty', order.get('quantity', 'N/A')))),
            ("Unit Price",    f"${order.get('unit_price', 0):,.2f}"),
            ("Total Amount",  f"${order.get('amount', order.get('total_cost', 0)):,.2f}"),
            ("Vendor",        order.get('vendor_name', 'N/A')),
            ("Vendor Email",  order.get('vendor_email', 'N/A')),
            ("Priority",      order.get('priority', 'Standard')),
        ]

    # Test Case 1: Database keys
    db_order = {"qty": 5, "amount": 500.0}
    fields1 = get_fields_sim(db_order)
    print("DB Case (qty/amount):", fields1)
    # Check Quantity and Total Amount
    qty1 = next(v for l, v in fields1 if l == "Quantity")
    amt1 = next(v for l, v in fields1 if l == "Total Amount")
    
    if qty1 == "5" and amt1 == "$500.00":
        print("✅ DB SUCCESS")
    else:
        print(f"❌ DB FAILURE: qty={qty1}, amt={amt1}")

    # Test Case 2: Manual keys
    manual_order = {"quantity": 10, "total_cost": 1000.0}
    fields2 = get_fields_sim(manual_order)
    print("Manual Case (quantity/total_cost):", fields2)
    qty2 = next(v for l, v in fields2 if l == "Quantity")
    amt2 = next(v for l, v in fields2 if l == "Total Amount")
    
    if qty2 == "10" and amt2 == "$1,000.00":
        print("✅ MANUAL SUCCESS")
    else:
        print(f"❌ MANUAL FAILURE: qty={qty2}, amt={amt2}")

if __name__ == "__main__":
    test_pdf_fields_mapping()
