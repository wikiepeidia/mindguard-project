"""Quick migration to add new columns to database"""
import sqlite3
import os

# Path to database
db_path = os.path.join('database', 'mindguard_v2.db')

if not os.path.exists(db_path):
    print(f"❌ Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check existing columns
    cursor.execute("PRAGMA table_info(scammer_reports)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"📋 Existing columns: {columns}")
    
    # Add verification_status if not exists
    if 'verification_status' not in columns:
        print("➕ Adding verification_status...")
        cursor.execute("ALTER TABLE scammer_reports ADD COLUMN verification_status VARCHAR(20) DEFAULT 'unverified'")
        print("✅ Added verification_status")
    else:
        print("⏭️  verification_status already exists")
    
    # Add risk_score if not exists
    if 'risk_score' not in columns:
        print("➕ Adding risk_score...")
        cursor.execute("ALTER TABLE scammer_reports ADD COLUMN risk_score INTEGER DEFAULT 0")
        print("✅ Added risk_score")
    else:
        print("⏭️  risk_score already exists")
    
    # Add confirmed_by_count if not exists
    if 'confirmed_by_count' not in columns:
        print("➕ Adding confirmed_by_count...")
        cursor.execute("ALTER TABLE scammer_reports ADD COLUMN confirmed_by_count INTEGER DEFAULT 0")
        print("✅ Added confirmed_by_count")
    else:
        print("⏭️  confirmed_by_count already exists")
    
    conn.commit()
    print("\n✅ Migration completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    conn.close()
