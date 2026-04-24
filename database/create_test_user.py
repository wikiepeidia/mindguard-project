import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import db, Registration
from werkzeug.security import generate_password_hash

with app.app_context():
    # Check if exists
    user = Registration.query.filter_by(email="admin@gmail.com").first()
    if user:
        print("User admin@gmail.com already exists. Updating password...")
        user.password_hash = generate_password_hash("admin")
    else:
        print("Creating user admin@gmail.com...")
        user = Registration(
            name="Super User",
            email="admin@gmail.com",
            password_hash=generate_password_hash("admin"),
            city="Hanoi",
            occupation="Tester"
        )
        db.session.add(user)
    
    db.session.commit()
    print("User 'admin@gmail.com' / 'admin' created successfully!")
