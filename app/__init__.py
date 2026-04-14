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
        from bson.objectid import ObjectId
        if not user_id:
            return None
            
        user_json = None
        # Check if user_id is a valid ObjectId string
        if len(user_id) == 24:
            try:
                user_json = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            except:
                pass
                
        # If not found or not ObjectId, fallback to string _id or email
        if not user_json:
            user_json = mongo.db.users.find_one({'_id': user_id})
        if not user_json:
            user_json = mongo.db.users.find_one({'email': user_id})
            
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
        try:
            create_admin_user_if_not_exists()
        except Exception as e:
            print(f"Warning: Failed to create or verify admin user during startup: {e}")

    return app

def create_admin_user_if_not_exists():
    """Checks for and creates a default admin user from .env credentials."""
    admin_email = os.environ.get('ADMIN_EMAIL')
    admin_password = os.environ.get('ADMIN_PASSWORD')

    if not admin_email or not admin_password:
        print("Warning: ADMIN_EMAIL or ADMIN_PASSWORD not set in .env. Skipping admin creation.")
        return

    hashed_password = bcrypt.generate_password_hash(admin_password).decode('utf-8')

    existing = mongo.db.users.find_one({'email': admin_email})
    if not existing:
        # Create fresh admin user
        mongo.db.users.insert_one({
            '_id': admin_email,
            'email': admin_email,
            'password': hashed_password,
            'is_admin': True
        })
        print(f"Admin user '{admin_email}' created successfully.")
    elif not existing.get('password'):
        # Fix malformed doc that is missing the password field
        mongo.db.users.update_one(
            {'email': admin_email},
            {'$set': {'password': hashed_password, 'is_admin': True}}
        )
        print(f"Admin user '{admin_email}' repaired (password was missing).")
    else:
        print(f"Admin user '{admin_email}' already exists.")