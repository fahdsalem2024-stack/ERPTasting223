"""
Tunnel Helper - Manage public tunnel URLs (Cloudflare/ngrok)
"""
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
TUNNEL_FILE = CONFIG_DIR / "tunnel_config.json"


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


def load_config():
    default = {
        "flask_url": "",
        "vnc_url": "",
        "provider": "cloudflare",
        "updated_at": "",
    }
    data = _load_json(TUNNEL_FILE, {}) or {}
    return {**default, **data}


def save_config(flask_url, vnc_url, provider="cloudflare"):
    config = {
        "flask_url": flask_url.strip().rstrip("/"),
        "vnc_url": vnc_url.strip().rstrip("/"),
        "provider": provider,
        "updated_at": datetime.now().isoformat(),
    }
    _save_json(TUNNEL_FILE, config)
    return config


def get_vnc_full_url():
    """يرجع رابط noVNC كامل جاهز للاستخدام في iframe"""
    config = load_config()
    vnc = config.get("vnc_url", "").rstrip("/")
    if not vnc:
        return "http://localhost:7900/vnc.html?autoconnect=true&resize=scale&password=secret"
    return f"{vnc}/vnc.html?autoconnect=true&resize=scale&password=secret&reconnect=true&reconnect_delay=2000"


def get_flask_url():
    return load_config().get("flask_url", "")
