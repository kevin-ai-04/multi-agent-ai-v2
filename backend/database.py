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
    
    # query = 'SELECT * FROM emails WHERE folder = ? ORDER BY timestamp DESC LIMIT ? OFFSET ?'
    # We use the 'date' string for sorting for now, but ideally we should parse it. 
    # For IMAP, the ID is usually sequential, so sorting by ID DESC simulates time properly enough for simple sync.
    # Actually, let's sort by ID (casted to int) DESC to show newest first.
    
    c.execute('''
        SELECT * FROM emails 
        WHERE folder = ? 
        ORDER BY CAST(id AS INTEGER) DESC 
        LIMIT ? OFFSET ?
    ''', (folder, limit, offset))
    
    rows = c.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

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
