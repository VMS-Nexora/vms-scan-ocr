import os
from flask import Flask
from app.core.config import Config
from app.core.logging_config import configure_logging
from app.api.routes import api_bp

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    configure_logging(app)
    
    # Create required directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    return app