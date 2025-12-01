# Render Deployment Configuration
# Instructions: https://render.com

import os

# Environment configuration
class Config:
    # Use environment variable for database in production
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///foodshare.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    
    # File uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Update app config for production
def configure_app(app):
    """Configure app for production deployment"""
    config = Config()
    app.config.from_object(config)
    
    # Ensure upload directory exists
    upload_dir = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    return app