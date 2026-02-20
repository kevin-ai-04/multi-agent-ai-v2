import sqlite3
import json
from datetime import datetime
import os

DB_NAME = "emails.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id TEXT PRIMARY KEY,
            subject TEXT,
            sender TEXT,
            date TEXT,
            body TEXT,
            folder TEXT,
            is_read BOOLEAN DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

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
