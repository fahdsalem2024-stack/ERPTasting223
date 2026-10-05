"""
Scheduled Runs Page
"""
import sys
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
import pandas as pd
from config.test_registry import TestRegistry
from dashboard.theme import init_theme, apply_theme, theme_toggle_button

st.set_page_config(page_title="Schedule", page_icon="⏰", layout="wide")
init_theme()
apply_theme()

SCHEDULES_DIR = BASE_DIR / "config" / "schedules"
SCHEDULES_DIR.mkdir(parents=True, exist_ok=True)
SCHEDULES_FILE = SCHEDULES_DIR / "schedules.json"


def load_schedules():
    if not SCHEDULES_FILE.exists():
        return []
    try:
        with open(SCHEDULES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_schedules(schedules):
    with open(SCHEDULES_FILE, "w", encoding="utf-8") as f:
        json.dump(schedules, f, ensure_ascii=False, indent=2)


tests = TestRegistry.get_all()

st.title("⏰ الجدولة التلقائية")
st.caption("جدول تشغيل الاختبارات تلقائياً")
st.markdown("---")

# ==================== Info ====================
st.info("""
**ملاحظة:** الجدولة الحقيقية بتتم عبر **Windows Task Scheduler**.
هنا بتقدر تحفظ الإعدادات، وبعدين نسخة **.bat** هنعملها تشغل المهمة.
""")

st.markdown("---")

# ==================== Create Schedule ====================
st.subheader("➕ إنشاء جدولة جديدة")

with st.form("new_schedule"):
    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("اسم الجدولة", placeholder="مثلاً: تشغيل يومي صباحاً")
        test_options = {t['id']: f"{t['icon']} {t['name']}" for t in tests}
        selected_test_id = st.selectbox("الاختبار", list(test_options.keys()), format_func=lambda k: test_options[k])

    with col2:
        time_input = st.time_input("الوقت")
        frequency = st.selectbox("التكرار", ["يومياً", "أسبوعياً", "شهرياً", "مرة واحدة"])

    enabled = st.checkbox("مفعّل", value=True)

    submitted = st.form_submit_button("💾 حفظ الجدولة", use_container_width=True)

    if submitted and name:
        schedules = load_schedules()
        new_schedule = {
            "id": f"sch_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "name": name,
            "test_id": selected_test_id,
            "time": time_input.strftime("%H:%M"),
            "frequency": frequency,
            "enabled": enabled,
            "created_at": datetime.now().isoformat(),
        }
        schedules.append(new_schedule)
        save_schedules(schedules)
        st.success(f"✅ تم حفظ الجدولة: {name}")
        st.rerun()

st.markdown("---")

# ==================== Existing Schedules ====================
st.subheader("📋 الجدولات الحالية")

schedules = load_schedules()

if not schedules:
    st.info("📭 لا توجد جدولات بعد")
else:
    for sch in schedules:
        test = TestRegistry.get_by_id(sch['test_id'])
        test_name = f"{test['icon']} {test['name']}" if test else sch['test_id']

        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

            with col1:
                st.markdown(f"### {sch['name']}")
                st.caption(f"🧪 {test_name}")

            with col2:
                st.markdown(f"**⏰ {sch['time']}**")
                st.caption(sch['frequency'])

            with col3:
                if sch['enabled']:
                    st.success("✅ مفعّل")
                else:
                    st.warning("⏸️ موقوف")

            with col4:
                if st.button("🗑️", key=f"del_{sch['id']}"):
                    schedules = [s for s in schedules if s['id'] != sch['id']]
                    save_schedules(schedules)
                    st.rerun()

st.markdown("---")

# ==================== Generate BAT ====================
if schedules:
    st.subheader("🔧 توليد ملف Task Scheduler")

    if st.button("📄 توليد ملف .bat", use_container_width=True):
        enabled_schedules = [s for s in schedules if s['enabled']]

        bat_content = "@echo off\n"
        bat_content += "REM ERP Test Automation - Scheduled Runs\n"
        bat_content += f"REM Generated: {datetime.now().isoformat()}\n\n"
        bat_content += f'cd /d "{BASE_DIR}"\n'
        bat_content += 'call venv\\Scripts\\activate.bat\n\n'

        for sch in enabled_schedules:
            test = TestRegistry.get_by_id(sch['test_id'])
            if not test:
                continue
            bat_content += f"REM === {sch['name']} ({sch['time']} {sch['frequency']}) ===\n"
            bat_content += f'python -m pytest {test["test_path"]} -v\n\n'

        bat_content += "pause\n"

        bat_file = BASE_DIR / "run_scheduled.bat"
        with open(bat_file, "w", encoding="utf-8") as f:
            f.write(bat_content)

        st.success(f"✅ تم حفظ الملف: `{bat_file}`")
        st.info("""
**الخطوة التالية:**
1. افتح **Task Scheduler** في Windows
2. اضغط **Create Basic Task**
3. اختار التكرار والوقت
4. **Action:** Start a program → اختار `run_scheduled.bat`
5. Save
        """)

        with st.expander("📄 معاينة الملف"):
            st.code(bat_content, language="batch")

with st.sidebar:
    theme_toggle_button()
