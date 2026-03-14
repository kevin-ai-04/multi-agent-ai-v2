import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path.cwd()))

from backend.database import get_email_analysis, get_db_connection

def verify_order_fix():
    print("Verifying Order and PDF Path Logic...")
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # 1. Check if there are any orders
    c.execute("SELECT id, pdf_path FROM orders LIMIT 1")
    order = c.fetchone()
    
    if not order:
        print("  ⚠️ No orders found. Creating a dummy order for testing...")
        c.execute("INSERT INTO orders (item_id, qty, vendor_id, amount, status, pdf_path) VALUES (1, 10, 1, 100, 'DRAFT', 'orders/test.pdf')")
        conn.commit()
        order_id = c.lastrowid
        
        # Link it to an existing email analysis
        c.execute("SELECT email_id FROM email_analysis LIMIT 1")
        ea = c.fetchone()
        if ea:
            c.execute("UPDATE email_analysis SET order_id = ? WHERE email_id = ?", (order_id, ea['email_id']))
            conn.commit()
            test_email_id = ea['email_id']
        else:
            print("  ❌ No email analysis found to link.")
            conn.close()
            return
    else:
        order_id = order['id']
        c.execute("SELECT email_id FROM email_analysis WHERE order_id = ?", (order_id,))
        ea = c.fetchone()
        if ea:
            test_email_id = ea['email_id']
        else:
            print("  ❌ Could not find an email linked to order ID", order_id)
            conn.close()
            return

    conn.close()
    
    # 2. Call get_email_analysis
    print(f"Testing retrieval for Email ID: {test_email_id}")
    analysis = get_email_analysis(test_email_id)
    
    if analysis and 'pdf_path' in analysis:
        print(f"  ✅ SUCCESS: Retrieved pdf_path: {analysis['pdf_path']}")
    else:
        print(f"  ❌ FAILURE: pdf_path missing in analysis result: {analysis}")

if __name__ == "__main__":
    verify_order_fix()
