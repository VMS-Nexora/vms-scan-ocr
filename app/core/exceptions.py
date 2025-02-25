from flask import jsonify
from werkzeug.exceptions import HTTPException

class APIError(Exception):
    """Base class for API exceptions"""
    code = 500
    description = "An error occurred while processing your request"

    def __init__(self, description=None, code=None):
        if description:
            self.description = description
        if code:
            self.code = code
        super().__init__(self.description)

class InvalidFileError(APIError):
    code = 400
    description = "Invalid or missing file"

class ProcessingError(APIError):
    code = 500
    description = "Error processing the image"

class ModelNotLoadedError(APIError):
    code = 503
    description = "Required models could not be loaded"

def register_error_handlers(app):
    """Register error handlers with the Flask app"""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify({
            'error': error.description,
            'status_code': error.code
        })
        response.status_code = error.code
        return response
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        response = jsonify({
            'error': error.description,
            'status_code': error.code
        })
        response.status_code = error.code
        return response
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        response = jsonify({
            'error': "An unexpected error occurred",
            'status_code': 500
        })
        response.status_code = 500
        return response