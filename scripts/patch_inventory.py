import sqlite3

conn = sqlite3.connect('procurement.db')
for i in range(1, 81):
    conn.execute(f"INSERT OR IGNORE INTO inventory(item_id, qty_on_hand, max_capacity, min_qty) VALUES ({i}, 200, 5000, 50)")
conn.commit()
conn.close()
print("Inventory patched successfully.")
