import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'mindguard.db')
print(f"Connecting to: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Attempting to add 'password_hash' column...")
    try:
        cursor.execute("ALTER TABLE registrations ADD COLUMN password_hash VARCHAR(256)")
        conn.commit()
        print("✅ Column 'password_hash' added successfully!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
             print("ℹ️ Column 'password_hash' already exists.")
        else:
             print(f"❌ Error adding column: {e}")
             
    conn.close()
except Exception as e:
    print(f"❌ Critical Error: {e}")
