import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"

for d in (LOGS_DIR, REPORTS_DIR, SCREENSHOTS_DIR):
    d.mkdir(parents=True, exist_ok=True)

BASE_URL = os.getenv("BASE_URL", "https://test-site-nq.premiumasp.net")
LOGIN_URL = f"{BASE_URL}/Login"

USERNAME = os.getenv("LOGIN_USERNAME")
PASSWORD = os.getenv("LOGIN_PASSWORD")

DEFAULT_TIMEOUT = 20
SHORT_TIMEOUT = 5
LONG_TIMEOUT = 60
