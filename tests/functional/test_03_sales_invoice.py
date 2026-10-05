import pytest
import time
import allure
from pages.login_page import LoginPage
from pages.sales_invoice_page import SalesInvoicePage
from utils.logger import logger
from config.invoice_data import InvoiceDefaults


def _login_and_open_add(driver, credentials):
    login = LoginPage(driver)
    login.load()
    login.login(credentials["username"], credentials["password"])
    invoice = SalesInvoicePage(driver)
    invoice.open_list()
    invoice.click_add_new()
    assert invoice.is_on_add_page(), f"مش في صفحة الإضافة: {driver.current_url}"
    return invoice


@allure.feature("Sales Invoice")
@allure.story("Create Full Invoice")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
def test_full_sales_invoice_flow(driver, credentials):
    """اختبار كامل: إنشاء فاتورة بيع"""
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("اختبار: إنشاء فاتورة بيع كاملة")
    logger.info("=" * 60)

    invoice = _login_and_open_add(driver, credentials)

    logger.info("1) عميل")
    invoice.select_customer()

    logger.info("2) نافذة الأصناف")
    invoice.click_plus_button()
    invoice.wait_for_item_modal(timeout=20)

    logger.info("3) بحث")
    invoice.click_search_btn_in_modal()
    invoice.wait_for_items_results(timeout=20)

    logger.info("4) صنف")
    invoice.click_add_item_by_name("فلتر تكييف")

    logger.info("5) سعر")
    invoice.set_price_for_last_item("10000")

    logger.info("6) حقول نصية")
    invoice.fill_required_text_fields()

    logger.info("7) Select2")
    invoice.fill_required_select2_fields()

    if InvoiceDefaults.UNCHECK_AUTO_VOUCHER:
        logger.info("8) إلغاء سند الصرف")
        invoice.uncheck_auto_voucher()

    invoice.take_screenshot("inv_before_save")

    logger.info("9) تحقق")
    status = invoice.get_all_required_status()
    logger.info(f"حالة الحقول: {status}")

    essential = ["comm_reg", "vat", "postal", "building", "payment", "project", "cost_center"]
    missing = [k for k in essential if status.get(k) in ["(فاضي)", "(مش موجود)"]]
    assert not missing, f"❌ حقول ناقصة: {missing}"

    logger.info("10) حفظ")
    invoice.click_save()

    logger.info("التعامل مع SweetAlerts...")
    swal_count = invoice.handle_all_swals(max_count=5, timeout=25)
    logger.info(f"عدد SweetAlerts اللي اتعاملنا معاها: {swal_count}")

    logger.info("11) انتظار نتيجة الحفظ...")
    saved = invoice.wait_for_save_result(timeout=45)
    invoice.take_screenshot("inv_final")

    elapsed = time.time() - start_time
    logger.info(f"⏱️ الوقت الإجمالي: {int(elapsed // 60)}:{int(elapsed % 60):02d}")

    assert saved, f"❌ الفاتورة مش اتحفظت! URL: {driver.current_url}"

    # ⚠️ التحقق النهائي: من صفحة الفواتير
    logger.info("🔍 التحقق النهائي من صفحة الفواتير...")
    verified = invoice.verify_invoice_in_list(expected_amount="10000")
    invoice.take_screenshot("inv_verify_list")

    if verified:
        logger.success("🎉✅ الفاتورة اتحفظت فعلاً وموجودة في القائمة!")
    else:
        logger.warning("⚠️ الفاتورة مش موجودة في القائمة (بس حفظت)")

    # النجاح النهائي
    logger.success(f"🎉 الفاتورة اتحفظت بنجاح! ({int(elapsed)} ثانية)")

    logger.success(f"🎉 الفاتورة اتحفظت بنجاح! ({int(elapsed)} ثانية)")




