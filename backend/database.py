import sqlite3
import json
import re
from datetime import datetime
import os
from pathlib import Path

# DB is located at backend/data/procurement.db
DB_DIR = Path(__file__).resolve().parent / "data"
DB_NAME = str(DB_DIR / "procurement.db")

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # Database initialization is now handled by scripts/db_init.py
    # We just ensure the directory exists here just in case.
    DB_DIR.mkdir(parents=True, exist_ok=True)


def save_emails(emails):
    """
    Upserts a list of email dictionaries into the database.
    """
    conn = get_db_connection()
    c = conn.cursor()
    
    for email in emails:
        c.execute('''
            INSERT OR REPLACE INTO emails (id, subject, sender, date, body, folder)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            email['id'],
            email['subject'],
            email['sender'],
            email['date'],
            email['body'],
            email['folder']
        ))
    
    conn.commit()
    conn.close()

def get_emails(folder, limit=50, offset=0):
    """
    Retrieves emails for a specific folder with pagination.
    """
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''
        SELECT e.*, 
               CASE WHEN ea.id IS NOT NULL THEN 1 ELSE 0 END as has_analysis,
               ea.priority
        FROM emails e 
        LEFT JOIN email_analysis ea ON e.id = ea.email_id
        WHERE e.folder = ? 
        ORDER BY CAST(e.id AS INTEGER) DESC 
        LIMIT ? OFFSET ?
    ''', (folder, limit, offset))
    
    rows = c.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        r = dict(row)
        r['has_analysis'] = bool(r['has_analysis'])
        result.append(r)
        
    return result

