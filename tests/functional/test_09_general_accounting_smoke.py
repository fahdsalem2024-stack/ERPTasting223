"""
General Accounting Smoke Tests
12 شاشة — تفتح + تعرض بيانات
"""
import pytest
import time
import allure
from pages.login_page import LoginPage
from pages.general_list_page import GeneralListPage
from utils.logger import logger
from config.general_accounting_modules import GeneralAccountingModules


def _login(driver, credentials):
    """تسجيل دخول"""
    login = LoginPage(driver)
    login.load()
    login.login(credentials["username"], credentials["password"])
    return True


@allure.feature("General Accounting")
@allure.story("Smoke Tests - All Modules")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.smoke
def test_general_accounting_all_modules_smoke(driver, credentials):
    """
    اختبار Smoke لكل شاشات الحسابات العامة:
    - يفتح كل شاشة
    - يستنى التحميل
    - يتأكد إن فيه جدول + بيانات
    - مفيش أخطاء
    """
    start = time.time()
    logger.info("=" * 60)
    logger.info("🧪 Smoke Test: كل شاشات الحسابات العامة")
    logger.info(f"📊 عدد الشاشات: {GeneralAccountingModules.count()}")
    logger.info("=" * 60)

    # تسجيل دخول مرة واحدة
    _login(driver, credentials)

    all_results = []
    modules = GeneralAccountingModules.get_all()

    for key, info in modules.items():
        page = GeneralListPage(driver, info["url"])
        result = page.run_smoke_test(key, info)
        all_results.append(result)
        time.sleep(1)

    # ===== تقرير نهائي =====
    logger.info("")
    logger.info("=" * 60)
    logger.info("📊 التقرير النهائي")
    logger.info("=" * 60)

    passed = [r for r in all_results if r["success"]]
    failed = [r for r in all_results if not r["success"]]

    logger.info(f"✅ نجح: {len(passed)}/{len(all_results)}")
    logger.info(f"❌ فشل: {len(failed)}/{len(all_results)}")

    logger.info("")
    logger.info("📋 التفاصيل:")
    for r in all_results:
        status = "✅" if r["success"] else "❌"
        logger.info(
            f"  {status} {r['name_ar']:<30} | صفوف: {r['row_count']:>3} | "
            f"جدول: {'✅' if r['has_table'] else '❌'} | "
            f"إضافة: {'✅' if r['has_add_button'] else '❌'}"
        )

    elapsed = time.time() - start
    logger.info("")
    logger.info(f"⏱️ الوقت الإجمالي: {int(elapsed // 60)}:{int(elapsed % 60):02d}")

    # ===== تأكيد =====
    # لازم على الأقل 9 من 12 ينجحوا
    success_rate = len(passed) / len(all_results) if all_results else 0
    assert success_rate >= 0.75, (
        f"❌ نسبة النجاح {success_rate:.0%} أقل من 75%. "
        f"فشل: {[r['name_ar'] for r in failed]}"
    )

    logger.success(f"🎉 نجح {len(passed)}/{len(all_results)} ({success_rate:.0%})")


@allure.feature("General Accounting")
@allure.story("Smoke Test - Individual")
@pytest.mark.parametrize("module_key", list(GeneralAccountingModules.get_all().keys()))
def test_individual_module_smoke(driver, credentials, module_key):
    """
    اختبار Smoke لكل شاشة على حدة
    (مفيد للتشغيل الفردي)
    """
    info = GeneralAccountingModules.get_by_key(module_key)
    if not info:
        pytest.skip(f"مفيش شاشة بالاسم: {module_key}")

    _login(driver, credentials)

    page = GeneralListPage(driver, info["url"])
    result = page.run_smoke_test(module_key, info)

    assert result["loaded"], f"❌ {info['name_ar']}: الصفحة مش اتحملت"
    assert result["has_table"], f"❌ {info['name_ar']}: مفيش جدول"
    assert not result["has_errors"], f"❌ {info['name_ar']}: فيه أخطاء"