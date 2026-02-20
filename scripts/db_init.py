import sqlite3
import os
from pathlib import Path

# Set up the database path
DB_DIR = Path(__file__).resolve().parents[1] / "backend" / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "procurement.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. emails table (copied from previous emails.db with structure)
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

    # 2. email_analysis table
    c.execute('''
        CREATE TABLE IF NOT EXISTS email_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_id TEXT NOT NULL,
            priority TEXT,
            summary TEXT,
            item_id INTEGER,
            item_name TEXT,
            item_unit_price REAL,
            vendor_id INTEGER,
            vendor_name TEXT,
            vendor_email TEXT,
            vendor_phone TEXT,
            total_cost REAL,
            FOREIGN KEY(email_id) REFERENCES emails(id)
        )
    ''')

    # 3. items table
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            sku TEXT,
            item_unit_qty INTEGER,
            item_unit_price REAL,
            item_vendor_id TEXT -- comma-separated string of vendor IDs
        )
    ''')

    # 4. vendors table
    c.execute('''
        CREATE TABLE IF NOT EXISTS vendors (
            vendor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_name TEXT NOT NULL,
            vendor_email TEXT,
            vendor_phone TEXT,
            vendor_approved BOOLEAN DEFAULT 1,
            vendor_score REAL
        )
    ''')

    # 5. inventory table
    c.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            item_id INTEGER PRIMARY KEY,
            qty_on_hand INTEGER DEFAULT 0,
            max_capacity INTEGER DEFAULT 0,
            min_qty INTEGER DEFAULT 0,
            FOREIGN KEY(item_id) REFERENCES items(item_id)
        )
    ''')

    # 6. budget table
    c.execute('''
        CREATE TABLE IF NOT EXISTS budget (
            dept TEXT,
            period TEXT,
            limit_amount REAL,
            used_amount REAL DEFAULT 0,
            PRIMARY KEY(dept, period)
        )
    ''')

    # 7. policies table
    c.execute('''
        CREATE TABLE IF NOT EXISTS policies (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    # 8. orders table
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            qty INTEGER,
            vendor_id INTEGER,
            total_amount REAL,
            status TEXT DEFAULT 'DRAFT',
            pdf_path TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(item_id) REFERENCES items(item_id),
            FOREIGN KEY(vendor_id) REFERENCES vendors(vendor_id)
        )
    ''')

    print(f"Schema created successfully at {DB_PATH}")

    # --- SEED DATA ---
    print("Seeding data...")

    # Seed Policies
    c.execute("INSERT OR REPLACE INTO policies (key, value) VALUES ('max_single_order_amount', '50000')")
    c.execute("INSERT OR REPLACE INTO policies (key, value) VALUES ('min_vendor_score', '80')")
    c.execute("INSERT OR REPLACE INTO policies (key, value) VALUES ('max_open_orders', '10')")

    # Seed Budgets
    budgets = [
        ('IT', '2026-Q1', 100000.0, 15000.0),
        ('Operations', '2026-Q1', 250000.0, 50000.0),
        ('Facilities', '2026-Q1', 50000.0, 5000.0)
    ]
    c.executemany("INSERT OR IGNORE INTO budget (dept, period, limit_amount, used_amount) VALUES (?, ?, ?, ?)", budgets)

    # Seed Vendors (adapted from reference)
    vendors = [
        (1, 'TechCorp Solutions', 'sales@techcorp.com', '555-0101', 1, 92.5),
        (2, 'OfficeSupplies Inc', 'orders@officesupplies.com', '555-0102', 1, 88.0),
        (3, 'Global Hardware Co', 'b2b@globalhardware.com', '555-0103', 1, 85.5),
        (4, 'FastShip Logistics', 'support@fastship.com', '555-0104', 1, 95.0),
        (5, 'Discount Electronics', 'sales@discountelectronics.com', '555-0105', 0, 72.0)
    ]
    c.executemany("INSERT OR IGNORE INTO vendors (vendor_id, vendor_name, vendor_email, vendor_phone, vendor_approved, vendor_score) VALUES (?, ?, ?, ?, ?, ?)", vendors)

    # Seed Items (adapted from reference, with item_vendor_id as comma separated string)
    items = [
        (1, 'ThinkPad T14 Laptop', 'LAP-T14-001', 1, 1200.00, '1,5'),
        (2, 'Ergonomic Desk Chair', 'FURN-CHR-002', 1, 250.00, '2'),
        (3, '27-inch 4K Monitor', 'MON-27-4K', 1, 350.00, '1,3,5'),
        (4, 'Wireless Mouse', 'PER-MOU-004', 1, 45.00, '1,2,3'),
        (5, 'Server Rack 42U', 'SRV-RCK-005', 1, 800.00, '3')
    ]
    c.executemany("INSERT OR IGNORE INTO items (item_id, item_name, sku, item_unit_qty, item_unit_price, item_vendor_id) VALUES (?, ?, ?, ?, ?, ?)", items)

    # Seed Inventory
    inventory = [
        (1, 15, 50, 10),
        (2, 40, 100, 20),
        (3, 8, 30, 15),
        (4, 120, 200, 50),
        (5, 2, 10, 3)
    ]
    c.executemany("INSERT OR IGNORE INTO inventory (item_id, qty_on_hand, max_capacity, min_qty) VALUES (?, ?, ?, ?)", inventory)

    # Seed Orders
    orders = [
        (1, 1, 5, 1, 6000.00, 'DELIVERED', '/docs/orders/ord_001.pdf'),
        (2, 3, 10, 3, 3500.00, 'PENDING', '/docs/orders/ord_002.pdf'),
        (3, 2, 20, 2, 5000.00, 'DRAFT', '/docs/orders/ord_003.pdf')
    ]
    c.executemany("INSERT OR IGNORE INTO orders (order_id, item_id, qty, vendor_id, total_amount, status, pdf_path) VALUES (?, ?, ?, ?, ?, ?, ?)", orders)

    conn.commit()
    conn.close()
    print("Database initialization and seeding complete.")

if __name__ == "__main__":
    init_db()
