import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'mindguard_v2.db')
print(f"Checking database at: {db_path}")

if not os.path.exists(db_path):
    print("❌ Database file does not exist!")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Existing tables:")
        if not tables:
            print("  (No tables found)")
        for table in tables:
            print(f"  - {table[0]}")
            
        # specifically check for registrations
        cursor.execute("PRAGMA table_info(registrations)")
        columns = cursor.fetchall()
        if columns:
            print("\nColumns in registrations:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        else:
            print("\n❌ Table 'registrations' NOT FOUND.")
            
        conn.close()
    except Exception as e:
        print(f"❌ Error reading database: {e}")
