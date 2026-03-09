import sqlite3
import csv
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "backend" / "data" / "procurement.db"
CSV_PATH = BASE_DIR / "refrence-forecast" / "mock_orders.csv"

def import_mock_orders():
    print(f"Importing mock orders from {CSV_PATH} to {DB_PATH}...")
    
    if not CSV_PATH.exists():
        print(f"Error: {CSV_PATH} not found.")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Read CSV
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            # mock_orders has columns: order_id,order_date,item_id,vendor_id,quantity,unit_price,total_price
            # procurement.db orders table has columns:
            # id (auto), item_id, qty, vendor_id, amount, status, pdf_path, created_at
            # We map mock_orders.order_date to created_at
            
            cursor.execute('''
                INSERT OR IGNORE INTO orders (id, item_id, qty, vendor_id, amount, status, pdf_path, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['order_id'],
                row['item_id'],
                row['quantity'],
                row['vendor_id'],
                row['total_price'], # amount = total price
                'Completed',        # status
                None,               # pdf_path
                row['order_date']   # created_at
            ))
            count += 1
            
    conn.commit()
    conn.close()
    print(f"Successfully imported {count} mock orders for forecasting.")

if __name__ == "__main__":
    import_mock_orders()
