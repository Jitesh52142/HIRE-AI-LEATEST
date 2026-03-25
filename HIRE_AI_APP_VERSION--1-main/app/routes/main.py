from flask import Blueprint, render_template, request, flash, redirect, url_for
from app import mongo
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('main/index.html')

@main_bp.route('/about')
def about():
    return render_template('main/about.html')

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        if not name or not email or not message:
            flash('All fields are required.', 'danger')
            return redirect(url_for('main.contact'))

        mongo.db.contact_queries.insert_one({
            'name': name,
            'email': email,
            'message': message,
            'timestamp': datetime.utcnow()
        })

        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('main.contact'))

    return render_template('main/contact.html')