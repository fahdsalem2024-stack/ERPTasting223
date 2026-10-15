"""
الحسابات العامة — كل الشاشات
Smoke Tests: تفتح الشاشة + تعرض البيانات
"""


class GeneralAccountingModules:
    """قائمة كل شاشات الحسابات العامة"""

    MODULES = {
        "journal_entries": {
            "name_ar": "قيود التسوية اليدوية",
            "name_en": "Manual Journal Entries",
            "url": "/JournalEntries?type=1",
            "type": "list",
        },
        "cash_receipt": {
            "name_ar": "سند القبض",
            "name_en": "Cash Receipt Voucher",
            "url": "/CashReceiptVoucher",
            "type": "list",
        },
        "expense_request": {
            "name_ar": "طلب صرف",
            "name_en": "Expense Request",
            "url": "/ExpenseRequest",
            "type": "list",
        },
        "advance_payment_request": {
            "name_ar": "طلب دفعة مقدمة",
            "name_en": "Advance Payment Request",
            "url": "/RequestAdvancePayment",
            "type": "list",
        },
        "advance_payment_invoice": {
            "name_ar": "فاتورة دفعة مقدمة",
            "name_en": "Advance Payment Invoice",
            "url": "/AdvancePaymentInvoice",
            "type": "list",
        },
        "expenses": {
            "name_ar": "تصفية العهد",
            "name_en": "Expenses Settlement",
            "url": "/Expenses",
            "type": "list",
        },
        "cash_issue": {
            "name_ar": "سند الدفع",
            "name_en": "Cash Issue Voucher",
            "url": "/CashIssueVoucher",
            "type": "list",
        },
        "cash_transfers": {
            "name_ar": "التحويلات المالية",
            "name_en": "Cash Transfers",
            "url": "/CashTransfers",
            "type": "list",
        },
        "inventory_boxes": {
            "name_ar": "جرد الصناديق",
            "name_en": "Inventory Boxes",
            "url": "/InventoryBoxes",
            "type": "list",
        },
        "notifications": {
            "name_ar": "الإشعارات",
            "name_en": "Notifications",
            "url": "/Notifications",
            "type": "list",
        },
        "treasury_financing": {
            "name_ar": "تمويل الصناديق",
            "name_en": "Treasury & Custody Financing",
            "url": "/TreasuryAndCustodyFinancing",
            "type": "list",
        },
        "utility_bill": {
            "name_ar": "فاتورة خدمية",
            "name_en": "Utility Bill",
            "url": "/UtilityBill",
            "type": "list",
        },
    }

    @classmethod
    def get_all(cls):
        return cls.MODULES

    @classmethod
    def get_by_key(cls, key):
        return cls.MODULES.get(key)

    @classmethod
    def get_by_url(cls, url):
        for k, v in cls.MODULES.items():
            if v["url"] == url:
                return k, v
        return None, None

    @classmethod
    def count(cls):
        return len(cls.MODULES)