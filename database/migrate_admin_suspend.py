"""
Migration: thêm is_suspended và suspended_reason vào bảng registrations.
Chạy một lần: python database/migrate_admin_suspend.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'mindguard_v2.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Kiểm tra cột đã tồn tại chưa
    cursor.execute("PRAGMA table_info(registrations)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    if 'is_suspended' not in existing_columns:
        cursor.execute("ALTER TABLE registrations ADD COLUMN is_suspended BOOLEAN DEFAULT 0")
        print("✓ Đã thêm cột is_suspended")
    else:
        print("- is_suspended đã tồn tại, bỏ qua")

    if 'suspended_reason' not in existing_columns:
        cursor.execute("ALTER TABLE registrations ADD COLUMN suspended_reason VARCHAR(255)")
        print("✓ Đã thêm cột suspended_reason")
    else:
        print("- suspended_reason đã tồn tại, bỏ qua")

    conn.commit()
    conn.close()
    print("Migration hoàn tất.")

if __name__ == '__main__':
    migrate()
