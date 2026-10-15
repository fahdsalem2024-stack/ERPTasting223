"""
Cash Receipt Voucher — القيم الافتراضية
عدّل القيم دي حسب الحقول اللي هتديهالي
"""


class CashReceiptDefaults:
    # ===== الحقول الإجبارية =====
    # ⚠️ عدّل القيم دي حسب ما تحب
    BRANCH = "الفرع الرئيسي - 1"          # الفرع
    CUSTOMER = "588897991 - محمد جدة"     # العميل (مؤقتًا زي فاتورة البيع)
    AMOUNT = "10000"                      # المبلغ
    PAYMENT_METHOD = "نقدى"               # طريقة الدفع
    COST_CENTER = "سند القبض - 1"         # مركز التكلفة
    EXCHANGE_RATE = "ريال سعودي - SAR"    # سعر الصرف
    CURRENCY = "1"                        # العملة

    # ===== حقول اختيارية =====
    DOCUMENT_NUMBER = ""                  # رقم المستند (اتركه فاضي = تلقائي)
    SERIAL = ""                           # السيريال
    REFERENCE_NUMBER = ""                 # الرقم المرجعي
    MANUAL_NUMBER = ""                    # الرقم اليدوي
    NOTES = "اختبار سند قبض آلي"          # ملاحظات
    DESCRIPTION = "اختبار سند قبض آلي"    # الشروح

    # ===== Checkboxes =====
    PREPAID_PAYMENTS = False              # الدفعات مقدمة
    STOP_CURRENCY_CONVERSION = False      # إيقاف التحويل النقدي
    SELECT_INVOICES = False               # تحديد الفواتير

    # ===== إعدادات =====
    FORCE_COST_CENTER = True              # إعادة اختيار مركز التكلفة
    WAIT_AFTER_SAVE = 3                   # ثواني انتظار بعد الحفظ