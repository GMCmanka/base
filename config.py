# config.py
import os

class Config:
    # Database connection (edit if needed)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:admin123@127.0.0.1/admin" # Default value
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False # To suppress a warning
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
    # Other configurations can be added here
    DEBUG = True # Set to False in production
    TESTING = False # Set to True in testing environments