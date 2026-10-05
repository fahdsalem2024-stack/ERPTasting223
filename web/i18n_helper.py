"""
Translation helper - Handles UTF-8 with/without BOM
"""
import json
from pathlib import Path
from flask import session, has_request_context

I18N_DIR = Path(__file__).parent / "i18n"


def get_translations(lang):
    """Load translations from JSON - tries both UTF-8 and UTF-8-SIG"""
    if lang not in ["ar", "en"]:
        lang = "ar"

    file = I18N_DIR / f"{lang}.json"
    if not file.exists():
        print(f"[i18n] File not found: {file}")
        return {}

    # Try UTF-8 without BOM first
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except UnicodeDecodeError:
        pass
    except json.JSONDecodeError:
        pass

    # Fallback: try with UTF-8-SIG (handles BOM)
    try:
        with open(file, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception as e:
        print(f"[i18n] Error loading {file}: {e}")
        return {}


def get_current_lang():
    """Get current language from session"""
    try:
        if has_request_context():
            lang = session.get("lang", "ar")
            return lang if lang in ["ar", "en"] else "ar"
    except Exception:
        pass
    return "ar"


def t(key, default=None):
    """Translate key"""
    lang = get_current_lang()
    translations = get_translations(lang)

    if key in translations:
        return translations[key]

    # Fallback to other language
    other = "en" if lang == "ar" else "ar"
    other_trans = get_translations(other)
    if key in other_trans:
        return other_trans[key]

    return default or key


def get_dir():
    """Return text direction"""
    return "rtl" if get_current_lang() == "ar" else "ltr"
