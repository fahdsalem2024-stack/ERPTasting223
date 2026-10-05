"""
Test Registry - Bilingual
"""


class TestRegistry:
    TESTS = [
        {
            "id": "sales_invoice_full",
            "name": "فاتورة بيع كاملة",
            "name_en": "Full Sales Invoice",
            "icon": "🧾",
            "category": "Sales",
            "description": "إنشاء فاتورة بيع كاملة (تسجيل دخول → صنف → حفظ)",
            "description_en": "Create complete sales invoice (login → item → save)",
            "test_path": "tests/functional/test_03_sales_invoice.py::test_full_sales_invoice_flow",
            "duration_estimate": 140,
            "tags": ["smoke", "sales", "e2e"],
            "steps": [
                "تسجيل الدخول",
                "فتح فاتورة بيع جديدة",
                "اختيار عميل",
                "إضافة صنف 'فلتر تكييف'",
                "كتابة السعر 10000",
                "ملء الحقول الإجبارية",
                "إلغاء سند الصرف",
                "حفظ الفاتورة",
                "التحقق من النجاح"
            ],
            "steps_en": [
                "Login",
                "Open new sales invoice",
                "Select customer",
                "Add item 'Filter AC'",
                "Enter price 10000",
                "Fill required fields",
                "Uncheck receipt voucher",
                "Save invoice",
                "Verify success"
            ]
        }
    ]

    @classmethod
    def get_all(cls):
        return cls.TESTS

    @classmethod
    def get_by_id(cls, test_id):
        for t in cls.TESTS:
            if t["id"] == test_id:
                return t
        return None

    @classmethod
    def get_categories(cls):
        return sorted(set(t["category"] for t in cls.TESTS))

    @classmethod
    def get_by_category(cls, category):
        return [t for t in cls.TESTS if t["category"] == category]

    @classmethod
    def localize(cls, test, lang="ar"):
        """Return a localized copy of the test"""
        if lang == "en":
            return {
                **test,
                "name": test.get("name_en", test["name"]),
                "description": test.get("description_en", test["description"]),
                "steps": test.get("steps_en", test["steps"]),
            }
        return test

    @classmethod
    def get_all_localized(cls, lang="ar"):
        return [cls.localize(t, lang) for t in cls.TESTS]
