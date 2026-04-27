# This file marks the app directory as a Python package
from flask import Flask
from dotenv import load_dotenv
import os
from .extensions import db, migrate, login_manager

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///whatsapp_campaign.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    with app.app_context():
        from app.routes import main
        from app.auth import auth

        app.register_blueprint(main)
        app.register_blueprint(auth)

    return app