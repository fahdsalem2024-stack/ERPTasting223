"""
Web Config
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "erp-automation-secret-key-2026")
    BABEL_DEFAULT_LOCALE = "ar"
    BABEL_DEFAULT_TIMEZONE = "Africa/Cairo"
    LANGUAGES = ["ar", "en"]
    BASE_DIR = BASE_DIR
    RESULTS_DIR = BASE_DIR / "reports" / "results"
    SCREENSHOTS_DIR = BASE_DIR / "reports" / "screenshots"
    LOGS_DIR = BASE_DIR / "logs"
    SLACK_CONFIG = BASE_DIR / "config" / "slack_config.json"
    EMAIL_CONFIG = BASE_DIR / "config" / "email_config.json"
