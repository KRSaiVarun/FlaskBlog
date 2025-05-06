import os
import logging
import datetime
import markdown
from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.security import generate_password_hash

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy and Flask
db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

# Configure app
app.config.from_object('config.Config')
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,  # Test connections before using them
    'pool_recycle': 300,    # Recycle connections every 5 minutes
    'pool_timeout': 30,     # Connection timeout after 30 seconds
    'pool_size': 10         # Maximum of 10 connections in the pool
}

# Initialize the app with the extension
db.init_app(app)

# Register Markdown filter
@app.template_filter('markdown')
def render_markdown(text):
    return markdown.markdown(text)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Import models (must be after db initialization)
from models import User, Post

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except ValueError:
        # Handle old session cookies during migration
        return None

# Create tables and seed data
with app.app_context():
    db.create_all()
    
    # Check if admin user exists, if not create one
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('password'),
            created_at=datetime.datetime.utcnow()
        )
        db.session.add(admin_user)
        db.session.commit()
        
        # Add a sample blog post
        welcome_post = Post(
            title='Welcome to FlaskBlog',
            content='# Welcome to FlaskBlog\n\nThis is a sample blog post created with FlaskBlog. You can write your posts using Markdown syntax.\n\n## Features\n\n- User authentication\n- Create, edit, and delete blog posts\n- Markdown support\n- Responsive design\n\nEnjoy blogging!',
            author_id=admin_user.id,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow()
        )
        db.session.add(welcome_post)
        db.session.commit()
        
        app.logger.info("Initialized PostgreSQL database with demo data")
    else:
        app.logger.info("Database already contains data, skipping initialization")

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('403.html'), 403

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# Import routes - must be at the end to avoid circular imports
import routes

# This is required by gunicorn
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
