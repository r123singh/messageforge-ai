from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from .extensions import db #, limiter
import re

auth = Blueprint('auth', __name__)

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_strong_password(password):
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    return True

@auth.route('/login', methods=['GET', 'POST'])
# @limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False

        if not email or not password:
            flash('Please provide both email and password.', 'error')
            return redirect(url_for('auth.login'))

        if not is_valid_email(email):
            flash('Please enter a valid email address.', 'error')
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid email or password.', 'error')
            current_app.logger.warning(f'Failed login attempt for email: {email}')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):  # Ensure next_page is relative
            return redirect(next_page)
        return redirect(url_for('main.dashboard'))

    return render_template('auth/login.html')

@auth.route('/signup', methods=['GET', 'POST'])
# @limiter.limit("3 per minute")
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip()
            name = request.form.get('name', '').strip()
            password = request.form.get('password', '')

            if not email or not name or not password:
                flash('All fields are required', 'error')
                return redirect(url_for('auth.signup'))

            if not is_valid_email(email):
                flash('Please enter a valid email address', 'error')
                return redirect(url_for('auth.signup'))

            if not is_strong_password(password):
                flash('Password must be at least 8 characters long and contain uppercase, lowercase, and numbers', 'error')
                return redirect(url_for('auth.signup'))

            if len(name) < 2:
                flash('Name must be at least 2 characters long', 'error')
                return redirect(url_for('auth.signup'))

            if User.query.filter_by(email=email).first():
                flash('Email address already exists', 'error')
                return redirect(url_for('auth.signup'))

            new_user = User(
                email=email.lower(),
                name=name
            )
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()

            flash('Successfully registered! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error during signup: {str(e)}')
            flash('An error occurred during registration. Please try again.', 'error')
            return redirect(url_for('auth.signup'))

    return render_template('auth/signup.html')

@auth.route('/logout')
@login_required
# @limiter.limit("3 per minute")
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('main.index')) 