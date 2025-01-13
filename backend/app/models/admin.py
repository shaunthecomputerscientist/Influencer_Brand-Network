# from models import db
from werkzeug.security import generate_password_hash

def create_admin(db, User, app):
    # Check if the admin already exists
    admin = User.query.filter_by(role=0).first()  # Admin role assumed to be 0

    if admin is None:
        # Admin doesn't exist, so create one
        admin_password = generate_password_hash(app.config['SECRET_KEY'])  # Use secret key as the admin password
        admin = User(
            username='admin',
            password=admin_password,
            role=0,  # 0 for admin
            name='Admin',
            email='admin@example.com',
            location='N/A',
            description='Administrator',
            profile_image=None,
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created.")

