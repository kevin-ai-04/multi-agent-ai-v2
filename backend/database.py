import sqlite3
import json
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
        SELECT e.*, CASE WHEN ea.id IS NOT NULL THEN 1 ELSE 0 END as has_analysis
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

# --- Email Analysis Features ---

def get_item_by_name(query: str):
    conn = get_db_connection()
    c = conn.cursor()
    
    # Find matching item by splitting query into words and checking if all exist in name
    # Helps match "Lithium-ion Battery Pack" to "Lithium-ion Battery Pack 75kWh Model X"
    words = query.split()
    if not words:
        conn.close()
        return None
        
    where_clauses = " AND ".join(["name LIKE ?"] * len(words))
    params = tuple(f"%{w}%" for w in words)
    
    c.execute(f"SELECT * FROM items WHERE {where_clauses}", params)
    row = c.fetchone()
    
    if not row:
        # Fallback to simple matching
        c.execute("SELECT * FROM items WHERE name LIKE ?", (f"%{query}%",))
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
    c.execute("SELECT * FROM email_analysis WHERE email_id = ?", (email_id,))
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
            email_id, priority, summary, item_id, item_name, item_unit_price,
            vendor_id, vendor_name, vendor_email, vendor_phone, total_cost
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        email_id,
        analysis_data.get('priority'),
        analysis_data.get('summary'),
        item_data.get('id') if item_data else None,
        item_data.get('name') if item_data else analysis_data.get('item_name'),
        unit_price,
        vendor_data.get('id') if vendor_data else None,
        vendor_data.get('name') if vendor_data else None,
        vendor_data.get('email') if vendor_data else None,
        None, # vendor_phone doesn't exist in new schema
        total_cost
    ))
    
    conn.commit()
    conn.close()
    return True
