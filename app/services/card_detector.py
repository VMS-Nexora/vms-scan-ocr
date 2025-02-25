import os
import numpy as np
import tensorflow as tf
from app.core.config import settings
from app.core.exceptions import ModelNotLoadedError, ProcessingError

class CardDetector:
    """Service to detect and extract ID card from images"""
    
    def __init__(self):
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the ID card detection model"""
        try:
            model_path = settings.ID_DETECTOR_MODEL
            if not os.path.exists(model_path):
                raise ModelNotLoadedError(f"ID detector model not found at {model_path}")
            
            self.model = tf.keras.models.load_model(model_path)
        except Exception as e:
            raise ModelNotLoadedError(f"Failed to load ID detector model: {str(e)}")
    
    def detect(self, image):
        """
        Detect and extract ID card from image
        
        Args:
            image: numpy array of the image
            
        Returns:
            Cropped image containing only the ID card
        """
        try:
            if self.model is None:
                self.load_model()
            
            # Preprocess image for model input
            img_rgb = image if len(image.shape) == 3 else np.stack((image,)*3, axis=-1)
            img_resized = tf.image.resize(img_rgb, (224, 224))
            img_normalized = img_resized / 255.0
            img_batch = tf.expand_dims(img_normalized, axis=0)
            
            # Get predictions (bounding box coordinates)
            predictions = self.model.predict(img_batch)
            
            # Extract coordinates (normalized)
            box = predictions[0]
            
            # Check if confidence is high enough
            confidence = predictions[1][0][0] if len(predictions) > 1 else 1.0
            if confidence < settings.DETECTION_CONFIDENCE_THRESHOLD:
                # If confidence is low, return original image
                return image
            
            # Convert normalized coordinates to pixel coordinates
            h, w = image.shape[:2]
            x1, y1, x2, y2 = [
                int(box[0] * w),  # x1
                int(box[1] * h),  # y1
                int(box[2] * w),  # x2
                int(box[3] * h)   # y2
            ]
            
            # Ensure valid coordinates
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            
            # Check if the detected region is valid
            if x2 <= x1 or y2 <= y1 or (x2 - x1) * (y2 - y1) < 0.1 * w * h:
                # If detected region is too small, return original image
                return image
            
            # Extract card region
            card_image = image[y1:y2, x1:x2]
            
            return card_image
            
        except Exception as e:
            raise ProcessingError(f"Error detecting ID card: {str(e)}")