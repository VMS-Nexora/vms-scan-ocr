from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import time
import uuid
from app.core.exceptions import InvalidFileError, ProcessingError
from app.services.card_detector import CardDetector
from app.services.image_processor import ImageProcessor
from app.services.ocr_engine import OCREngine
from app.services.language_detector import LanguageDetector
from app.services.info_extractor import InfoExtractor
from app.models.schemas import ScanResponse
from app.api.validators import validate_file

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Initialize services
card_detector = CardDetector()
image_processor = ImageProcessor()
ocr_engine = OCREngine()
language_detector = LanguageDetector()
info_extractor = InfoExtractor()

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'OK',
        'version': '1.0.0',
        'timestamp': time.time()
    })

@api_bp.route('/scan', methods=['POST'])
def scan_id_card():
    """Scan ID card and extract information"""
    try:
        # Validate file
        file = validate_file(request)
        
        # Generate unique ID for tracking
        scan_id = str(uuid.uuid4())
        
        # Save file for auditing/debugging
        filename = secure_filename(f"{scan_id}_{file.filename}")
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Read image
        file_bytes = file.read()
        file.seek(0)  # Rewind file pointer for saving
        file.save(file_path)
        
        # Process image
        current_app.logger.info(f"Processing image {scan_id}")
        image = image_processor.load_image(file_bytes)
        
        # Detect ID card
        card_image = card_detector.detect(image)
        
        # Get language preference from request, default to 'auto'
        language_pref = request.form.get('language', 'auto')
        
        # Extract text with OCR
        processed_image = image_processor.preprocess(card_image)
        extracted_text = ocr_engine.extract_text(processed_image, language_pref)
        
        # Detect language if auto
        if language_pref == 'auto':
            detected_language = language_detector.detect(extracted_text)
        else:
            detected_language = language_pref
        
        # Extract structured information
        info = info_extractor.extract(extracted_text, detected_language)
        
        # Add metadata
        response_data = {
            'scan_id': scan_id,
            'detected_language': detected_language,
            'raw_text': extracted_text,
            **info
        }
        
        # Create validated response schema
        response = ScanResponse(**response_data)
        
        current_app.logger.info(f"Successfully processed image {scan_id}")
        return jsonify(response.dict())
        
    except InvalidFileError as e:
        current_app.logger.warning(f"Invalid file: {str(e)}")
        return jsonify({'error': str(e)}), e.code
        
    except ProcessingError as e:
        current_app.logger.error(f"Processing error: {str(e)}")
        return jsonify({'error': str(e)}), e.code
        
    except Exception as e:
        current_app.logger.exception(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500