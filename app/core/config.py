import os
from typing import Dict, Any, List, Union
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Application settings"""
    # Flask settings
    SECRET_KEY: str = Field(default=os.urandom(24).hex(), env="SECRET_KEY")
    DEBUG: bool = Field(default=False, env="DEBUG")
    TESTING: bool = Field(default=False, env="TESTING")
    
    # Application settings
    PROJECT_NAME: str = "ID Card Scanner Service"
    API_V1_STR: str = "/api/v1"
    
    # File upload settings
    UPLOAD_FOLDER: str = Field(default="data/uploads", env="UPLOAD_FOLDER")
    MAX_CONTENT_LENGTH: int = Field(default=16 * 1024 * 1024, env="MAX_CONTENT_LENGTH")  # 16MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png"]
    
    # Model paths
    MODELS_FOLDER: str = Field(default="data/models", env="MODELS_FOLDER")
    ID_DETECTOR_MODEL: str = Field(default="data/models/id_detector.h5", env="ID_DETECTOR_MODEL")
    NER_EN_MODEL: str = Field(default="data/models/ner_en", env="NER_EN_MODEL")
    NER_VI_MODEL: str = Field(default="data/models/ner_vi", env="NER_VI_MODEL")
    
    # Service settings
    OCR_TIMEOUT: int = Field(default=30, env="OCR_TIMEOUT")  # Seconds
    DETECTION_CONFIDENCE_THRESHOLD: float = Field(default=0.7, env="DETECTION_CONFIDENCE_THRESHOLD")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

class Config:
    """Flask configuration"""
    SECRET_KEY = settings.SECRET_KEY
    DEBUG = settings.DEBUG
    TESTING = settings.TESTING
    UPLOAD_FOLDER = settings.UPLOAD_FOLDER
    MAX_CONTENT_LENGTH = settings.MAX_CONTENT_LENGTH

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False