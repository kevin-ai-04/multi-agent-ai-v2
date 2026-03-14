import sys
import os
import sqlite3
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path.cwd()))

from backend.database import get_email_analysis, get_db_connection

def verify_live_repair():
    print("Testing Live Repair Logic...")
    
    # 1. Create a "broken" analysis record for testing
    # We'll use a unique email_id for the test.
    test_email_id = "test_case_na_fix_99"
    test_item_name = "Air Conditioning Unit Model X (SKU: AC-EV-X)"
    
    conn = get_db_connection()
    c = conn.cursor()
    # Delete if exists
    c.execute("DELETE FROM email_analysis WHERE email_id = ?", (test_email_id,))
    # Insert broken record (many NULLs)
    c.execute("""
        INSERT INTO email_analysis (email_id, item_name, vendor_name, item_quantity)
        VALUES (?, ?, NULL, 5)
    """, (test_email_id, test_item_name))
    conn.commit()
    conn.close()
    
    print(f"Created broken record for '{test_email_id}'")
    
    # 2. Call get_email_analysis - this should trigger the repair
    print("Calling get_email_analysis()...")
    analysis = get_email_analysis(test_email_id)
    
    if analysis and analysis.get('vendor_name') == "Acme Corp":
        print("  ✅ SUCCESS: Analysis repaired automatically!")
        print(f"  Fixed Item: {analysis.get('item_name')}")
        print(f"  Fixed Vendor: {analysis.get('vendor_name')}")
        print(f"  Fixed Total: ${analysis.get('total_cost')}")
    else:
        print("  ❌ FAILURE: Analysis NOT repaired.")
        print(f"  Result: {analysis}")

if __name__ == "__main__":
    verify_live_repair()
