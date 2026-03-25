from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import mongo, bcrypt
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.main_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email').lower()
        password = request.form.get('password')

        # Check if user already exists
        if mongo.db.users.find_one({'email': email}):
            flash('An account with this email already exists. Please log in.', 'warning')
            return redirect(url_for('auth.login'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Use email as the _id for simplicity and uniqueness
        mongo.db.users.insert_one({
            '_id': email,
            'email': email,
            'password': hashed_password,
            'is_admin': False # Default users are not admins
        })

        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.main_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email').lower()
        password = request.form.get('password')
        user_doc = mongo.db.users.find_one({'email': email})

        if user_doc and bcrypt.check_password_hash(user_doc['password'], password):
            user_obj = User(user_doc)
            login_user(user_obj, remember=True)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.main_dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))