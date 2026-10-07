"""
Test Sites Helper - Manage test site profiles (URLs + credentials)
"""
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
TEST_SITES_FILE = CONFIG_DIR / "test_sites.json"


def _load_json(path, default=None):
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (UnicodeDecodeError, json.JSONDecodeError):
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                return json.load(f)
        except Exception:
            return default
    except Exception:
        return default


def _save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(data, ensure_ascii=False, indent=2)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def load_all():
    data = _load_json(TEST_SITES_FILE, {"active_profile": None, "profiles": []})
    return data or {"active_profile": None, "profiles": []}


def get_active_profile():
    data = load_all()
    active_id = data.get("active_profile")
    if not active_id:
        return None
    for p in data.get("profiles", []):
        if p.get("id") == active_id:
            return p
    return None


def add_profile(name, base_url, username, password, notes=""):
    data = load_all()
    new_id = "p_" + datetime.now().strftime("%Y%m%d%H%M%S")
    profile = {
        "id": new_id,
        "name": name,
        "base_url": base_url.rstrip("/"),
        "username": username,
        "password": password,
        "notes": notes,
        "created_at": datetime.now().isoformat(),
    }
    data.setdefault("profiles", []).append(profile)
    if not data.get("active_profile"):
        data["active_profile"] = new_id
    _save_json(TEST_SITES_FILE, data)
    return True, profile


def update_profile(profile_id, **kwargs):
    data = load_all()
    for p in data.get("profiles", []):
        if p.get("id") == profile_id:
            if "name" in kwargs:
                p["name"] = kwargs["name"]
            if "base_url" in kwargs:
                p["base_url"] = kwargs["base_url"].rstrip("/")
            if "username" in kwargs:
                p["username"] = kwargs["username"]
            if "password" in kwargs and kwargs["password"]:
                p["password"] = kwargs["password"]
            if "notes" in kwargs:
                p["notes"] = kwargs["notes"]
            p["updated_at"] = datetime.now().isoformat()
            _save_json(TEST_SITES_FILE, data)
            return True, p
    return False, "Profile not found"


def delete_profile(profile_id):
    data = load_all()
    profiles = data.get("profiles", [])
    new_profiles = [p for p in profiles if p.get("id") != profile_id]
    if len(new_profiles) == len(profiles):
        return False, "Profile not found"
    data["profiles"] = new_profiles
    if data.get("active_profile") == profile_id:
        data["active_profile"] = new_profiles[0]["id"] if new_profiles else None
    _save_json(TEST_SITES_FILE, data)
    return True, "Deleted"


def set_active_profile(profile_id):
    data = load_all()
    for p in data.get("profiles", []):
        if p.get("id") == profile_id:
            data["active_profile"] = profile_id
            _save_json(TEST_SITES_FILE, data)
            return True
    return False
