"""
Config Settings - Reads from active test site profile, falls back to .env
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _read_active_profile():
    try:
        f = BASE_DIR / "config" / "test_sites.json"
        if not f.exists():
            return None
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        active_id = data.get("active_profile")
        if not active_id:
            return None
        for p in data.get("profiles", []):
            if p.get("id") == active_id:
                return p
    except Exception:
        return None
    return None


def _get(key, env_key, default=""):
    profile = _read_active_profile()
    if profile:
        value = profile.get(key)
        if value:
            return value
    return os.getenv(env_key, default)


# ==================== URLs ====================
BASE_URL = _get("base_url", "BASE_URL", "https://test-site-nq.premiumasp.net")

# ==================== Credentials ====================
USERNAME = _get("username", "LOGIN_USERNAME", "erpadmin")
PASSWORD = _get("password", "LOGIN_PASSWORD", "")

# ==================== Paths ====================
DRIVERS_DIR = BASE_DIR / "drivers"
REPORTS_DIR = BASE_DIR / "reports"
RESULTS_DIR = REPORTS_DIR / "results"
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
LOGS_DIR = BASE_DIR / "logs"


# ==================== Timeouts ====================
DEFAULT_TIMEOUT = 20
SHORT_TIMEOUT = 5
LONG_TIMEOUT = 60
IMPLICIT_WAIT = 3
PAGE_LOAD_TIMEOUT = 60

# ==================== Screenshots ====================
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# ==================== Other Config ====================
HEADLESS = False
BROWSER = "chrome"


# ==================== URLs ====================
LOGIN_URL = BASE_URL + "/Login"
SALES_INVOICE_LIST_URL = BASE_URL + "/SalesInvoice"
SALES_INVOICE_ADD_URL = BASE_URL + "/SalesInvoice/AddEdit"

# ==================== Timeouts ====================
DEFAULT_TIMEOUT = 20
SHORT_TIMEOUT = 5
LONG_TIMEOUT = 60
IMPLICIT_WAIT = 3
PAGE_LOAD_TIMEOUT = 60

# ==================== Directories ====================
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
LOGS_DIR = BASE_DIR / "logs"
DRIVERS_DIR = BASE_DIR / "drivers"

# إنشاء المجلدات لو مش موجودة
for _d in [REPORTS_DIR, RESULTS_DIR, SCREENSHOTS_DIR, LOGS_DIR, DRIVERS_DIR]:
    try:
        _d.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

# ==================== Browser ====================
BROWSER = "chrome"
HEADLESS = False
