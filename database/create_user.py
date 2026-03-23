import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import db, Registration
from werkzeug.security import generate_password_hash

with app.app_context():
    # Check if exists
    user = Registration.query.filter_by(email="user@gmail.com").first()
    if user:
        print("User user@gmail.com already exists. Updating password...")
        user.password_hash = generate_password_hash("user123")
    else:
        print("Creating user user@gmail.com...")
        user = Registration(
            name="Test User",
            email="user@gmail.com",
            password_hash=generate_password_hash("user123"),
            city="Hanoi",
            occupation="Tester"
        )
        db.session.add(user)
    
    db.session.commit()
    print("User 'user@gmail.com' / 'user123' created successfully!")
