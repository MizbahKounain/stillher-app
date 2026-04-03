import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
_BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Application configuration loaded by the app factory."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    SQLALCHEMY_DATABASE_URI = "sqlite:///../instance/database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("EMAIL_USER")
    MAIL_PASSWORD = os.environ.get("EMAIL_PASS")
    MAIL_DEFAULT_SENDER = os.environ.get("EMAIL_USER")
