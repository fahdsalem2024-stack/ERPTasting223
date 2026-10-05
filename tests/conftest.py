import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from pathlib import Path
from config.settings import USERNAME, PASSWORD
from utils.logger import logger


SELENIUM_HUB = os.getenv("SELENIUM_HUB", "http://localhost:4444")
USE_GRID = os.getenv("USE_SELENIUM_GRID", "true").lower() == "true"


@pytest.fixture(scope="function")
def driver():
    """Create WebDriver - Grid or Local"""
    logger.info("Starting Chrome...")

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=ar-EG")
    options.add_argument("--window-size=1920,1080")

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
    DRIVER_PATH = Path(__file__).resolve().parent.parent / "drivers" / "chromedriver.exe"
    if DRIVER_PATH.exists():
        service = Service(str(DRIVER_PATH))
    else:
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


@pytest.fixture
def credentials():
    return {"username": USERNAME, "password": PASSWORD}
