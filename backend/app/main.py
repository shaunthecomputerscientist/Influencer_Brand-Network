from flask import Flask
from models.models import db
from models.admin import create_admin
from Extensions.extensions import initialize_extensions
from Blueprint.blueprints import register_blueprints
from services.Celery.celery_utils import make_celery
from services.Redis.cache_helpers import configure_redis
from config import DevelopmentConfig  # or ProductionConfig
from dotenv import load_dotenv
load_dotenv()
from flask import jsonify

# # Initialize Socket.IO with your Flask app
# socketio = SocketIO(async_mode='eventlet',cors_allowed_origins=["https://localhost:5173"])


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(config_class)
    print("app name", app.import_name)
    print(f"Loaded config: {config_class.__name__}")
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"Debug Mode: {app.config['DEBUG']}")

    # Initialize and configure components
    initialize_extensions(app, db=db)
    register_blueprints(app)
    configure_redis(app)
    
    # Set up Celery instance
    celery = make_celery(app)
    app.config['CELERY'] = celery
    celery.conf.update(app.config)
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
        from models.models import User
        create_admin(db, User, app)
    
    
    return app, celery

# Create the Flask app instance
app, celery = create_app()

def print_routes():
    for rule in app.url_map.iter_rules():
        methods = ', '.join(rule.methods)
        print(f"Path: {rule}, Methods: {methods}")



@app.errorhandler(404)
def not_found(error):
    return jsonify({"message": "Resource not found"}), 404

if __name__ == '__main__':
    print_routes()
    app.run(ssl_context=('ssl-certificates/selfsigned.crt', 'ssl-certificates/selfsigned.key'), debug=True, host='0.0.0.0', port=5000)
    # socketio.run(app,
    #              debug=True, host='0.0.0.0', port=5000)
    # app.run(debug=True, host='0.0.0.0', port=5000)