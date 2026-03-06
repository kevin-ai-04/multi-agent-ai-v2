import sqlite3
import os

db_path = os.path.join("backend", "data", "procurement.db")

def force_fix():
    print(f"Connecting to {db_path}...")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Get all items for mapping
    c.execute("SELECT * FROM items")
    items = [dict(r) for r in c.fetchall()]
    
    # Get all vendors for mapping
    c.execute("SELECT * FROM vendors")
    vendors = {v['id']: dict(v) for v in [dict(r) for r in c.fetchall()]}
    
    # Get all analyses that are "N/A" (vendor_name is null)
    c.execute("SELECT * FROM email_analysis WHERE vendor_name IS NULL")
    analyses = [dict(r) for r in c.fetchall()]
    
    print(f"Found {len(analyses)} records to fix.")
    
    for analysis in analyses:
        email_id = analysis['email_id']
        found_item = None
        
        # Simple matching logic similar to my fix
        for item in items:
            name_match = (analysis['item_name'] and analysis['item_name'].lower() in item['name'].lower())
            sku_match = (analysis['item_name'] and analysis['item_name'] == item['sku'])
            
            if sku_match or name_match:
                found_item = item
                break
        
        if found_item:
            vendor = vendors.get(found_item['default_vendor_id'])
            if vendor:
                total_cost = (analysis['item_quantity'] or 0) * (found_item['unit_price'] or 0)
                
                c.execute("""
                    UPDATE email_analysis SET
                        item_id = ?,
                        item_name = ?,
                        item_unit_price = ?,
                        vendor_id = ?,
                        vendor_name = ?,
                        vendor_email = ?,
                        vendor_phone = ?,
                        total_cost = ?
                    WHERE email_id = ?
                """, (
                    found_item['id'], found_item['name'], found_item['unit_price'],
                    vendor['id'], vendor['name'], vendor['email'], vendor['phone'],
                    total_cost, email_id
                ))
                print(f"  Fixed {email_id}: Found {found_item['name']} via {vendor['name']}")
            else:
                print(f"  Item found for {email_id} but no vendor found for ID {found_item['default_vendor_id']}")
        else:
            print(f"  Could not find item for {email_id} ({analysis['item_name']})")
            
    conn.commit()
    conn.close()
    print("Force fix complete.")

if __name__ == "__main__":
    force_fix()
