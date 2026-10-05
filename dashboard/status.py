"""
Live Status utilities
"""
import json
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "reports" / "results"
LOCK_FILE = BASE_DIR / "reports" / ".running"


def is_test_running():
    """Check if a test is currently running"""
    if not LOCK_FILE.exists():
        return False

    try:
        with open(LOCK_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        started_at = datetime.fromisoformat(data.get("started_at", ""))
        # If test started more than 15 minutes ago, consider it stale
        if datetime.now() - started_at > timedelta(minutes=15):
            return False
        return True
    except Exception:
        return False


def get_running_info():
    """Get info about currently running test"""
    if not LOCK_FILE.exists():
        return None
    try:
        with open(LOCK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def start_test_lock(test_name):
    """Create lock file when test starts"""
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "test_name": test_name,
        "started_at": datetime.now().isoformat(),
    }
    with open(LOCK_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def stop_test_lock():
    """Remove lock file when test ends"""
    if LOCK_FILE.exists():
        LOCK_FILE.unlink()


def render_status_indicator():
    """Render live status indicator"""
    import streamlit as st

    running = is_test_running()

    if running:
        info = get_running_info()
        test_name = info.get("test_name", "اختبار") if info else "اختبار"
        started_at = info.get("started_at", "")[:19] if info else ""

        st.markdown(f"""
        <div style="
            display: inline-flex; align-items: center; gap: 10px;
            padding: 8px 16px; background: rgba(245, 158, 11, 0.1);
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-radius: 999px;
        ">
            <span style="
                width: 8px; height: 8px; border-radius: 50%;
                background: #f59e0b;
                animation: pulse 1s infinite;
                box-shadow: 0 0 10px #f59e0b;
            "></span>
            <span style="color: #f59e0b; font-weight: 600; font-size: 0.85rem;">
                🔄 جاري تشغيل: {test_name}
            </span>
        </div>
        <style>
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; transform: scale(1); }}
                50% {{ opacity: 0.5; transform: scale(1.3); }}
            }}
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="
            display: inline-flex; align-items: center; gap: 10px;
            padding: 8px 16px; background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 999px;
        ">
            <span style="
                width: 8px; height: 8px; border-radius: 50%;
                background: #10b981;
                box-shadow: 0 0 8px #10b981;
            "></span>
            <span style="color: #10b981; font-weight: 600; font-size: 0.85rem;">
                🟢 النظام جاهز
            </span>
        </div>
        """, unsafe_allow_html=True)
