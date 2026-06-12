from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import mongo, bcrypt
from app.models.user import User
import re

auth_bp = Blueprint('auth', __name__)


def _valid_email(email):
    return re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email) is not None

def _valid_password(password):
    return len(password) >= 8 and bool(re.search(r'\d', password))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.main_dashboard'))

    if request.method == 'POST':
        full_name    = request.form.get('full_name', '').strip()
        company_name = request.form.get('company_name', '').strip()
        job_title    = request.form.get('job_title', '').strip()
        phone        = request.form.get('phone', '').strip()
        email        = request.form.get('email', '').strip().lower()
        password     = request.form.get('password', '')
        confirm_pwd  = request.form.get('confirm_password', '')

        # ---- Server-side validation ----
        errors = []

        if not full_name or len(full_name) < 2:
            errors.append('Full name must be at least 2 characters.')
        if not company_name or len(company_name) < 2:
            errors.append('Company name is required.')
        if not job_title:
            errors.append('Job title is required.')
        if not email or not _valid_email(email):
            errors.append('Please enter a valid email address.')
        if not password or not _valid_password(password):
            errors.append('Password must be at least 8 characters and include a number.')
        if password != confirm_pwd:
            errors.append('Passwords do not match.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('auth/register.html',
                                   form_data=request.form)

        # ---- Check duplicate email ----
        if mongo.db.users.find_one({'email': email}):
            flash('An account with this email already exists.', 'warning')
            return render_template('auth/register.html',
                                   form_data=request.form)

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        mongo.db.users.insert_one({
            '_id':          email,
            'email':        email,
            'password':     hashed_password,
            'full_name':    full_name,
            'company_name': company_name,
            'job_title':    job_title,
            'phone':        phone,
            'is_admin':     False,
        })

        flash(f'Welcome to Hire AI, {full_name.split()[0]}! Your account is ready.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form_data={})


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.main_dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not email or not password:
            flash('Please enter your email and password.', 'danger')
            return render_template('auth/login.html', form_email=email)

        user_doc = mongo.db.users.find_one({'email': email})

        if user_doc and user_doc.get('password') and \
                bcrypt.check_password_hash(user_doc['password'], password):
            user_obj = User(user_doc)
            login_user(user_obj, remember=remember)
            flash(f'Welcome back{", " + user_doc.get("full_name","").split()[0] if user_doc.get("full_name") else ""}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.main_dashboard'))

        flash('Incorrect email or password. Please try again.', 'danger')

    return render_template('auth/login.html', form_email='')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))
