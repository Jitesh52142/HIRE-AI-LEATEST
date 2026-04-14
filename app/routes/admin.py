from functools import wraps
from flask import Blueprint, render_template, abort
from flask_login import current_user, login_required
from app import mongo
from bson import ObjectId
import os

admin_bp = Blueprint('admin', __name__)

# --- Admin Required Decorator ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_email = os.environ.get('ADMIN_EMAIL')
        if not current_user.is_authenticated or current_user.email != admin_email:
            abort(403) # Forbidden
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def admin_dashboard():
    # Fetch all data from MongoDB collections
    collections = {}
    try:
        collection_names = mongo.db.list_collection_names()
        for name in collection_names:
            docs = []
            for doc in mongo.db[name].find():
                # Convert ObjectId to string so templates can render them
                if '_id' in doc and isinstance(doc['_id'], ObjectId):
                    doc['_id'] = str(doc['_id'])
                docs.append(doc)
            collections[name] = docs
    except Exception as e:
        collections = {}
    return render_template('admin/admin_dashboard.html', collections=collections)