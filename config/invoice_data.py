"""
قيم ثابتة للفاتورة
"""

class InvoiceDefaults:
    # حقول نصية إجبارية
    COMMERCIAL_REGISTRATION = "1234567890"
    VAT_NUMBER = "123456789012343"
    POSTAL_CODE = "12345"
    BUILDING_NUMBER = "1234"

    # حقول Select2
    PAYMENT_TYPE = "نقدى"
    COUNTRY = "جده"
    CITY = "الرياض"
    PROJECT = None
    FORCE_COST_CENTER = True

    # إعدادات
    UNCHECK_AUTO_VOUCHER = True
    ALLOW_EMPTY_COUNTRY_CITY = True
