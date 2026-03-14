import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path.cwd()))

from backend.database import get_db_connection, get_item_by_name, get_vendor

def fix_analyses():
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT * FROM email_analysis")
    analyses = [dict(row) for row in c.fetchall()]
    
    print(f"Checking {len(analyses)} existing records...")
    
    for analysis in analyses:
        email_id = analysis['email_id']
        item_name = analysis['item_name']
        
        print(f"Processing Email ID: {email_id} (Item: {item_name})")
        
        # 1. Re-lookup item using NEW logic
        item_data = get_item_by_name(item_name)
        if not item_data:
            print(f"  ❌ Still could not find item for '{item_name}'")
            continue
            
        # 2. Re-lookup vendor
        vendor_data = None
        if item_data.get('default_vendor_id'):
            vendor_data = get_vendor(item_data['default_vendor_id'])
            
        # 3. Update the record
        quantity = analysis.get('item_quantity', 0)
        unit_price = item_data.get('unit_price', 0)
        total_cost = quantity * unit_price
        
        c.execute('''
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
        ''', (
            item_data.get('id'),
            item_data.get('name'),
            unit_price,
            vendor_data.get('id') if vendor_data else None,
            vendor_data.get('name') if vendor_data else None,
            vendor_data.get('email') if vendor_data else None,
            vendor_data.get('phone') if vendor_data else None,
            total_cost,
            email_id
        ))
        
        print(f"  ✅ Updated: {item_data['name']} via {vendor_data['name'] if vendor_data else 'Unknown'}")
        
    conn.commit()
    conn.close()
    print("Done.")

if __name__ == "__main__":
    fix_analyses()
