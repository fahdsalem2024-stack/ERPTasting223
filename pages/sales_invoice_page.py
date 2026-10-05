"""
Sales Invoice Page Object
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage
from utils.select2_helper import Select2Helper
from utils.logger import logger
from config.settings import BASE_URL
from config.invoice_data import InvoiceDefaults
import time


class SalesInvoicePage(BasePage):
    LIST_URL = f"{BASE_URL}/SalesInvoice"
    ADD_URL = f"{BASE_URL}/SalesInvoice/AddEdit"

    ADD_NEW_BUTTON = (By.CSS_SELECTOR, "a[href='/SalesInvoice/AddEdit']")
    CUSTOMER_SELECT2 = "VendorOrCustomerId"

    ITEM_ADD_PLUS_BUTTON = (By.CSS_SELECTOR, "span.Add-Button")
    ANY_MODAL = (By.CSS_SELECTOR, ".modal.show, .modal.in, .modal[style*='display: block']")
    SEARCH_BTN_IN_MODAL = (By.CSS_SELECTOR, ".modal.show #submitSearch, .modal.in #submitSearch")
    ITEM_ROW_ANY = (By.CSS_SELECTOR, ".modal.show tbody tr, .modal.in tbody tr")

    COMM_REG = (By.ID, "CommercialRegistrationNumber")
    VAT_NUMBER = (By.ID, "CashCustomerVATNumber")
    POSTAL_CODE = (By.ID, "PostalCode")
    BUILDING_NUMBER = (By.ID, "BuildingNumber")

    AUTO_VOUCHER = (By.ID, "AutoGenerateStockReceiptVoucher")

    SAVE_BUTTON = (By.CSS_SELECTOR, "button#save")
    SWAL_POPUP = (By.CSS_SELECTOR, ".swal2-popup")
    SWAL_CONFIRM = (By.CSS_SELECTOR, "button.swal2-confirm")

    def __init__(self, driver):
        super().__init__(driver)
        self.s2 = Select2Helper(driver)

    # ========== Navigation ==========
    def open_list(self):
        self.open(self.LIST_URL)
        self.wait_for_preloader()
        time.sleep(1)

    def click_add_new(self):
        logger.info("اضغط إضافة جديد")
        self.wait_for_preloader(timeout=20)
        time.sleep(0.5)
        self.click(self.ADD_NEW_BUTTON, "زر إضافة جديد")
        self.wait_for_preloader(timeout=20)
        time.sleep(1)

    def is_on_add_page(self):
        return "/AddEdit" in self.driver.current_url

    # ========== Customer ==========
    def select_customer(self, customer_name: str = None):
        if customer_name:
            self.s2.select_by_id(self.CUSTOMER_SELECT2, customer_name)
            return customer_name
        else:
            return self.s2.select_first_real_option(self.CUSTOMER_SELECT2)

    # ========== Items ==========
    def click_plus_button(self):
        logger.info("اضغط على زر ➕")
        spans = self.driver.find_elements(*self.ITEM_ADD_PLUS_BUTTON)
        if not spans:
            raise Exception("مفيش span.Add-Button")
        first_span = spans[0]
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", first_span)
        first_span.click()
        time.sleep(1)

    def wait_for_item_modal(self, timeout=20):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self.ANY_MODAL)
            )
            time.sleep(0.5)
            return True
        except TimeoutException:
            return False

    def click_search_btn_in_modal(self):
        try:
            btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(self.SEARCH_BTN_IN_MODAL)
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            btn.click()
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located(self.ITEM_ROW_ANY)
                )
            except TimeoutException:
                pass
            return True
        except TimeoutException:
            return False

    def wait_for_items_results(self, timeout=20):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self.ITEM_ROW_ANY)
            )
            return True
        except TimeoutException:
            return False

    def click_add_item_by_name(self, item_name: str):
        logger.info(f"إضافة الصنف: {item_name}")
        rows = self.driver.find_elements(*self.ITEM_ROW_ANY)
        target_row = None
        for row in rows:
            try:
                if item_name in row.text:
                    target_row = row
                    break
            except Exception:
                continue
        if not target_row:
            raise Exception(f"مفيش صنف: {item_name}")
        add_btn = target_row.find_element(
            By.CSS_SELECTOR, "button[onclick='chooseItem(this)']"
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", add_btn)
        add_btn.click()
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.float.price"))
            )
        except TimeoutException:
            pass
        logger.success(f"✅ تم إضافة: {item_name}")
        return True

    def set_price_for_last_item(self, price):
        logger.info(f"كتابة السعر: {price}")
        try:
            inputs = WebDriverWait(self.driver, 10).until(
                lambda d: d.find_elements(By.CSS_SELECTOR, "input.float.price")
            )
            if not inputs:
                return False
            last_input = inputs[-1]
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", last_input
            )
            time.sleep(0.3)
            self.driver.execute_script("""
                var el = arguments[0];
                el.focus();
                el.click();
            """, last_input)
            time.sleep(0.3)
            self.driver.execute_script("""
                var el = arguments[0];
                el.value = '';
                el.value = arguments[1];
                el.dispatchEvent(new Event('input', {bubbles: true}));
                el.dispatchEvent(new Event('change', {bubbles: true}));
                el.dispatchEvent(new Event('keyup', {bubbles: true}));
                el.dispatchEvent(new Event('blur', {bubbles: true}));
            """, last_input, str(price))
            time.sleep(1.5)
            logger.success(f"✅ تم كتابة السعر: {price}")
            return True
        except Exception as e:
            logger.error(f"مشكلة: {str(e)[:150]}")
            return False

    # ========== Text Fields ==========
    def _fill_text_field(self, locator, value, field_name):
        try:
            el = self.driver.find_element(*locator)
            current = el.get_attribute("value") or ""
            if current.strip():
                logger.info(f"⏭️ {field_name} متملي: {current}")
                return True
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            el.click()
            self.driver.execute_script("""
                var el = arguments[0];
                el.value = '';
                el.value = arguments[1];
                el.dispatchEvent(new Event('input', {bubbles: true}));
                el.dispatchEvent(new Event('change', {bubbles: true}));
                el.dispatchEvent(new Event('blur', {bubbles: true}));
            """, el, value)
            logger.info(f"✅ {field_name}: {value}")
            return True
        except Exception as e:
            logger.warning(f"⚠️ مشكلة {field_name}: {str(e)[:100]}")
            return False

    def fill_required_text_fields(self):
        logger.info("ملء الحقول النصية الإجبارية")
        self.wait_for_preloader()
        self._fill_text_field(self.COMM_REG, InvoiceDefaults.COMMERCIAL_REGISTRATION, "السجل التجاري")
        self._fill_text_field(self.VAT_NUMBER, InvoiceDefaults.VAT_NUMBER, "الرقم الضريبي")
        self._fill_text_field(self.POSTAL_CODE, InvoiceDefaults.POSTAL_CODE, "الرقم البريدي")
        self._fill_text_field(self.BUILDING_NUMBER, InvoiceDefaults.BUILDING_NUMBER, "رقم المبنى")
        logger.success("✅ تم ملء الحقول النصية")

    # ========== Select2 ==========
    def _select2_has_value(self, select_id):
        try:
            container = self.driver.find_element(By.ID, f"select2-{select_id}-container")
            text = container.text.strip()
            if text and text not in ["--اختر--", "-اختر-", "اختر", ""]:
                return text
        except Exception:
            pass
        return None

    def _fill_select2_field(self, select_id, value, name):
        try:
            current = self._select2_has_value(select_id)
            if current:
                logger.info(f"⏭️ {name} متملي: {current}")
                return True

            if value:
                logger.info(f"محاولة البحث عن '{value}' في {name}")
                if self.s2.select_by_id(select_id, value):
                    return True

            logger.info(f"محاولة force_select في {name}")
            if self.s2.force_select_value(select_id, value or ""):
                time.sleep(0.3)
                current = self._select2_has_value(select_id)
                if current:
                    logger.success(f"✅ {name} = {current}")
                    return True

            logger.info(f"محاولة select_first_real_option في {name}")
            result = self.s2.select_first_real_option(select_id)
            if result and not self.s2._is_placeholder(result):
                return True

            logger.warning(f"⚠️ فشل {name}")
            return False
        except Exception as e:
            logger.warning(f"⚠️ مشكلة في {name}: {str(e)[:120]}")
            return False

    def _force_reload_cost_center(self):
        logger.info("إعادة اختيار مركز التكلفة")
        try:
            if self.s2.force_select_value("CostCenterId", ""):
                return True
            container = self.driver.find_element(By.ID, "select2-CostCenterId-container")
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", container)
            container.click()
            time.sleep(1)
            options = self.driver.find_elements(
                By.CSS_SELECTOR,
                "span.select2-container--open li.select2-results__option"
            )
            for opt in options:
                text = opt.text.strip()
                if not text or text in ["--اختر--", "-اختر-", "اختر"]:
                    continue
                if opt.is_displayed() and opt.is_enabled():
                    opt.click()
                    logger.success(f"✅ مركز التكلفة: {text}")
                    time.sleep(0.3)
                    return True
            return False
        except Exception as e:
            logger.warning(f"⚠️ مشكلة: {str(e)[:100]}")
            return False

    def fill_required_select2_fields(self):
        logger.info("ملء حقول Select2")
        self.wait_for_preloader()
        self._fill_select2_field("PaymentType", InvoiceDefaults.PAYMENT_TYPE, "نوع السداد")
        self._fill_select2_field("CountryId", InvoiceDefaults.COUNTRY, "الدولة")
        self._fill_select2_field("CityId", InvoiceDefaults.CITY, "المدينة")
        self._fill_select2_field("ProjectId", InvoiceDefaults.PROJECT, "المشروع")
        time.sleep(1)
        if InvoiceDefaults.FORCE_COST_CENTER:
            self._force_reload_cost_center()
        logger.success("✅ تم ملء حقول Select2")

    def uncheck_auto_voucher(self):
        logger.info("التحقق من checkbox 'إنشاء سند صرف'")
        try:
            el = self.driver.find_element(*self.AUTO_VOUCHER)
            if el.is_selected():
                self.driver.execute_script("arguments[0].click();", el)
                time.sleep(0.2)
                if not el.is_selected():
                    logger.success("✅ تم إلغاء 'إنشاء سند صرف'")
                    return True
            else:
                logger.info("⏭️ مش مفعّل")
            return True
        except Exception as e:
            logger.warning(f"⚠️ مشكلة: {str(e)[:100]}")
            return False

    def get_all_required_status(self):
        status = {}
        for name, locator in [
            ("comm_reg", self.COMM_REG),
            ("vat", self.VAT_NUMBER),
            ("postal", self.POSTAL_CODE),
            ("building", self.BUILDING_NUMBER),
        ]:
            try:
                el = self.driver.find_element(*locator)
                status[name] = el.get_attribute("value") or "(فاضي)"
            except Exception:
                status[name] = "(مش موجود)"
        for name, sid in [
            ("payment", "PaymentType"),
            ("country", "CountryId"),
            ("city", "CityId"),
            ("project", "ProjectId"),
            ("cost_center", "CostCenterId"),
        ]:
            val = self._select2_has_value(sid)
            status[name] = val if val else "(فاضي)"
        return status

    def find_validation_errors(self):
        errors = []
        try:
            for el in self.driver.find_elements(
                By.CSS_SELECTOR,
                ".field-validation-error, .text-danger:not(:empty)"
            ):
                if el.is_displayed():
                    t = el.text.strip()
                    if t and t not in errors:
                        errors.append(t)
        except Exception:
            pass
        return errors

    # ========== Save ==========
    def click_save(self):
        logger.info("اضغط زر الحفظ")
        self.wait_for_preloader()
        try:
            btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(self.SAVE_BUTTON)
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            btn.click()
            logger.info("✅ ضغط حفظ")
        except Exception as e:
            logger.warning(f"محاولة JS: {e}")
            btn = self.driver.find_element(*self.SAVE_BUTTON)
            self.driver.execute_script("arguments[0].click();", btn)

    def get_swal_message(self, timeout=5):
        try:
            popup = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self.SWAL_POPUP)
            )
            title = ""
            content = ""
            try:
                title = popup.find_element(By.CSS_SELECTOR, ".swal2-title").text
            except Exception:
                pass
            try:
                content = popup.find_element(By.CSS_SELECTOR, ".swal2-html-container").text
            except Exception:
                pass
            return {"title": title, "content": content}
        except TimeoutException:
            return None

    def confirm_swal(self):
        try:
            btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(self.SWAL_CONFIRM)
            )
            btn.click()
            logger.info("✅ تم الضغط على موافقة")
            return True
        except TimeoutException:
            return False

    # ========== NEW: Handle multiple SweetAlerts ==========
    def handle_all_swals(self, max_count=5, timeout=8, wait_after=1):
        """
        يتعامل مع كل SweetAlerts اللي بتظهر ورا بعض
        - "عدم انشاء سند صرف الى" → موافقة
        - "هل تريد الحفظ؟" → موافقة
        - أي رسالة نجاح → يوقف
        - يرجع عدد SweetAlerts اللي اتعامل معاها
        """
        count = 0
        for i in range(max_count):
            try:
                popup = WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located(self.SWAL_POPUP)
                )

                title = ""
                try:
                    title = popup.find_element(By.CSS_SELECTOR, ".swal2-title").text.strip()
                except Exception:
                    pass

                logger.info(f"SweetAlert #{i+1}: '{title}'")
                self.take_screenshot(f"swal_{i+1}")

                title_lower = title.lower()
                # لو رسالة نجاح، مش محتاج نضغط
                if any(w in title_lower for w in ["نجح", "تم الحفظ", "success", "saved", "تمت"]):
                    logger.info("✅ رسالة نجاح - مش محتاج ضغط إضافي")
                    break

                # اضغط موافقة
                try:
                    confirm_btn = popup.find_element(By.CSS_SELECTOR, "button.swal2-confirm")
                    confirm_btn.click()
                    logger.success(f"✅ ضغط موافقة #{i+1}")
                    count += 1
                    time.sleep(wait_after)

                    # استنى الـ SweetAlert الحالي يختفي
                    try:
                        WebDriverWait(self.driver, 3).until(
                            EC.invisibility_of_element_located(self.SWAL_POPUP)
                        )
                    except TimeoutException:
                        pass

                except Exception as e:
                    logger.warning(f"مشكلة في الضغط: {str(e)[:100]}")
                    break

            except TimeoutException:
                logger.info(f"مفيش SweetAlert تاني (بعد {count})")
                break

        return count

    def is_invoice_saved(self):
        current = self.driver.current_url
        if "/AddEdit" not in current and "/SalesInvoice" in current:
            logger.success(f"✅ خرجنا: {current}")
            return True
        swal = self.get_swal_message(timeout=3)
        if swal:
            text = (swal.get("title", "") + " " + swal.get("content", "")).lower()
            success_words = ["نجح", "تم", "success", "saved", "حفظ"]
            if any(w in text for w in success_words):
                return True
        return False

    def wait_for_save_result(self, timeout=30):
        """انتظر نتيجة الحفظ"""
        logger.info(f"في انتظار نتيجة الحفظ (max {timeout}s)...")
        original_url = self.driver.current_url
        start = time.time()

        while time.time() - start < timeout:
            current = self.driver.current_url

            if original_url != current and "/SalesInvoice" in current and "/AddEdit" not in current:
                logger.success(f"🎯 الحفظ نجح - الرابط اتغير: {current}")
                return True

            try:
                for el in self.driver.find_elements(
                    By.CSS_SELECTOR,
                    ".toast-success, .alert-success, .success-message"
                ):
                    if el.is_displayed() and el.text.strip():
                        text = el.text.strip()
                        if "حفظ" in text or "success" in text.lower() or "saved" in text.lower():
                            logger.success(f"✅ رسالة نجاح: {text}")
                            return True
            except Exception:
                pass

            try:
                for el in self.driver.find_elements(
                    By.CSS_SELECTOR,
                    ".toast-error, .alert-danger:not(.d-none)"
                ):
                    if el.is_displayed() and el.text.strip():
                        logger.error(f"❌ رسالة خطأ: {el.text.strip()}")
                        return False
            except Exception:
                pass

            time.sleep(0.5)

        logger.warning(f"⚠️ انتهى الوقت. URL: {self.driver.current_url}")
        return False

# ============================================================
# 📋 قراءة رقم المستند من قائمة الفواتير
# ============================================================

INVOICE_LIST_URL    = "/SalesInvoice"
INVOICE_LIST_ROW    = (By.CSS_SELECTOR, "table tbody tr")
INVOICE_NUMBER_CELL = (By.CSS_SELECTOR, "td:first-child")


def get_latest_invoice_number(driver, timeout=15):
    """
    يفتح /SalesInvoice ويقرأ أحدث رقم مستند (int) أو None.
    """
    from config.settings import BASE_URL
    import re

    logger.info("📋 قراءة أحدث رقم مستند من القائمة...")

    # نروح لصفحة القائمة
    if INVOICE_LIST_URL not in driver.current_url:
        driver.get(f"{BASE_URL}{INVOICE_LIST_URL}")

    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(INVOICE_LIST_ROW)
        )
        time.sleep(1)  # نستنى الجدول يستقر

        rows = driver.find_elements(*INVOICE_LIST_ROW)
        if not rows:
            logger.warning("⚠️ الجدول فاضي")
            return None

        # أول صف = أحدث فاتورة
        first_row = rows[0]
        cells = first_row.find_elements(By.TAG_NAME, "td")
        if not cells:
            logger.warning("⚠️ مفيش خلايا في أول صف")
            return None

        raw = cells[0].text.strip()
        m = re.search(r"\d+", raw)
        if not m:
            logger.warning(f"⚠️ مفيش رقم في أول خلية: «{raw}»")
            return None

        number = int(m.group(0))
        logger.info(f"✅ أحدث رقم مستند: {number}")
        return number

    except TimeoutException:
        logger.error("❌ الجدول مش ظهر")
        return None
    except Exception as e:
        logger.error(f"❌ خطأ في قراءة الرقم: {e}")
        return None


def wait_for_new_invoice(driver, previous_number, timeout=60, poll=2):
    """
    ينتظر لحد ما رقم مستند أكبر من previous_number يظهر.
    يرجع الرقم الجديد أو None.
    """
    from config.settings import BASE_URL
    import re

    logger.info(f"⏳ انتظار فاتورة جديدة (أكبر من {previous_number})...")
    end = time.time() + timeout
    attempt = 0

    while time.time() < end:
        attempt += 1
        driver.get(f"{BASE_URL}{INVOICE_LIST_URL}")

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(INVOICE_LIST_ROW)
            )
            time.sleep(1)

            rows = driver.find_elements(*INVOICE_LIST_ROW)
            if rows:
                cells = rows[0].find_elements(By.TAG_NAME, "td")
                if cells:
                    m = re.search(r"\d+", cells[0].text)
                    if m:
                        latest = int(m.group(0))
                        logger.info(f"🔍 محاولة #{attempt}: أحدث رقم = {latest}")

                        if latest > previous_number:
                            logger.info(f"🎉 فاتورة جديدة ظهرت: {latest}")
                            return latest
        except Exception as e:
            logger.warning(f"⚠️ محاولة #{attempt} فشلت: {e}")

        time.sleep(poll)

    logger.error(f"❌ مفيش فاتورة جديدة بعد {timeout}s")
    return None
