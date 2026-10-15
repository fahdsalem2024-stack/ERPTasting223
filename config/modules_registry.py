"""
Modules Registry — كل المديولات والشاشات
"""
from config.general_accounting_modules import GeneralAccountingModules


class ModulesRegistry:
    """كل المديولات في النظام"""

    MODULES = {
        "general_accounting": {
            "name_ar": "الحسابات العامة",
            "name_en": "General Accounting",
            "icon": "📊",
            "pages": GeneralAccountingModules.MODULES,
        },        "sales": {
            "name_ar": "حركات المبيعات",
            "name_en": "Sales Transactions",
            "icon": "🛒",
            "pages": {
                "sales_quotation": {
                    "name_ar": "عرض سعر بيع",
                    "name_en": "Sales Quotation",
                    "url": "/SalesQuotation",
                },
                "sales_order": {
                    "name_ar": "أوامر البيع",
                    "name_en": "Sales Order",
                    "url": "/SalesOrder",
                },
                "pre_sales_invoice": {
                    "name_ar": "فاتورة مبدئية",
                    "name_en": "Pre Sales Invoice",
                    "url": "/PreSalesInvoice",
                },
                "sales_order_request": {
                    "name_ar": "طلب أمر بيع",
                    "name_en": "Sales Order Request",
                    "url": "/SalesOrderRequest",
                },
                "sales_invoices_delivery": {
                    "name_ar": "تسليم الفواتير",
                    "name_en": "Sales Invoices Delivery",
                    "url": "/SalesInvoicesDelivery",
                },
                "advance_payment_invoice_sales": {
                    "name_ar": "فاتورة دفعة مقدمة",
                    "name_en": "Advance Payment Invoice",
                    "url": "/AdvancePaymentInvoice",
                },
                "sales_invoice": {
                    "name_ar": "فواتير البيع",
                    "name_en": "Sales Invoice",
                    "url": "/SalesInvoice",
                },
                "sales_return": {
                    "name_ar": "مرتجع البيع",
                    "name_en": "Sales Return",
                    "url": "/SalesReturn",
                },
                "purchase_invoice_packing_list": {
                    "name_ar": "قائمة الشحنات",
                    "name_en": "Packing List",
                    "url": "/PurchaseInvoicePackingList",
                },
                "items_offers": {
                    "name_ar": "عروض الأصناف",
                    "name_en": "Items Offers",
                    "url": "/ItemsOffers",
                },
                "transfer_client_representative": {
                    "name_ar": "نقل مندوب عميل",
                    "name_en": "Transfer Client Representative",
                    "url": "/TransferClientRepresentative",
                },
                "black_list": {
                    "name_ar": "القائمة السوداء",
                    "name_en": "Black List",
                    "url": "/BlackList",
                },
            },
        },
        # مديولات تانية — تتضاف بعدين
        # "sales": {...},
        # "inventory": {...},
    }

    @classmethod
    def get_all(cls):
        return cls.MODULES

    @classmethod
    def get_module(cls, module_key):
        return cls.MODULES.get(module_key)

    @classmethod
    def get_page(cls, module_key, page_key):
        module = cls.get_module(module_key)
        if module:
            return module["pages"].get(page_key)
        return None

    @classmethod
    def get_all_pages(cls):
        """يرجّع كل الصفحات مسطحة"""
        pages = []
        for mod_key, mod_info in cls.MODULES.items():
            for page_key, page_info in mod_info["pages"].items():
                pages.append({
                    "module_key": mod_key,
                    "module_name_ar": mod_info["name_ar"],
                    "module_name_en": mod_info["name_en"],
                    "module_icon": mod_info["icon"],
                    "page_key": page_key,
                    **page_info,
                })
        return pages

    @classmethod
    def get_localized(cls, lang="ar"):
        """يرجّع المديولات مع التسميات المترجمة"""
        result = {}
        for mod_key, mod_info in cls.MODULES.items():
            localized_pages = {}
            for page_key, page_info in mod_info["pages"].items():
                localized_pages[page_key] = {
                    **page_info,
                    "name": page_info.get(f"name_{lang}", page_info.get("name_ar", "")),
                    "full_name": f"{page_info.get(f'name_{lang}', page_info.get('name_ar'))}",
                }
            result[mod_key] = {
                "name": mod_info.get(f"name_{lang}", mod_info["name_ar"]),
                "icon": mod_info["icon"],
                "pages": localized_pages,
            }
        return result