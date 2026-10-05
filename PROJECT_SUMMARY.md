# 📋 ERP Test Automation — ملخص المشروع الشامل

**آخر تحديث:** 2026-10-05
**الحالة:** ✅ يعمل بنجاح
**الإصدار:** v3.0

---

## 1. نظرة عامة

مشروع أتمتة اختبارات نظام ERP بـ Python + Selenium + Pytest + Streamlit.

**الهدف:** اختبار End-to-End كامل لفاتورة بيع.

**المكونات:**
- Framework احترافي (Page Object Model)
- Dashboard متقدم (Streamlit)
- إشعارات إيميل + جدولة تلقائية
- تقارير تفاعلية مع Charts

---

## 2. معلومات الموقع

- Base URL: https://test-site-nq.premiumasp.net
- Login: /Login
- Sales Invoice List: /SalesInvoice
- Sales Invoice Add: /SalesInvoice/AddEdit

### بيانات الدخول (.env)

BASE_URL=https://test-site-nq.premiumasp.net
LOGIN_USERNAME=erpadmin
LOGIN_PASSWORD=Admin@01212388887

---

## 3. بيئة التشغيل

- OS: Windows 11
- Python: 3.14.7
- Chrome: 154.0.8037.58
- مجلد المشروع: D:\50505050505050505050050505050\erp-automation
- venv: venv\Scripts\activate
- ChromeDriver: drivers\chromedriver.exe

### مشاكل بيئة معروفة

| المشكلة | الحل |
|---|---|
| Application Control Policy بتحجب pip.exe | استخدم python -m pip install |
| DNS مبيعرفش msedgedriver.azureedge.net | استخدم ChromeDriver محلي |
| BOM في ملفات PowerShell | استخدم Out-File -Encoding utf8 |
| WinError 4551 | إعادة تشغيل الجهاز |

---

## 4. هيكل المشروع
erp-automation/
│
├── config/
│ ├── settings.py # إعدادات + URLs
│ ├── invoice_data.py # قيم افتراضية
│ ├── test_registry.py # سجل الاختبارات
│ ├── test_runner.py # مدير التشغيل
│ ├── emailer.py # خدمة الإيميل
│ └── schedules/
│
├── pages/
│ ├── base_page.py # كلاس أساسي
│ ├── login_page.py # تسجيل الدخول
│ └── sales_invoice_page.py # فاتورة البيع
│
├── utils/
│ ├── logger.py # loguru
│ └── select2_helper.py # معالج Select2
│
├── tests/
│ ├── conftest.py # Fixtures
│ └── functional/
│ └── test_03_sales_invoice.py
│
├── dashboard/
│ ├── .streamlit/config.toml
│ ├── app.py # الرئيسية
│ ├── theme.py # Dark/Light
│ ├── status.py # Live Status
│ └── pages/
│ ├── 1_Run_Tests.py
│ ├── 2_Reports.py
│ ├── 3_Screenshots.py
│ ├── 4_Compare.py
│ ├── 5_Schedule.py
│ └── 6_Email.py
│
├── drivers/
│ └── chromedriver.exe
│
├── reports/
│ ├── results/ # JSON
│ ├── screenshots/ # PNG
│ └── .running # Lock file
│
├── logs/
├── .env
├── requirements.txt
├── pytest.ini
└── PROJECT_SUMMARY.md
---

## 5. الاختبارات المتاحة

### 🧾 فاتورة بيع كاملة

**الملف:** tests/functional/test_03_sales_invoice.py
**الاسم:** test_full_sales_invoice_flow
**المدة:** ~2:33 دقيقة
**الحالة:** ✅ يعمل بنجاح

