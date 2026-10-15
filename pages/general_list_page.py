"""
General List Page — لكل شاشات القوائم في الحسابات العامة
Smoke Test: تفتح الشاشة + تستنى الجدول + تتأكد إن فيه بيانات
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage
from utils.logger import logger
from config.settings import BASE_URL
import time


class GeneralListPage(BasePage):
    """صفحة قائمة عامة — تفتح شاشة وتعرض البيانات"""

    # Selectors
    TABLE_ROWS = (By.CSS_SELECTOR, "table tbody tr")
    TABLE_ANY = (By.CSS_SELECTOR, "table")
    ADD_BUTTON = (By.CSS_SELECTOR, "a[href*='/AddEdit'], button.add-new, .btn-add")
    SEARCH_BOX = (By.CSS_SELECTOR, "input[type='search'], input.search-input")
    PAGINATION = (By.CSS_SELECTOR, ".pagination, .pager")
    NO_DATA_MSG = (By.CSS_SELECTOR, ".no-data, .empty-state, .text-center")
    ERROR_MSG = (By.CSS_SELECTOR, ".alert-danger, .error-message, .validation-summary-errors")

    def __init__(self, driver, url_path):
        super().__init__(driver)
        self.url_path = url_path
        self.full_url = f"{BASE_URL}{url_path}" if not url_path.startswith("http") else url_path

    # ========== Navigation ==========
    def open_page(self):
        """يفتح الشاشة"""
        logger.info(f"فتح: {self.full_url}")
        self.driver.get(self.full_url)
        self.wait_for_preloader(timeout=20)
        time.sleep(2)
        return self

    def is_loaded(self, timeout=15):
        """يتأكد إن الصفحة اتحملت (URL صح)"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: self.url_path.split("?")[0] in d.current_url or d.current_url.endswith(self.url_path)
            )
            logger.success(f"✅ الصفحة اتحملت: {self.driver.current_url}")
            return True
        except TimeoutException:
            logger.error(f"❌ الصفحة مش اتحملت: {self.driver.current_url}")
            return False

    def has_table(self, timeout=10):
        """يتأكد إن فيه جدول"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self.TABLE_ANY)
            )
            logger.success("✅ الجدول موجود")
            return True
        except TimeoutException:
            logger.warning("⚠️ مفيش جدول")
            return False

    def get_row_count(self):
        """يرجع عدد الصفوف"""
        try:
            rows = self.driver.find_elements(*self.TABLE_ROWS)
            return len(rows)
        except Exception:
            return 0

    def has_data(self):
        """يتأكد إن فيه بيانات"""
        count = self.get_row_count()
        if count > 0:
            logger.success(f"✅ فيه {count} صف في الجدول")
            return True
        logger.warning("⚠️ الجدول فاضي")
        return False

    def get_first_row_text(self):
        """يرجع نص أول صف"""
        try:
            rows = self.driver.find_elements(*self.TABLE_ROWS)
            if rows:
                return rows[0].text.strip()[:200]
        except Exception:
            pass
        return ""

    def has_add_button(self):
        """يتأكد إن فيه زر إضافة"""
        try:
            btns = self.driver.find_elements(*self.ADD_BUTTON)
            visible = [b for b in btns if b.is_displayed()]
            if visible:
                logger.success(f"✅ فيه {len(visible)} زر إضافة")
                return True
            logger.warning("⚠️ مفيش زر إضافة")
            return False
        except Exception:
            return False

    def has_errors(self):
        """يتأكد إن مفيش أخطاء"""
        try:
            for el in self.driver.find_elements(*self.ERROR_MSG):
                if el.is_displayed() and el.text.strip():
                    logger.error(f"❌ خطأ: {el.text.strip()[:150]}")
                    return True
            return False
        except Exception:
            return False

    def take_page_screenshot(self, name):
        """صورة للشاشة"""
        self.take_screenshot(f"ga_{name}")

    # ========== Smoke Test ==========
    def run_smoke_test(self, module_key, module_info):
        """
        اختبار Smoke كامل:
        1) يفتح الشاشة
        2) يستنى التحميل
        3) يتأكد إن الجدول موجود
        4) يتأكد إن فيه بيانات
        5) يتأكد إن مفيش errors
        يرجع dict فيه النتيجة
        """
        result = {
            "key": module_key,
            "name_ar": module_info["name_ar"],
            "name_en": module_info["name_en"],
            "url": module_info["url"],
            "loaded": False,
            "has_table": False,
            "row_count": 0,
            "has_data": False,
            "has_add_button": False,
            "has_errors": False,
            "first_row": "",
            "success": False,
        }

        try:
            logger.info(f"{'=' * 60}")
            logger.info(f"🧪 Smoke Test: {module_info['name_ar']} ({module_info['name_en']})")
            logger.info(f"{'=' * 60}")

            # 1) فتح
            self.open_page()

            # 2) تحميل
            result["loaded"] = self.is_loaded()

            # 3) جدول
            result["has_table"] = self.has_table()

            # 4) بيانات
            result["row_count"] = self.get_row_count()
            result["has_data"] = result["row_count"] > 0
            result["first_row"] = self.get_first_row_text()

            # 5) زر إضافة
            result["has_add_button"] = self.has_add_button()

            # 6) أخطاء
            result["has_errors"] = self.has_errors()

            # 7) صورة
            self.take_page_screenshot(module_key)

            # 8) النجاح = الصفحة اتحملت + الجدول موجود + مفيش أخطاء
            result["success"] = (
                result["loaded"]
                and result["has_table"]
                and not result["has_errors"]
            )

            if result["success"]:
                logger.success(f"✅ {module_info['name_ar']} — نجح ({result['row_count']} صف)")
            else:
                logger.warning(f"⚠️ {module_info['name_ar']} — فشل")

        except Exception as e:
            logger.error(f"❌ {module_info['name_ar']}: {str(e)[:200]}")

        return result