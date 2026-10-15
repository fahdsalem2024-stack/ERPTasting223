"""
Selenium Opener — يفتح شاشة في المتصفح ويعرضها
يستخدم لتشغيل "فتح فقط" من الموقع
"""
import sys
import time
import threading
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


class SeleniumOpener:
    """يفتح شاشة في المتصفح ويوقف"""

    def __init__(self):
        self.driver = None
        self.lock = threading.Lock()
        self.last_opened = None

    def open_page(self, url_path, keep_open_seconds=30):
        """يفتح الشاشة ويستنى"""
        with self.lock:
            try:
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
                from selenium.webdriver.chrome.service import Service
                from config.settings import BASE_URL, USERNAME, PASSWORD

                # لو فيه متصفح مفتوح، اقفله
                if self.driver:
                    try:
                        self.driver.quit()
                    except Exception:
                        pass
                    self.driver = None

                # Chrome options
                options = Options()
                options.add_argument("--start-maximized")
                options.add_argument("--disable-notifications")
                options.add_argument("--disable-popup-blocking")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--lang=ar-EG")

                # ChromeDriver محلي
                driver_path = BASE_DIR / "drivers" / "chromedriver.exe"
                if driver_path.exists():
                    service = Service(str(driver_path))
                    self.driver = webdriver.Chrome(service=service, options=options)
                else:
                    self.driver = webdriver.Chrome(options=options)

                self.driver.set_page_load_timeout(60)

                # تسجيل دخول
                self.driver.get(f"{BASE_URL}/Login")
                time.sleep(2)

                try:
                    username_input = self.driver.find_element("id", "userName")
                    password_input = self.driver.find_element("id", "password")
                    login_btn = self.driver.find_element("css selector", "button.btn-login")

                    username_input.clear()
                    username_input.send_keys(USERNAME)
                    password_input.clear()
                    password_input.send_keys(PASSWORD)
                    login_btn.click()
                    time.sleep(5)
                except Exception as e:
                    print(f"[SeleniumOpener] Login warning: {e}")

                # روح للشاشة المطلوبة
                full_url = f"{BASE_URL}{url_path}" if not url_path.startswith("http") else url_path
                self.driver.get(full_url)
                time.sleep(2)

                self.last_opened = {
                    "url": full_url,
                    "opened_at": time.time(),
                    "keep_open": keep_open_seconds,
                }

                # جدول إغلاق تلقائي
                if keep_open_seconds > 0:
                    def auto_close():
                        time.sleep(keep_open_seconds)
                        with self.lock:
                            if self.driver:
                                try:
                                    self.driver.quit()
                                except Exception:
                                    pass
                                self.driver = None
                    threading.Thread(target=auto_close, daemon=True).start()

                return {"success": True, "url": full_url}

            except Exception as e:
                return {"success": False, "error": str(e)[:200]}

    def close(self):
        """يقفل المتصفح"""
        with self.lock:
            if self.driver:
                try:
                    self.driver.quit()
                except Exception:
                    pass
                self.driver = None
                return True
        return False

    def is_open(self):
        """هل فيه متصفح مفتوح؟"""
        with self.lock:
            return self.driver is not None


# Singleton
_opener = None


def get_opener():
    global _opener
    if _opener is None:
        _opener = SeleniumOpener()
    return _opener