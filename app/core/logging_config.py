import logging
import os
from logging.handlers import RotatingFileHandler
from flask import has_request_context, request
import time

class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.method = request.method
        else:
            record.url = None
            record.remote_addr = None
            record.method = None
        return super().format(record)

def configure_logging(app):
    """Configure logging for the application"""
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Configure rotating file handler
    file_handler = RotatingFileHandler(
        os.path.join(logs_dir, 'id_scanner.log'),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    
    # Configure formatters
    file_formatter = RequestFormatter(
        '%(asctime)s %(levelname)s: [%(method)s] %(url)s (%(remote_addr)s) - %(message)s [in %(pathname)s:%(lineno)d]'
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.INFO)
    
    # Add handlers to the app logger
    app.logger.addHandler(file_handler)
    
    # Set log level based on environment
    if app.config['DEBUG']:
        app.logger.setLevel(logging.DEBUG)
    else:
        app.logger.setLevel(logging.INFO)
    
    # Add request timing middleware
    @app.before_request
    def before_request():
        request.start_time = time.time()

    @app.after_request
    def after_request(response):
        if hasattr(request, 'start_time'):
            elapsed = time.time() - request.start_time
            app.logger.info(f"Request processed in {elapsed:.6f} seconds")
        return response