"""
Settings helper - Site config + Users (Handles BOM)
"""
import json
import hashlib
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
SITE_CONFIG = CONFIG_DIR / "site_config.json"
USERS_FILE = CONFIG_DIR / "users.json"
UPLOADS_DIR = BASE_DIR / "web" / "static" / "uploads"


def _load_json(path, default=None):
    """Load JSON with BOM support"""
    if not path.exists():
        return default
    try:
        # Try UTF-8 first
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (UnicodeDecodeError, json.JSONDecodeError):
        pass
    try:
        # Fallback: UTF-8-SIG (handles BOM)
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception as e:
        print(f"[settings] Error loading {path}: {e}")
        return default


def _save_json(path, data):
    """Save JSON without BOM"""
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(data, ensure_ascii=False, indent=2)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ==================== Site Config ====================
def load_site_config():
    default = {
        "site_name_ar": "أتمتة اختبارات ERP",
        "site_name_en": "ERP Test Automation",
        "company_name_ar": "",
        "company_name_en": "",
        "company_address": "",
        "company_phone": "",
        "company_email": "",
        "logo_filename": "",
        "favicon_filename": "",
    }
    data = _load_json(SITE_CONFIG, {})
    return {**default, **(data or {})}


def save_site_config(config):
    config["updated_at"] = datetime.now().isoformat()
    _save_json(SITE_CONFIG, config)


# ==================== Users ====================
def _hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def load_users():
    data = _load_json(USERS_FILE, {"users": []})
    users = (data or {}).get("users", [])

    # لو مفيش مستخدمين، اعمل admin افتراضي
    if not users:
        default_user = {
            "id": "u_admin",
            "username": "admin",
            "password_hash": _hash_password("password"),
            "full_name": "Administrator",
            "role": "admin",
            "active": True,
            "created_at": datetime.now().isoformat(),
        }
        users = [default_user]
        save_users(users)

    return users


def save_users(users):
    _save_json(USERS_FILE, {"users": users})


def get_user(username):
    for u in load_users():
        if u.get("username") == username:
            return u
    return None


def verify_password(username, password):
    user = get_user(username)
    if not user or not user.get("active", True):
        return None
    if user.get("password_hash") == _hash_password(password):
        return user
    return None


def add_user(username, password, full_name="", role="user"):
    users = load_users()
    if any(u.get("username") == username for u in users):
        return False, "اسم المستخدم موجود بالفعل"

    new_user = {
        "id": f"u_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "username": username,
        "password_hash": _hash_password(password),
        "full_name": full_name or username,
        "role": role,
        "active": True,
        "created_at": datetime.now().isoformat(),
    }
    users.append(new_user)
    save_users(users)
    return True, new_user


def update_user(user_id, **kwargs):
    users = load_users()
    for u in users:
        if u.get("id") == user_id:
            if kwargs.get("password"):
                u["password_hash"] = _hash_password(kwargs["password"])
            if "full_name" in kwargs:
                u["full_name"] = kwargs["full_name"]
            if "role" in kwargs:
                u["role"] = kwargs["role"]
            if "active" in kwargs:
                u["active"] = kwargs["active"]
            save_users(users)
            return True
    return False


def delete_user(user_id):
    users = load_users()
    new_users = [u for u in users if u.get("id") != user_id]
    if len(new_users) == len(users):
        return False
    save_users(new_users)
    return True


def get_uploads_dir():
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    return UPLOADS_DIR


# ==================== Email Config ====================
EMAIL_CONFIG_FILE = CONFIG_DIR / "email_config.json"


def load_email_config():
    default = {
        "enabled": False,
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": "",
        "sender_password": "",
        "recipients": [],
        "notify_on": "failure",
    }
    data = _load_json(EMAIL_CONFIG_FILE, {}) or {}
    return {**default, **data}


def save_email_config(config):
    old = load_email_config()
    if not config.get("sender_password"):
        config["sender_password"] = old.get("sender_password", "")
    config["updated_at"] = datetime.now().isoformat()
    _save_json(EMAIL_CONFIG_FILE, config)
    return True

