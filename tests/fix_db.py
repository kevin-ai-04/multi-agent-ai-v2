import sqlite3
import traceback

with open('db_check.txt', 'w') as f:
    try:
        conn = sqlite3.connect('backend/data/procurement.db')
        c = conn.cursor()
        c.execute("PRAGMA table_info(email_analysis)")
        cols = c.fetchall()
        for col in cols:
            f.write(f"{col}\n")
        f.write("\nAttempting ALTER TABLE...\n")
        try:
            c.execute("ALTER TABLE email_analysis ADD COLUMN item_quantity INTEGER DEFAULT 0")
            conn.commit()
            f.write("Success adding column.\n")
        except sqlite3.OperationalError as e:
            f.write(f"OperationalError (maybe exists?): {e}\n")
    except Exception as e:
        f.write(traceback.format_exc())
