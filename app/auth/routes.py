from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app.extensions import db #, limiter
import re
from urllib.parse import urlparse, urljoin
import logging

auth = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

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
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        try:
            user = User.query.filter_by(email=email).first()
            
            if user and check_password_hash(user.password, password):
                login_user(user, remember=remember)
                next_page = request.args.get('next')
                if next_page and is_safe_url(next_page):
                    return redirect(next_page)
                return redirect(url_for('main.dashboard'))
            
            flash('Invalid email or password.', 'error')
            logger.warning(f"Failed login attempt for email: {email}")
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash('An error occurred during login. Please try again.', 'error')

    return render_template('auth/login.html')

@auth.route('/signup', methods=['GET', 'POST'])
# @limiter.limit("3 per minute")
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')

        try:
            # Input validation
            if len(name) < 2:
                flash('Name must be at least 2 characters long.', 'error')
                return render_template('auth/signup.html')

            if not is_valid_email(email):
                flash('Please enter a valid email address.', 'error')
                return render_template('auth/signup.html')

            if not is_strong_password(password):
                flash('Password must be at least 8 characters long and contain uppercase, lowercase, and numbers.', 'error')
                return render_template('auth/signup.html')

            # Check if user already exists
            if User.query.filter_by(email=email).first():
                flash('Email address already registered.', 'error')
                return render_template('auth/signup.html')

            # Create new user
            new_user = User(
                name=name,
                email=email,
                password=generate_password_hash(password, method='pbkdf2:sha256')
            )
            
            db.session.add(new_user)
            db.session.commit()

            # Log in the new user
            login_user(new_user)
            flash('Account created successfully!', 'success')
            return redirect(url_for('main.dashboard'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Signup error: {str(e)}")
            flash('An error occurred during signup. Please try again.', 'error')

    return render_template('auth/signup.html')

@auth.route('/logout')
@login_required
def logout():
    try:
        logout_user()
        flash('You have been logged out.', 'info')
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        flash('An error occurred during logout.', 'error')
    
    return redirect(url_for('main.index')) 