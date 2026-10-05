import pytest
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from config.settings import USERNAME, PASSWORD
from utils.logger import logger


DRIVER_PATH = Path(__file__).resolve().parent.parent / "drivers" / "chromedriver.exe"


@pytest.fixture(scope="function")
def driver():
    logger.info("Starting Chrome...")
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-images")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("--lang=ar-EG")
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.page_load_strategy = "eager"

    if DRIVER_PATH.exists():
        service = Service(str(DRIVER_PATH))
    else:
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(60)
    driver.set_script_timeout(60)
    driver.implicitly_wait(3)

    yield driver

    logger.info("Closing browser...")
    try:
        driver.quit()
    except Exception:
        pass


@pytest.fixture
def credentials():
    return {"username": USERNAME, "password": PASSWORD}
