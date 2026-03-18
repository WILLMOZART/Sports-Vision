import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DATABASE = os.getenv("DATABASE", "data/sportvision.db")
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))
    ALLOWED_EXTENSIONS = {"csv"}

    # API settings
    API_KEY = os.getenv("API_KEY", "sportvision-api-key-2024")
    API_ENABLED = os.getenv("API_ENABLED", "true").lower() == "true"

    # Pagination
    ITEMS_PER_PAGE = int(os.getenv("ITEMS_PER_PAGE", 20))

    # ML Model settings
    MIN_MATCHES_FOR_PREDICTION = int(os.getenv("MIN_MATCHES_FOR_PREDICTION", 10))
    MODEL_PATH = os.getenv("MODEL_PATH", "data/model.pkl")
    SCALER_PATH = os.getenv("SCALER_PATH", "data/scaler.pkl")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    DATABASE = "data/test_sportvision.db"


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
