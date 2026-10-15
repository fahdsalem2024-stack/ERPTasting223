"""
Cash Receipt Voucher Page Object
سند القبض — إنشاء + حفظ + تحقق
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage
from utils.select2_helper import Select2Helper
from utils.logger import logger
from config.settings import BASE_URL
from config.cash_receipt_data import CashReceiptDefaults
import time
import re


class CashReceiptVoucherPage(BasePage):
    LIST_URL = f"{BASE_URL}/CashReceiptVoucher"
    ADD_URL = f"{BASE_URL}/CashReceiptVoucher/AddEdit"

    # ===== Navigation =====
    ADD_NEW_BUTTON = (By.CSS_SELECTOR, "a[href='/CashReceiptVoucher/AddEdit']")

    # ===== الحقول الإجبارية =====
    BRANCH_SELECT2 = "BranchId"                # ⚠️ ممكن يتغير — ابعتيلي الـ ID الفعلي
    CUSTOMER_SELECT2 = "CustomerId"            # ⚠️ ممكن يتغير
    DATE_INPUT = (By.CSS_SELECTOR, "input[type='datetime-local'], input[name='Date'], input#Date")
    AMOUNT_INPUT = (By.CSS_SELECTOR, "input#Amount, input[name='Amount']")
    PAYMENT_METHOD_SELECT2 = "PaymentMethodId" # ⚠️ ممكن يتغير
    COST_CENTER_SELECT2 = "CostCenterId"
    EXCHANGE_RATE_SELECT2 = "ExchangeRateId"   # ⚠️ ممكن يتغير
    CURRENCY_INPUT = (By.CSS_SELECTOR, "input#Currency, input[name='Currency']")

    # ===== حقول نصية =====
    DOCUMENT_NUMBER = (By.ID, "DocumentNumber")
    SERIAL = (By.ID, "Serial")
    REFERENCE_NUMBER = (By.ID, "ReferenceNumber")
    MANUAL_NUMBER = (By.ID, "ManualNumber")
    NOTES = (By.ID, "Notes")
    DESCRIPTION = (By.ID, "Description")

    # ===== Checkboxes =====
    PREPAID_PAYMENTS = (By.ID, "PrepaidPayments")
    STOP_CURRENCY = (By.ID, "StopCurrencyConversion")
    SELECT_INVOICES = (By.ID, "SelectInvoices")

    # ===== Save =====
    SAVE_BUTTON = (By.CSS_SELECTOR, "button#save, button[onclick*='save']")
    SAVE_AND_NEW = (By.CSS_SELECTOR, "button#saveAndNew, button[onclick*='saveAndNew']")

    # ===== SweetAlerts =====
    SWAL_POPUP = (By.CSS_SELECTOR, ".swal2-popup")
    SWAL_CONFIRM = (By.CSS_SELECTOR, "button.swal2-confirm")

    # ===== Preloader =====
    PRELOADER = (By.ID, "preloader")

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

    # ========== Select2 Fields ==========
    def _fill_select2(self, select_id, value, name, force=False):
        """يملأ حقل Select2 بأمان"""
        try:
            if not force:
                current = self._select2_has_value(select_id)
                if current:
                    logger.info(f"⏭️ {name} متملي: {current}")
                    return True

            if value:
                if self.s2.select_by_id(select_id, value):
                    logger.success(f"✅ {name} = {value}")
                    return True

            if self.s2.force_select_value(select_id, value or ""):
                time.sleep(0.3)
                current = self._select2_has_value(select_id)
                if current:
                    logger.success(f"✅ {name} = {current}")
                    return True

            if self.s2.select_first_real_option(select_id):
                logger.success(f"✅ {name} = (أول خيار)")
                return True

            logger.warning(f"⚠️ فشل {name}")
            return False
        except Exception as e:
            logger.warning(f"⚠️ مشكلة في {name}: {str(e)[:120]}")
            return False

    def _select2_has_value(self, select_id):
        try:
            container = self.driver.find_element(By.ID, f"select2-{select_id}-container")
            text = container.text.strip()
            if text and text not in ["--اختر--", "-اختر-", "اختر", ""]:
                return text
        except Exception:
            pass
        return None

    def fill_branch(self):
        return self._fill_select2(
            self.BRANCH_SELECT2, CashReceiptDefaults.BRANCH, "الفرع"
        )

    def fill_customer(self):
        return self._fill_select2(
            self.CUSTOMER_SELECT2, CashReceiptDefaults.CUSTOMER, "العميل"
        )

    def fill_payment_method(self):
        return self._fill_select2(
            self.PAYMENT_METHOD_SELECT2, CashReceiptDefaults.PAYMENT_METHOD, "طريقة الدفع"
        )

    def fill_cost_center(self):
        # دايماً force عشان القيمة الافتراضية
        return self._fill_select2(
            self.COST_CENTER_SELECT2, CashReceiptDefaults.COST_CENTER, "مركز التكلفة", force=True
        )

    def fill_exchange_rate(self):
        return self._fill_select2(
            self.EXCHANGE_RATE_SELECT2, CashReceiptDefaults.EXCHANGE_RATE, "سعر الصرف"
        )

    # ========== Text Fields ==========
    def _fill_text(self, locator, value, name):
        """يملأ حقل نصي — يتخطى لو متملي"""
        if not value:
            return True
        try:
            el = self.driver.find_element(*locator)
            current = el.get_attribute("value") or ""
            if current.strip():
                logger.info(f"⏭️ {name} متملي: {current}")
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
            logger.success(f"✅ {name}: {value}")
            return True
        except Exception as e:
            logger.warning(f"⚠️ مشكلة {name}: {str(e)[:100]}")
            return False

    def fill_amount(self):
        return self._fill_text(
            self.AMOUNT_INPUT, CashReceiptDefaults.AMOUNT, "المبلغ"
        )

    def fill_currency(self):
        return self._fill_text(
            self.CURRENCY_INPUT, CashReceiptDefaults.CURRENCY, "العملة"
        )

    def fill_optional_text_fields(self):
        """الحقول الاختيارية"""
        self._fill_text(self.REFERENCE_NUMBER, CashReceiptDefaults.REFERENCE_NUMBER, "الرقم المرجعي")
        self._fill_text(self.MANUAL_NUMBER, CashReceiptDefaults.MANUAL_NUMBER, "الرقم اليدوي")
        self._fill_text(self.NOTES, CashReceiptDefaults.NOTES, "ملاحظات")
        self._fill_text(self.DESCRIPTION, CashReceiptDefaults.DESCRIPTION, "الشروح")

    # ========== Checkboxes ==========
    def _set_checkbox(self, locator, value, name):
        """يضبط checkbox — لو value=False → يلغيه"""
        try:
            el = self.driver.find_element(*locator)
            is_checked = el.is_selected()
            if is_checked == value:
                logger.info(f"⏭️ {name} = {value} (زي ما هو)")
                return True
            self.driver.execute_script("arguments[0].click();", el)
            time.sleep(0.2)
            logger.success(f"✅ {name} = {value}")
            return True
        except Exception as e:
            logger.warning(f"⚠️ مشكلة {name}: {str(e)[:100]}")
            return False

    def set_checkboxes(self):
        self._set_checkbox(self.PREPAID_PAYMENTS, CashReceiptDefaults.PREPAID_PAYMENTS, "الدفعات مقدمة")
        self._set_checkbox(self.STOP_CURRENCY, CashReceiptDefaults.STOP_CURRENCY_CONVERSION, "إيقاف التحويل النقدي")
        self._set_checkbox(self.SELECT_INVOICES, CashReceiptDefaults.SELECT_INVOICES, "تحديد الفواتير")

    # ========== Fill All ==========
    def fill_all_required_fields(self):
        """يملأ كل الحقول الإجبارية"""
        logger.info("ملء الحقول الإجبارية لسند القبض")

        self.wait_for_preloader()
        time.sleep(0.5)

        self.fill_branch()
        self.fill_customer()
        self.fill_amount()
        self.fill_payment_method()
        time.sleep(0.5)
        if CashReceiptDefaults.FORCE_COST_CENTER:
            self.fill_cost_center()
        self.fill_exchange_rate()
        self.fill_currency()
        self.fill_optional_text_fields()
        self.set_checkboxes()

        logger.success("✅ تم ملء كل الحقول")

    def get_all_status(self):
        """يرجع حالة كل الحقول"""
        status = {}
        try:
            status["amount"] = self.driver.find_element(*self.AMOUNT_INPUT).get_attribute("value") or "(فاضي)"
        except Exception:
            status["amount"] = "(مش موجود)"

        for name, sid in [
            ("branch", self.BRANCH_SELECT2),
            ("customer", self.CUSTOMER_SELECT2),
            ("payment_method", self.PAYMENT_METHOD_SELECT2),
            ("cost_center", self.COST_CENTER_SELECT2),
            ("exchange_rate", self.EXCHANGE_RATE_SELECT2),
        ]:
            val = self._select2_has_value(sid)
            status[name] = val if val else "(فاضي)"
        return status

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
            logger.success("✅ ضغط حفظ")
        except Exception as e:
            logger.warning(f"محاولة JS: {e}")
            btn = self.driver.find_element(*self.SAVE_BUTTON)
            self.driver.execute_script("arguments[0].click();", btn)

    def handle_all_swals(self, max_count=5, timeout=5, wait_after=0.5):
        """يتعامل مع كل SweetAlerts اللي بتظهر"""
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
                self.take_screenshot(f"crv_swal_{i+1}")

                title_lower = title.lower()
                if any(w in title_lower for w in ["نجح", "تم الحفظ", "success", "saved", "تمت"]):
                    logger.info("✅ رسالة نجاح")
                    break

                try:
                    confirm_btn = popup.find_element(By.CSS_SELECTOR, "button.swal2-confirm")
                    confirm_btn.click()
                    logger.success(f"✅ ضغط موافقة #{i+1}")
                    count += 1
                    time.sleep(wait_after)

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

    def wait_for_save_result(self, timeout=30):
        """ينتظر نتيجة الحفظ"""
        logger.info(f"في انتظار نتيجة الحفظ (max {timeout}s)...")
        start = time.time()
        original_url = self.driver.current_url
        was_in_addedit = "/AddEdit" in original_url

        while time.time() - start < timeout:
            current = self.driver.current_url

            # URL change
            if was_in_addedit and "/CashReceiptVoucher" in current and "/AddEdit" not in current:
                logger.success(f"🎯 الحفظ نجح - الرابط اتغير: {current}")
                time.sleep(2)
                return True

            # fallback
            if "/CashReceiptVoucher" in current and "/AddEdit" not in current and "/Login" not in current:
                logger.success(f"🎯 الحفظ نجح (fallback) - الرابط: {current}")
                time.sleep(1)
                return True

            # SweetAlert نجاح
            try:
                for s in self.driver.find_elements(By.CSS_SELECTOR, ".swal2-popup"):
                    if s.is_displayed():
                        text = s.text.strip()
                        if "حفظ" in text or "نجح" in text or "success" in text.lower():
                            try:
                                confirm = s.find_element(By.CSS_SELECTOR, "button.swal2-confirm")
                                if confirm.is_displayed():
                                    self.driver.execute_script("arguments[0].click();", confirm)
                                    time.sleep(1)
                            except Exception:
                                pass
                            logger.success("🎯 الحفظ نجح (SweetAlert)")
                            return True
            except Exception:
                pass

            # Toast نجاح
            try:
                for el in self.driver.find_elements(By.CSS_SELECTOR, ".toast-success, .alert-success"):
                    if el.is_displayed() and el.text.strip():
                        if "حفظ" in el.text or "تم" in el.text:
                            logger.success(f"✅ رسالة نجاح: {el.text.strip()}")
                            return True
            except Exception:
                pass

            time.sleep(0.5)

        logger.warning(f"⚠️ انتهى الوقت. URL: {self.driver.current_url}")
        return False

    def verify_voucher_in_list(self, expected_amount: str = None, timeout: int = 20):
        """يتحقق إن السند ظهر في القائمة"""
        logger.info(f"🔍 التحقق من السند في القائمة (المبلغ: {expected_amount})...")
        try:
            if "/CashReceiptVoucher" not in self.driver.current_url or "/AddEdit" in self.driver.current_url:
                self.driver.get(self.LIST_URL)

            self.wait_for_preloader()
            time.sleep(2)

            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
            )
            time.sleep(1)

            rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            if not rows:
                logger.warning("⚠️ الجدول فاضي")
                return False

            logger.info(f"عدد السندات في القائمة: {len(rows)}")
            first_row = rows[0]
            row_text = first_row.text.strip()
            logger.info(f"أول صف: {row_text[:150]}")

            if not expected_amount:
                return True

            row_clean = row_text.replace(",", "").replace("٫", "").replace("٬", "")
            amount_clean = str(expected_amount).replace(",", "").replace(".", "").strip()

            if amount_clean in row_clean:
                logger.success(f"✅ لقيت المبلغ {expected_amount} في القائمة")
                return True

            try:
                amount_num = float(str(expected_amount).replace(",", ""))
                numbers = re.findall(r'\d+(?:[\.,]\d+)?', row_clean)
                for num_str in numbers:
                    try:
                        num = float(num_str.replace(",", ""))
                        if abs(num - amount_num) < 0.01:
                            logger.success(f"✅ لقيت المبلغ {expected_amount}")
                            return True
                    except ValueError:
                        continue
            except Exception:
                pass

            logger.warning(f"⚠️ المبلغ {expected_amount} مش موجود")
            return False
        except TimeoutException:
            logger.error("❌ الجدول مش ظهر")
            return False
        except Exception as e:
            logger.error(f"❌ مشكلة: {str(e)[:150]}")
            return False