**الخطوات:**
1. تسجيل دخول
2. فتح فاتورة بيع جديدة
3. اختيار عميل (588897991 - محمد جدة)
4. فتح نافذة الأصناف (زر span.Add-Button ➕)
5. بحث الأصناف (زر #submitSearch في modal)
6. إضافة صنف فلتر تكييف
7. كتابة السعر 10000
8. ملء الحقول النصية:
   - CommercialRegistrationNumber = 1234567890
   - CashCustomerVATNumber = 123456789012343
   - PostalCode = 12345
   - BuildingNumber = 1234
9. ملء Select2:
   - PaymentType = نقدى
   - CountryId = جده - 245
   - CityId = الرياض
   - ProjectId = 23 - مشروع بناء برج الرياض
   - CostCenterId = 12 - خط انتاج السكر اصابع 5 خط
10. إلغاء AutoGenerateStockReceiptVoucher
11. حفظ (3 SweetAlerts)
12. التحقق (URL يتغير لـ /SalesInvoice)

---

## 6. Selectors المهمة

### تسجيل الدخول

    USERNAME_INPUT = (By.ID, "userName")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button.btn-login")

### الفاتورة

    ADD_NEW_BUTTON = (By.CSS_SELECTOR, "a[href='/SalesInvoice/AddEdit']")
    CUSTOMER_SELECT2 = "VendorOrCustomerId"
    ITEM_ADD_PLUS_BUTTON = (By.CSS_SELECTOR, "span.Add-Button")
    SEARCH_BTN_IN_MODAL = (By.CSS_SELECTOR, ".modal.show #submitSearch")
    ITEM_ROW_ANY = (By.CSS_SELECTOR, ".modal.show tbody tr")
    COMM_REG = (By.ID, "CommercialRegistrationNumber")
    VAT_NUMBER = (By.ID, "CashCustomerVATNumber")
    POSTAL_CODE = (By.ID, "PostalCode")
    BUILDING_NUMBER = (By.ID, "BuildingNumber")
    AUTO_VOUCHER = (By.ID, "AutoGenerateStockReceiptVoucher")
    SAVE_BUTTON = (By.CSS_SELECTOR, "button#save")

### SweetAlerts + Preloader

    SWAL_POPUP = (By.CSS_SELECTOR, ".swal2-popup")
    SWAL_CONFIRM = (By.CSS_SELECTOR, "button.swal2-confirm")
    PRELOADER = (By.ID, "preloader")

---

## 7. SweetAlerts في الموقع

الموقع بيعرض 3 SweetAlerts بالترتيب عند الحفظ:

| # | الرسالة | الإجراء |
|---|---|---|
| 1 | عدم انشاء سند صرف الى | موافقة |
| 2 | هل تريد الحفظ؟ | موافقة |
| 3 | حفظ | موافقة |

**الدالة المسؤولة:** handle_all_swals(max_count=5, timeout=8)

---

## 8. كتابة السعر — الطريقة الصح

**المشكلة:** send_keys العادي بيفشل بسبب preloader.

**الحل الناجح:** استخدام JavaScript value assignment:

```python
def set_price_for_last_item(self, price):
    inputs = driver.find_elements(By.CSS_SELECTOR, "input.float.price")
    last_input = inputs[-1]
    
    driver.execute_script("""
        var el = arguments[0];
        el.value = '';
        el.value = arguments[1];
        el.dispatchEvent(new Event('input', {bubbles: true}));
        el.dispatchEvent(new Event('change', {bubbles: true}));
        el.dispatchEvent(new Event('keyup', {bubbles: true}));
        el.dispatchEvent(new Event('blur', {bubbles: true}));
    """, last_input, str(price))
    
    time.sleep(2)
    actual = last_input.get_attribute("value")
    return actual and actual != "0.0000"
الطريقة اللي فشلت: click() + send_keys → element click intercepted.
الطريقة اللي نجحت: JS value assignment مباشرة.

9. التحقق من الحفظ
الدالة: wait_for_save_result(timeout=20)

المنطق:

URL اتغير من /AddEdit لـ /SalesInvoice → ✅ نجاح

رسالة Toast فيها "حفظ" أو "success" → ✅ نجاح

رسالة خطأ في .alert-danger → ❌ فشل

10. الأوامر السريعة
الانتقال للمشروع
cd D:\50505050505050505050050505050\erp-automation
venv\Scripts\activate

تشغيل اختبار الفاتورة
python -m pytest tests/functional/test_03_sales_invoice.py::test_full_sales_invoice_flow -v -s

تشغيل كل الاختبارات
python -m pytest tests/ -v

الداشبورد
streamlit run dashboard/app.py

فتح مجلد الصور
explorer reports\screenshots

11. ملفات المشروع المهمة
.env
BASE_URL=https://test-site-nq.premiumasp.net
LOGIN_USERNAME=erpadmin
LOGIN_PASSWORD=Admin@01212388887

requirements.txt
selenium==4.25.0
webdriver-manager==4.0.2
pytest==8.3.3
pytest-html==4.1.1
pytest-json-report==1.5.0
python-dotenv==1.0.1
loguru==0.7.2
streamlit==1.40.0
pandas==2.2.3
plotly==5.24.1

pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
addopts = -v -s --tb=short

config/invoice_data.py
class InvoiceDefaults:
COMMERCIAL_REGISTRATION = "1234567890"
VAT_NUMBER = "123456789012343"
POSTAL_CODE = "12345"
BUILDING_NUMBER = "1234"
PAYMENT_TYPE = "نقدى"
COUNTRY = "جده"
CITY = "الرياض"
PROJECT = None
FORCE_COST_CENTER = True
UNCHECK_AUTO_VOUCHER = True

12. Dashboard
الملف الرئيسي: dashboard/app.py
التشغيل: streamlit run dashboard/app.py

الصفحات
الصفحة	الوصف
🏠 app.py	الرئيسية + Live Status
🏃 1_Run_Tests	تشغيل الاختبارات + إيميل
📊 2_Reports	تقارير + Date Filter
📸 3_Screenshots	معرض الصور
🔍 4_Compare	مقارنة تشغيلين
⏰ 5_Schedule	جدولة تلقائية
📧 6_Email	إعدادات الإيميل
الميزات
Dark/Light Mode Toggle

Live Status Indicator

Progress Bar

Charts تفاعلية

Date Range Filter

13. مشاكل معروفة وحلولها
المشكلة	السبب	الحل
element click intercepted	Preloader	JS click
السعر يفضل 0.0000	send_keys فشل	JS value assignment
TomlDecodeError	BOM في config	UTF8Encoding.new($false)
StreamlitPageNotFoundError	st.page_link بإيموجي	التنقل التلقائي
SweetAlert مش بيظهر	timeout قصير	handle_all_swals بحلقة
use_container_width warning	API قديم	تجاهل
Application Control Policy	Windows Security	إعادة تشغيل / Unblock-File
DNS مبيعرفش msedgedriver	شبكة	ChromeDriver محلي
14. الحالة النهائية
المكون	الحالة
Framework	✅
اختبار تسجيل دخول	✅
اختبار فاتورة بيع	✅
Dashboard	✅
تقارير	✅
إيميل	✅ (يحتاج إعداد)
جدولة	✅ (يحتاج Windows Task Scheduler)
15. الخطوات القادمة
تحسينات مقترحة
⚡ تحسين الأداء (من 2:33 لـ 1:30)

🧪 اختبارات جديدة (فاتورة شراء، تقرير مبيعات)

📊 تقارير Allure

🌐 CI/CD (GitHub Actions)

🎥 Video Recording (Playwright)

📱 Slack Notifications

16. كيف تستخدم هذا الملف
في شات جديد:

أرفق هذا الملف (PROJECT_SUMMARY.md)

اكتب: "أكمل من هنا، الحالة: اختبار الفاتورة يعمل بنجاح"

حدد الهدف الجديد

للمطور الجديد:

اقرأ الأقسام 1-4 (نظرة عامة)

شوف قسم 5 (الاختبارات)

اتبع قسم 10 (الأوامر)

آخر تحديث: 2026-10-05
الحالة: ✅ الفاتورة بتتحفظ بنجاح
الوقت: 2:33 دقيقة

text

---

## 📄 الخطوة 4: احفظ الملف

في Notepad:
1. اضغط **Ctrl + S** (Save)
2. اقفل الـ Notepad

**الملف اتحفظ!** ✅

---

## ✅ الخطوة 5: تأكد إن الملف اتعمل

في PowerShell، اكتب:

```powershell
dir PROJECT_SUMMARY.md
لو ظهرلك الملف → تمام! ✅

افتحه بـ Notepad للتأكد:

powershell
notepad PROJECT_SUMMARY.md