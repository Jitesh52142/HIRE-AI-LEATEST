import os
from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from .models.user import User
from config import Config

# Initialize extensions
mongo = PyMongo()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login' # Redirect to login page if user is not authenticated
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    """
    Application factory function to create and configure the Flask app.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with the app
    mongo.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        """Load user from the database."""
        user_json = mongo.db.users.find_one({'_id': user_id})
        if user_json:
            return User(user_json)
        return None

    # Register blueprints
    from .routes.main import main_bp
    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp
    from .routes.candidates import candidates_bp
    from .routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(candidates_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    with app.app_context():
        # Create a default admin user if one doesn't exist
        create_admin_user_if_not_exists()

    return app

def create_admin_user_if_not_exists():
    """Checks for and creates a default admin user from .env credentials."""
    admin_email = os.environ.get('ADMIN_EMAIL')
    admin_password = os.environ.get('ADMIN_PASSWORD')

    if not admin_email or not admin_password:
        print("Warning: ADMIN_EMAIL or ADMIN_PASSWORD not set in .env. Skipping admin creation.")
        return

    # Check if admin user already exists
    if not mongo.db.users.find_one({'email': admin_email}):
        hashed_password = bcrypt.generate_password_hash(admin_password).decode('utf-8')
        mongo.db.users.insert_one({
            '_id': admin_email, # Using email as a unique ID
            'email': admin_email,
            'password': hashed_password,
            'is_admin': True
        })
        print(f"Admin user '{admin_email}' created successfully.")