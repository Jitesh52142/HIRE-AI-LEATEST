import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Set Flask configuration from .env file."""
    # General Config
    SECRET_KEY = os.environ.get('SECRET_KEY')
    FLASK_APP = 'run.py'
    
    # Database
    MONGO_URI = os.environ.get('MONGO_URI')

    # Webhook
    N8N_WEBHOOK_URL = os.environ.get('N8N_WEBHOOK_URL')
    
    # Admin
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')