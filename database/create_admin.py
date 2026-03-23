"""
File: create_admin.py
Chức năng: Tạo hoặc Cập nhật tài khoản Admin.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Registration
from werkzeug.security import generate_password_hash

def create_admin():
    with app.app_context():
        # Thông tin Admin bạn muốn tạo
        email = "admin@mindguard.com"
        password = "mindguard2025"
        
        print("🔄 Đang kiểm tra hệ thống...")

        # 1. Đảm bảo bảng dữ liệu tồn tại
        db.create_all()

        # 2. Kiểm tra xem email này đã có trong DB chưa
        user = Registration.query.filter_by(email=email).first()

        if user:
            print(f"⚠️ Tài khoản {email} đã tồn tại.")
            print("-> Đang tiến hành cấp lại quyền Admin và đặt lại mật khẩu...")
            user.role = 'admin'  # Cấp quyền admin
            user.password_hash = generate_password_hash(password) # Đặt lại pass
            user.onboarding_completed = True
        else:
            print(f"🆕 Chưa tìm thấy Admin. Đang tạo mới...")
            new_admin = Registration(
                name="Super Admin",
                email=email,
                password_hash=generate_password_hash(password),
                role="admin",  # QUAN TRỌNG: role admin
                city="Hệ thống MindGuard",
                onboarding_completed=True
            )
            db.session.add(new_admin)
        
        # 3. Lưu thay đổi
        db.session.commit()
        
        print("\n" + "="*40)
        print("✅ KHÔI PHỤC ADMIN THÀNH CÔNG!")
        print(f"👉 Link Login: http://127.0.0.1:5000/admin/login")
        print(f"📧 Email:     {email}")
        print(f"🔑 Password:  {password}")
        print("="*40)

if __name__ == "__main__":
    create_admin()