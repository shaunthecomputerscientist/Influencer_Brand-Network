from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_cors import CORS
from flask_sse import sse
from redis import StrictRedis

from models.admin import create_admin

# Initialize extensions
jwt = JWTManager()
migrate = Migrate()
mail = Mail()
cors = CORS()
redis_client = None  # Will be initialized in create_app

def initialize_extensions(app,db):
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    cors.init_app(app, supports_credentials=True, origins="*", allow_headers=["Content-Type", "Authorization", "accept"])
