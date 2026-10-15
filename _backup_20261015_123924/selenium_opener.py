"""
Selenium Opener — Simple
1. Login (باستخدام LoginPage الموجود)
2. Open page
3. Wait 5 seconds
4. Close browser
"""
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def open_page_simple(url_path, wait_seconds=5):
    """
    يفتح شاشة في المتصفح:
    1) يسجّل دخول (باستخدام LoginPage)
    2) يفتح الشاشة
    3) يستنى wait_seconds
    4) يقفل المتصفح
    """
    result = {
        "success": False,
        "url": "",
        "login_ok": False,
        "waited_seconds": 0,
        "error": "",
        "screenshot": "",
        "current_url": "",
    }

    driver = None
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from config.settings import BASE_URL, USERNAME, PASSWORD
        from pages.login_page import LoginPage

        # ===== Chrome Options =====
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--lang=ar-EG")

        # ===== ChromeDriver محلي =====
        driver_path = BASE_DIR / "drivers" / "chromedriver.exe"
        if driver_path.exists():
            service = Service(str(driver_path))
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)

        driver.set_page_load_timeout(60)

        # ===== 1) تسجيل الدخول باستخدام LoginPage =====
        try:
            login_page = LoginPage(driver)
            login_page.load()
            login_page.login(USERNAME, PASSWORD)

            # استنى التحويل
            time.sleep(3)

            current = driver.current_url
            # لو مش في صفحة Login → نجح
            if "/Login" not in current:
                result["login_ok"] = True
            else:
                result["error"] = f"Login failed — still on: {current}"
                return result

        except Exception as e:
            result["error"] = f"Login: {str(e)[:200]}"
            return result

        # ===== 2) فتح الشاشة =====
        full_url = f"{BASE_URL}{url_path}" if not url_path.startswith("http") else url_path
        result["url"] = full_url
        driver.get(full_url)

        # ===== 3) استنى 5 ثواني =====
        time.sleep(wait_seconds)
        result["waited_seconds"] = wait_seconds
        result["current_url"] = driver.current_url

        # ===== 4) صورة =====
        try:
            from datetime import datetime
            screenshots_dir = BASE_DIR / "reports" / "screenshots"
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            filename = f"opened_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(str(screenshots_dir / filename))
            result["screenshot"] = filename
        except Exception:
            pass

        result["success"] = True

    except Exception as e:
        result["error"] = str(e)[:200]

    finally:
        # ===== 5) اقفل المتصفح =====
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

    return result


def get_opener():
    """للتوافق مع الكود القديم"""
    return None