def get_tables():
    """Returns a list of all table names in the database."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row['name'] for row in c.fetchall()]
    conn.close()
    return tables

def get_table_data(table_name: str):
    """Returns all rows from a specified table."""
    conn = get_db_connection()
    c = conn.cursor()
    # Basic validation to prevent obvious SQLi. In a real app, use stricter allowlists.
    if not table_name.isidentifier():
        raise ValueError(f"Invalid table name: {table_name}")
        
    c.execute(f"SELECT * FROM {table_name}")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_table_row(table_name: str, original_row: dict, updated_row: dict):
    """
    Dynamically updates a row. Uses the original_row to construct the WHERE clause
    to ensure we update the exact row that was edited.
    """
    conn = get_db_connection()
    c = conn.cursor()
    
    if not table_name.isidentifier():
        raise ValueError("Invalid table name")

    # Construct SET clause
    set_clauses = []
    set_values = []
    for key, value in updated_row.items():
        if not key.isidentifier():
            continue
        set_clauses.append(f"{key} = ?")
        set_values.append(value)
        
    # Construct WHERE clause based on ALL original row values to act as a pseudo-primary key check
    where_clauses = []
    where_values = []
    for key, value in original_row.items():
         if not key.isidentifier():
            continue
         if value is None:
             where_clauses.append(f"{key} IS NULL")
         else:
             where_clauses.append(f"{key} = ?")
             where_values.append(value)
             
    if not set_clauses or not where_clauses:
        raise ValueError("Empty update or condition")
        
    query = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE {' AND '.join(where_clauses)}"
    
    try:
        c.execute(query, set_values + where_values)
        if c.rowcount == 0:
            raise ValueError("No matching row found to update. Data might have been concurrenty modified.")
        conn.commit()
    finally:
        conn.close()
        
    return True

def delete_table_data(table_name: str):
    """Deletes all rows from a given table."""
    conn = get_db_connection()
    c = conn.cursor()
    
    if not table_name.isidentifier():
        raise ValueError("Invalid table name")
        
    try:
        c.execute(f"DELETE FROM {table_name}")
        conn.commit()
    finally:
        conn.close()
    return True

# --- Email Analysis Features ---

def get_item_by_name(query: str):
    if not query:
        return None
        
    conn = get_db_connection()
    c = conn.cursor()
    
    # 1. Clean the query: Remove "(SKU: ...)" and other common patterns
    # Example: "Product X (SKU: SKU-123)" -> "Product X"
    clean_query = re.sub(r'\(?SKU:\s*[^)]+\)?', '', query, flags=re.IGNORECASE).strip()
    # Also extract SKU if present for direct lookup
    sku_match = re.search(r'SKU:\s*([A-Z0-9-]+)', query, flags=re.IGNORECASE)
    extracted_sku = sku_match.group(1) if sku_match else None

    # 2. Try Exact SKU match (extracted or original)
    for s in [extracted_sku, clean_query, query]:
        if s:
            c.execute("SELECT * FROM items WHERE sku = ?", (s.strip(),))
            row = c.fetchone()
            if row:
                conn.close()
                return dict(row)

    # 3. Fuzzy SKU match
    for s in [extracted_sku, clean_query]:
        if s and len(s) > 2:
            c.execute("SELECT * FROM items WHERE sku LIKE ?", (f"%{s.strip()}%",))
            row = c.fetchone()
            if row:
                conn.close()
                return dict(row)

    # 4. Fuzzy Name match (split words)
    # Use the cleaned query for name matching
    words = [w for w in clean_query.split() if len(w) > 1]
    if words:
        where_clauses = " AND ".join(["name LIKE ?"] * len(words))
        params = tuple(f"%{w}%" for w in words)
        c.execute(f"SELECT * FROM items WHERE {where_clauses}", params)
        row = c.fetchone()
        if row:
            conn.close()
            return dict(row)
            
    # 5. Fallback to simple name matching on original query
    c.execute("SELECT * FROM items WHERE name LIKE ?", (f"%{clean_query}%",))
    row = c.fetchone()
    
    conn.close()
    return dict(row) if row else None

def get_vendor(vendor_id: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM vendors WHERE id = ?", (vendor_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_unanalyzed_emails():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT e.* FROM emails e 
        LEFT JOIN email_analysis ea ON e.id = ea.email_id 
        WHERE ea.id IS NULL
        ORDER BY CAST(e.id AS INTEGER) DESC
    ''')
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_email_analysis(email_id: str):
    conn = get_db_connection()
    c = conn.cursor()
    # Join with orders to get pdf_path if it exists
    c.execute("""
        SELECT ea.*, o.pdf_path 
        FROM email_analysis ea
        LEFT JOIN orders o ON ea.order_id = o.id
        WHERE ea.email_id = ?
    """, (email_id,))
    row = c.fetchone()
    
    if not row:
        conn.close()
        return None
        
    analysis = dict(row)
    
    # ── Live Repair logic ───────────────────────────
    # If the analysis exists but vendor/item mapping is missing (NULL or "N/A"), try to fix it now.
    vendor_null_or_na = analysis.get('vendor_name') is None or str(analysis.get('vendor_name')).upper() == "N/A"
    
    if vendor_null_or_na and analysis.get('item_name'):
        try:
            item_data = get_item_by_name(analysis['item_name'])
            if item_data:
                vendor_data = get_vendor(item_data['default_vendor_id'])
                if vendor_data:
                    # Update counts and costs
                    quantity = analysis.get('item_quantity', 0)
                    unit_price = item_data.get('unit_price', 0)
                    total_cost = quantity * unit_price
                    
                    # Update the record in DB
                    c.execute('''
                        UPDATE email_analysis SET
                            item_id = ?, item_name = ?, item_unit_price = ?,
                            vendor_id = ?, vendor_name = ?, vendor_email = ?, vendor_phone = ?,
                            total_cost = ?
                        WHERE email_id = ?
                    ''', (
                        item_data.get('id'), item_data.get('name'), unit_price,
                        vendor_data.get('id'), vendor_data.get('name'), vendor_data.get('email'), vendor_data.get('phone'),
                        total_cost, email_id
                    ))
                    conn.commit()
                    
                    # Update the return object
                    analysis.update({
                        'item_id': item_data.get('id'),
                        'item_name': item_data.get('name'),
                        'item_unit_price': unit_price,
                        'vendor_id': vendor_data.get('id'),
                        'vendor_name': vendor_data.get('name'),
                        'vendor_email': vendor_data.get('email'),
                        'vendor_phone': vendor_data.get('phone'),
                        'total_cost': total_cost
                    })
        except Exception as e:
            print(f"Error during live repair of analysis '{email_id}': {e}")
            
    conn.close()
    return analysis

def get_all_email_analyses():
    """Returns all email_analysis rows for standalone compliance checking."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM email_analysis ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def find_analysis_by_item_name(item_name: str):
    """
    Fuzzy-searches email_analysis by item_name.
    Returns the most recent row so the caller can check compliance_status.
    """
    conn = get_db_connection()
    c = conn.cursor()
    words = [w for w in item_name.strip().split() if len(w) > 2]
    if not words:
        conn.close()
        return None
    where = " AND ".join(["item_name LIKE ?"] * len(words))
    params = tuple(f"%{w}%" for w in words)
    c.execute(
        f"SELECT * FROM email_analysis WHERE {where} ORDER BY id DESC LIMIT 1",
        params
    )
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def save_email_analysis(email_id: str, analysis_data: dict, item_data: dict, vendor_data: dict):
    conn = get_db_connection()
    c = conn.cursor()
    
    # Calculate total cost
    quantity = analysis_data.get('quantity', 0)
    unit_price = item_data.get('unit_price', 0) if item_data else 0
    total_cost = quantity * unit_price
    
    c.execute('''
        INSERT OR REPLACE INTO email_analysis (
            email_id, priority, summary, item_id, item_name, item_unit_price, item_quantity,
            vendor_id, vendor_name, vendor_email, vendor_phone, total_cost
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        email_id,
        analysis_data.get('priority'),
        analysis_data.get('summary'),
        item_data.get('id') if item_data else None,
        item_data.get('name') if item_data else analysis_data.get('item_name'),
        unit_price,
        quantity,
        vendor_data.get('id') if vendor_data else None,
        vendor_data.get('name') if vendor_data else None,
        vendor_data.get('email') if vendor_data else None,
        vendor_data.get('phone') if vendor_data else None,
        total_cost
    ))
    
    conn.commit()
    conn.close()
    return True


# --- Order Management ---

def get_department_for_item(item_name: str) -> str:
    """Maps an item name to its corresponding budget department based on semantic keywords."""
    if not item_name: return 'Operations'
    name_lower = item_name.lower()
    
    if any(kw in name_lower for kw in ['battery', 'lithium', 'cell', 'volt']):
        return 'Battery Dept'
    if any(kw in name_lower for kw in ['motor', 'engine', 'stator', 'rotor']):
        return 'Motor Assembly'
    if any(kw in name_lower for kw in ['glass', 'windshield', 'mirror', 'window', 'seat', 'mat', 'interior', 'leather', 'dashboard']):
        return 'Glass & Interiors'
    if any(kw in name_lower for kw in ['inverter', 'converter', 'charger', 'bms', 'ecu', 'gpu', 'sensor', 'radar', 'lidar', 'display', 'screen', 'module', 'controller', 'chip', 'processor', 'telematics']):
        return 'Electronics'
    if any(kw in name_lower for kw in ['wheel', 'tire', 'brake', 'pad', 'disc', 'suspension', 'strut', 'shock', 'chassis', 'rack']):
        return 'Chassis & Wheels'
    if any(kw in name_lower for kw in ['software', 'license', 'r&d', 'research']):
        return 'R&D'
    if any(kw in name_lower for kw in ['pump', 'radiator', 'heater', 'ac', 'cooling', 'fluid', 'washer', 'wiper']):
        return 'Engineering'
    if any(kw in name_lower for kw in ['procurement', 'admin', 'service']):
        return 'Procurement'
        
    return 'Operations'  # Fallback department

def create_order(item_id: int, vendor_id: int, qty: int, amount: float) -> int:
    """Inserts a DRAFT order. Returns the new order id."""
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO orders (item_id, qty, vendor_id, amount, status) VALUES (?, ?, ?, ?, 'DRAFT')",
            (item_id, qty, vendor_id, amount)
        )
        conn.commit()
        return c.lastrowid
    finally:
        conn.close()


def get_orders():
    """Returns all orders joined with item and vendor info."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT o.*, i.name AS item_name, i.unit_price,
               v.name AS vendor_name, v.email AS vendor_email
        FROM orders o
        LEFT JOIN items i ON o.item_id = i.id
        LEFT JOIN vendors v ON o.vendor_id = v.id
        ORDER BY o.id DESC
    """)
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_orders_paginated(page: int = 1, per_page: int = 20, status: str = None, search: str = None):
    """Returns paginated orders with total count for efficient rendering."""
    conn = get_db_connection()
    c = conn.cursor()

    where_clauses = []
    params = []

    if status:
        where_clauses.append("o.status = ?")
        params.append(status)
    if search:
        where_clauses.append("(i.name LIKE ? OR v.name LIKE ? OR CAST(o.id AS TEXT) LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    # Get total count
    c.execute(f"""
        SELECT COUNT(*) as total
        FROM orders o
        LEFT JOIN items i ON o.item_id = i.id
        LEFT JOIN vendors v ON o.vendor_id = v.id
        {where_sql}
    """, params)
    total = c.fetchone()['total']

    # Get paginated rows
    offset = (page - 1) * per_page
    c.execute(f"""
        SELECT o.*, i.name AS item_name, i.unit_price,
               v.name AS vendor_name, v.email AS vendor_email
        FROM orders o
        LEFT JOIN items i ON o.item_id = i.id
        LEFT JOIN vendors v ON o.vendor_id = v.id
        {where_sql}
        ORDER BY o.id DESC
        LIMIT ? OFFSET ?
    """, params + [per_page, offset])
    rows = c.fetchall()
    conn.close()

    total_pages = (total + per_page - 1) // per_page
    return {
        'orders': [dict(row) for row in rows],
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages
    }


def get_orders_summary():
    """Returns aggregate stats for the orders header (total volume, counts by status)."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT
            COUNT(*) as total_count,
            COALESCE(SUM(amount), 0) as total_volume,
            SUM(CASE WHEN status = 'DRAFT' THEN 1 ELSE 0 END) as draft_count,
            SUM(CASE WHEN status = 'APPROVED' THEN 1 ELSE 0 END) as approved_count
        FROM orders
    """)
    row = c.fetchone()
    conn.close()
    return dict(row)


def get_order_by_id(order_id: int):
    """Returns a single order with full item and vendor details."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT o.*, i.name AS item_name, i.unit_price,
               v.name AS vendor_name, v.email AS vendor_email
        FROM orders o
        LEFT JOIN items i ON o.item_id = i.id
        LEFT JOIN vendors v ON o.vendor_id = v.id
        WHERE o.id = ?
    """, (order_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def approve_order(order_id: int) -> bool:
    """Approves an order and deducts cost from the most recent budget."""
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT amount, item_id FROM orders WHERE id = ?", (order_id,))
        row = c.fetchone()
        if not row:
            raise ValueError(f"Order {order_id} not found.")
        amount = row['amount']
        item_id = row['item_id']
        c.execute("UPDATE orders SET status = 'APPROVED' WHERE id = ?", (order_id,))
        
        # Determine semantic budget department
        c.execute("SELECT name FROM items WHERE id = ?", (item_id,))
        item_row = c.fetchone()
        item_name = item_row['name'] if item_row else ""
        dept = get_department_for_item(item_name)
        
        c.execute("SELECT period FROM budgets WHERE dept = ? ORDER BY period DESC LIMIT 1", (dept,))
        budget = c.fetchone()
        if budget:
            c.execute(
                "UPDATE budgets SET used_amount = used_amount + ? WHERE dept = ? AND period = ?",
                (amount, dept, budget['period'])
            )
        conn.commit()
        return True
    finally:
        conn.close()


def reject_order(order_id: int) -> bool:
    """Rejects an order."""
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("UPDATE orders SET status = 'REJECTED' WHERE id = ?", (order_id,))
        conn.commit()
        return True
    finally:
        conn.close()
