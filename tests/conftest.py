"""
Pytest Fixtures
- Encoding صحيح
- Chrome Profile منفصل للاختبارات (مش بتاع المستخدم)
"""
import pytest
import os
import sys
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# ===== إصلاح Encoding =====
# نخلي Python يستخدم UTF-8 في الـ subprocess
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"

# نضيف BASE_DIR للـ sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.settings import USERNAME, PASSWORD
from utils.logger import logger


SELENIUM_HUB = os.getenv("SELENIUM_HUB", "http://localhost:4444")
USE_GRID = os.getenv("USE_SELENIUM_GRID", "false").lower() == "true"

# ===== Chrome Profile منفصل للاختبارات =====
# ملاحظة: مش بنستخدم نفس profile المتصفح العادي
# عشان نتجنب conflicts مع الجلسات المفتوحة
TEST_PROFILE_DIR = BASE_DIR / "chrome_profile_test"


@pytest.fixture(scope="function")
def driver():
    """Create WebDriver - local Chrome مع Profile منفصل"""
    logger.info("Starting Chrome...")

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=ar-EG")
    options.add_argument("--window-size=1920,1080")

    # نمنع استخدام الـ profile بتاع المستخدم
    options.add_argument("--incognito")  # ← وضع التخفي (مفيش profile)

    if USE_GRID:
        logger.info(f"Using Selenium Grid: {SELENIUM_HUB}")
        try:
            driver = webdriver.Remote(
                command_executor=SELENIUM_HUB,
                options=options,
            )
            logger.success(f"Connected to Grid. Session: {driver.session_id}")
        except Exception as e:
            logger.error(f"Grid connection failed: {e}")
            logger.warning("Falling back to local Chrome")
            driver = _create_local_driver(options)
    else:
        logger.info("Using local Chrome")
        driver = _create_local_driver(options)

    driver.set_page_load_timeout(60)
    driver.set_script_timeout(60)
    driver.implicitly_wait(3)

    yield driver

    logger.info("Closing browser...")
    try:
        driver.quit()
    except Exception:
        pass


def _create_local_driver(options):
    """Create local Chrome driver"""
    DRIVER_PATH = BASE_DIR / "drivers" / "chromedriver.exe"
    if DRIVER_PATH.exists():
        service = Service(str(DRIVER_PATH))
    else:
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())

    return webdriver.Chrome(service=service, options=options)


@pytest.fixture
def credentials():
    return {"username": USERNAME, "password": PASSWORD}