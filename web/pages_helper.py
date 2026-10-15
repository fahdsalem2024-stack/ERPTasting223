"""
Pages Helper — قائمة المديولات والشاشات للموقع
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def get_modules(lang="ar"):
    """يرجّع كل المديولات"""
    try:
        from config.modules_registry import ModulesRegistry
        return ModulesRegistry.get_localized(lang)
    except Exception as e:
        print(f"[pages_helper] Error: {e}")
        return {}


def get_all_pages(lang="ar"):
    """يرجّع كل الصفحات مسطحة"""
    try:
        from config.modules_registry import ModulesRegistry
        modules = ModulesRegistry.get_localized(lang)
        pages = []
        for mod_key, mod_info in modules.items():
            for page_key, page_info in mod_info["pages"].items():
                pages.append({
                    "module_key": mod_key,
                    "module_name": mod_info["name"],
                    "module_icon": mod_info["icon"],
                    "page_key": page_key,
                    **page_info,
                })
        return pages
    except Exception as e:
        print(f"[pages_helper] Error: {e}")
        return []


def get_page(module_key, page_key, lang="ar"):
    """يرجّع شاشة واحدة"""
    try:
        from config.modules_registry import ModulesRegistry
        module = ModulesRegistry.get_module(module_key)
        if not module:
            return None
        page = module["pages"].get(page_key)
        if not page:
            return None
        return {
            "module_key": module_key,
            "module_name": module.get(f"name_{lang}", module["name_ar"]),
            "module_icon": module["icon"],
            "page_key": page_key,
            **page,
        }
    except Exception as e:
        print(f"[pages_helper] Error: {e}")
        return None


def get_smoke_test_path():
    """مسار Smoke Test"""
    return "tests/functional/test_09_general_accounting_smoke.py"