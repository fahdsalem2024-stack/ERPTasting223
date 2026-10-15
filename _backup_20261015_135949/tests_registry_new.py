"""
Tests Registry — كل الاختبارات المتاحة
- نوع: full (اختبار كامل) / smoke (اختبار شاشة)
"""


class TestsRegistry:
    """سجل الاختبارات"""

    TESTS = [
        # ===== الحسابات العامة =====
        {
            "id": "cash_receipt_full",
            "module_key": "general_accounting",
            "page_key": "cash_receipt",
            "type": "full",
            "name_ar": "سند القبض - كامل",
            "name_en": "Cash Receipt - Full",
            "icon": "💵",
            "test_path": "tests/functional/test_04_cash_receipt_voucher.py::test_full_cash_receipt_voucher_flow",
            "duration_estimate": 120,
            "tags": ["full", "accounting"],
            "available": True,
        },
        {
            "id": "journal_entries_smoke",
            "module_key": "general_accounting",
            "page_key": "journal_entries",
            "type": "smoke",
            "name_ar": "قيود التسوية اليدوية",
            "name_en": "Manual Journal Entries",
            "icon": "📝",
            "test_path": "tests/functional/test_09_general_accounting_smoke.py::test_individual_module_smoke[journal_entries]",
            "duration_estimate": 15,
            "tags": ["smoke", "accounting"],
            "available": True,
        },
        {
            "id": "expense_request_smoke",
            "module_key": "general_accounting",
            "page_key": "expense_request",
            "type": "smoke",
            "name_ar": "طلب صرف",
            "name_en": "Expense Request",
            "icon": "💸",
            "test_path": "tests/functional/test_09_general_accounting_smoke.py::test_individual_module_smoke[expense_request]",
            "duration_estimate": 15,
            "tags": ["smoke", "accounting"],
            "available": True,
        },
        {
            "id": "cash_issue_smoke",
            "module_key": "general_accounting",
            "page_key": "cash_issue",
            "type": "smoke",
            "name_ar": "سند الدفع",
            "name_en": "Cash Issue Voucher",
            "icon": "💰",
            "test_path": "tests/functional/test_09_general_accounting_smoke.py::test_individual_module_smoke[cash_issue]",
            "duration_estimate": 15,
            "tags": ["smoke", "accounting"],
            "available": True,
        },
        {
            "id": "cash_transfers_smoke",
            "module_key": "general_accounting",
            "page_key": "cash_transfers",
            "type": "smoke",
            "name_ar": "التحويلات المالية",
            "name_en": "Cash Transfers",
            "icon": "🔄",
            "test_path": "tests/functional/test_09_general_accounting_smoke.py::test_individual_module_smoke[cash_transfers]",
            "duration_estimate": 15,
            "tags": ["smoke", "accounting"],
            "available": True,
        },
        {
            "id": "inventory_boxes_smoke",
            "module_key": "general_accounting",
            "page_key": "inventory_boxes",
            "type": "smoke",
            "name_ar": "جرد الصناديق",
            "name_en": "Inventory Boxes",
            "icon": "📦",
            "test_path": "tests/functional/test_09_general_accounting_smoke.py::test_individual_module_smoke[inventory_boxes]",
            "duration_estimate": 15,
            "tags": ["smoke", "accounting"],
            "available": True,
        },
        {
            "id": "notifications_smoke",
            "module_key": "general_accounting",
            "page_key": "notifications",
            "type": "smoke",
            "name_ar": "الإشعارات",
            "name_en": "Notifications",
            "icon": "🔔",
            "test_path": "tests/functional/test_09_general_accounting_smoke.py::test_individual_module_smoke[notifications]",
            "duration_estimate": 15,
            "tags": ["smoke", "accounting"],
            "available": True,
        },
        {
            "id": "treasury_financing_smoke",
            "module_key": "general_accounting",
            "page_key": "treasury_financing",
            "type": "smoke",
            "name_ar": "تمويل الصناديق",
            "name_en": "Treasury Financing",
            "icon": "🏦",
            "test_path": "tests/functional/test_09_general_accounting_smoke.py::test_individual_module_smoke[treasury_financing]",
            "duration_estimate": 15,
            "tags": ["smoke", "accounting"],
            "available": True,
        },
        {
            "id": "utility_bill_smoke",
            "module_key": "general_accounting",
            "page_key": "utility_bill",
            "type": "smoke",
            "name_ar": "فاتورة خدمية",
            "name_en": "Utility Bill",
            "icon": "🧾",
            "test_path": "tests/functional/test_09_general_accounting_smoke.py::test_individual_module_smoke[utility_bill]",
            "duration_estimate": 15,
            "tags": ["smoke", "accounting"],
            "available": True,
        },
        {
            "id": "advance_payment_request_smoke",
            "module_key": "general_accounting",
            "page_key": "advance_payment_request",
            "type": "smoke",
            "name_ar": "طلب دفعة مقدمة",
            "name_en": "Advance Payment Request",
            "icon": "💳",
            "test_path": "tests/functional/test_09_general_accounting_smoke.py::test_individual_module_smoke[advance_payment_request]",
            "duration_estimate": 15,
            "tags": ["smoke", "accounting"],
            "available": True,
        },
        {
            "id": "advance_payment_invoice_smoke",
            "module_key": "general_accounting",
            "page_key": "advance_payment_invoice",
            "type": "smoke",
            "name_ar": "فاتورة دفعة مقدمة",
            "name_en": "Advance Payment Invoice",
            "icon": "📄",
            "test_path": "tests/functional/test_09_general_accounting_smoke.py::test_individual_module_smoke[advance_payment_invoice]",
            "duration_estimate": 15,
            "tags": ["smoke", "accounting"],
            "available": True,
        },
        {
            "id": "expenses_smoke",
            "module_key": "general_accounting",
            "page_key": "expenses",
            "type": "smoke",
            "name_ar": "تصفية العهد",
            "name_en": "Expenses Settlement",
            "icon": "💼",
            "test_path": "tests/functional/test_09_general_accounting_smoke.py::test_individual_module_smoke[expenses]",
            "duration_estimate": 15,
            "tags": ["smoke", "accounting"],
            "available": True,
        },

        # ===== حركات المبيعات =====
        {
            "id": "sales_invoice_full",
            "module_key": "sales",
            "page_key": "sales_invoice",
            "type": "full",
            "name_ar": "فاتورة البيع - كامل",
            "name_en": "Sales Invoice - Full",
            "icon": "🧾",
            "test_path": "tests/functional/test_03_sales_invoice.py::test_full_sales_invoice_flow",
            "duration_estimate": 151,
            "tags": ["full", "sales"],
            "available": True,
        },
        {
            "id": "sales_quotation_smoke",
            "module_key": "sales",
            "page_key": "sales_quotation",
            "type": "smoke",
            "name_ar": "عرض سعر بيع",
            "name_en": "Sales Quotation",
            "icon": "📋",
            "test_path": "tests/functional/test_09_general_accounting_smoke.py::test_individual_module_smoke[sales_quotation]",
            "duration_estimate": 15,
            "tags": ["smoke", "sales"],
            "available": True,
        },
        {
            "id": "sales_order_smoke",
            "module_key": "sales",
            "page_key": "sales_order",
            "type": "smoke",
            "name_ar": "أوامر البيع",
            "name_en": "Sales Orders",
            "icon": "📦",
            "test_path": "tests/functional/test_09_general_accounting_smoke.py::test_individual_module_smoke[sales_order]",
            "duration_estimate": 15,
            "tags": ["smoke", "sales"],
            "available": True,
        },
        {
            "id": "sales_return_smoke",
            "module_key": "sales",
            "page_key": "sales_return",
            "type": "smoke",
            "name_ar": "مرتجع البيع",
            "name_en": "Sales Return",
            "icon": "↩️",
            "test_path": "tests/functional/test_09_general_accounting_smoke.py::test_individual_module_smoke[sales_return]",
            "duration_estimate": 15,
            "tags": ["smoke", "sales"],
            "available": True,
        },
    ]

    @classmethod
    def get_all(cls):
        return [t for t in cls.TESTS if t.get("available", True)]

    @classmethod
    def get_by_id(cls, test_id):
        for t in cls.TESTS:
            if t["id"] == test_id:
                return t
        return None

    @classmethod
    def get_by_type(cls, test_type):
        return [t for t in cls.get_all() if t["type"] == test_type]

    @classmethod
    def get_by_module(cls, module_key):
        return [t for t in cls.get_all() if t["module_key"] == module_key]

    @classmethod
    def get_by_page(cls, page_key):
        return [t for t in cls.get_all() if t["page_key"] == page_key]

    @classmethod
    def get_stats(cls):
        tests = cls.get_all()
        return {
            "total": len(tests),
            "full": len([t for t in tests if t["type"] == "full"]),
            "smoke": len([t for t in tests if t["type"] == "smoke"]),
            "modules": len(set(t["module_key"] for t in tests)),
        }



    @classmethod
    def get_all_with_paths(cls, lang="ar"):
        """
        يرجّع كل الاختبارات مع مسارين:
        - full_path: مسار الاختبار الكامل
        - smoke_path: مسار الـ Smoke Test
        """
        result = []
        for t in cls.get_all():
            localized = cls.localize(t, lang)

            # full_path = test_path الحالي
            full_path = t["test_path"]

            # smoke_path = مسار Smoke
            page_key = t.get("page_key", "")
            smoke_path = f"tests/functional/test_09_general_accounting_smoke.py::test_individual_module_smoke[{page_key}]"

            result.append({
                **localized,
                "full_path": full_path,
                "smoke_path": smoke_path,
            })
        return result

    @classmethod
    def localize(cls, test, lang="ar"):
        if lang == "en":
            return {
                **test,
                "name": test.get("name_en", test.get("name_ar", "")),
            }
        return {
            **test,
            "name": test.get("name_ar", ""),
        }

    @classmethod
    def get_all_localized(cls, lang="ar"):
        return [cls.localize(t, lang) for t in cls.get_all()]