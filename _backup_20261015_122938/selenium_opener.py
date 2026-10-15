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
        """
        يفتح الشاشة، يستنى التحميل، يتأكد من البيانات، وياخد Screenshot
        """
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

                login_ok = False
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
                    login_ok = True
                except Exception as e:
                    print(f"[SeleniumOpener] Login warning: {e}")

                # روح للشاشة المطلوبة
                full_url = f"{BASE_URL}{url_path}" if not url_path.startswith("http") else url_path
                self.driver.get(full_url)

                # ===== فحص البيانات =====
                check_result = self._check_page_data(full_url)

                self.last_opened = {
                    "url": full_url,
                    "opened_at": time.time(),
                    "keep_open": keep_open_seconds,
                    "check_result": check_result,
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

                return {
                    "success": True,
                    "url": full_url,
                    "login_ok": login_ok,
                    "check_result": check_result,
                }

            except Exception as e:
                return {"success": False, "error": str(e)[:200]}

    def _check_page_data(self, url):
        """
        يفحص الصفحة الحالية:
        - يستنى التحميل
        - يعدّ الصفوف في الجدول
        - يتأكد إن فيه بيانات
        - ياخد Screenshot
        """
        result = {
            "loaded": False,
            "has_table": False,
            "row_count": 0,
            "has_data": False,
            "has_add_button": False,
            "has_errors": False,
            "error_text": "",
            "first_row": "",
            "screenshot": "",
            "page_title": "",
        }

        try:
            # استنى التحميل
            time.sleep(3)

            # Preloader
            try:
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                from selenium.webdriver.common.by import By
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.invisibility_of_element_located((By.ID, "preloader"))
                    )
                except Exception:
                    pass
            except Exception:
                pass

            # عنوان الصفحة
            result["page_title"] = self.driver.title
            result["loaded"] = True

            # جدول
            try:
                tables = self.driver.find_elements("css selector", "table")
                result["has_table"] = len(tables) > 0
            except Exception:
                pass

            # صفوف
            try:
                rows = self.driver.find_elements("css selector", "table tbody tr")
                result["row_count"] = len(rows)
                result["has_data"] = len(rows) > 0
                if rows:
                    result["first_row"] = rows[0].text.strip()[:150]
            except Exception:
                pass

            # زر إضافة
            try:
                add_btns = self.driver.find_elements(
                    "css selector",
                    "a[href*='/AddEdit'], button.add-new, .btn-add, a.btn-primary"
                )
                visible = [b for b in add_btns if b.is_displayed()]
                result["has_add_button"] = len(visible) > 0
            except Exception:
                pass

            # أخطاء
            try:
                errors = self.driver.find_elements(
                    "css selector",
                    ".alert-danger, .error-message, .validation-summary-errors"
                )
                for e in errors:
                    if e.is_displayed() and e.text.strip():
                        result["has_errors"] = True
                        result["error_text"] = e.text.strip()[:200]
                        break
            except Exception:
                pass

            # Screenshot
            try:
                from datetime import datetime
                screenshots_dir = BASE_DIR / "reports" / "screenshots"
                screenshots_dir.mkdir(parents=True, exist_ok=True)
                filename = f"opened_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                filepath = screenshots_dir / filename
                self.driver.save_screenshot(str(filepath))
                result["screenshot"] = filename
            except Exception as e:
                print(f"[Screenshot error] {e}")

        except Exception as e:
            result["error_text"] = str(e)[:200]

        return result

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