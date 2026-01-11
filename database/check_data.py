import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'mindguard.db')
print(f"Checking data in: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check Registrations
    cursor.execute("SELECT count(*) FROM registrations")
    reg_count = cursor.fetchone()[0]
    print(f"Registrations: {reg_count}")
    
    # Check ScamReport (Old)
    cursor.execute("SELECT count(*) FROM scam_reports")
    old_scam_count = cursor.fetchone()[0]
    print(f"ScamReport (Old): {old_scam_count}")
    
    # Check ScammerReport (New)
    cursor.execute("SELECT count(*) FROM scammer_reports")
    new_scammer_count = cursor.fetchone()[0]
    print(f"ScammerReport (New): {new_scammer_count}")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")
