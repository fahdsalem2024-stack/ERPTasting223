"""
ERP Test Automation Dashboard
"""
import sys
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
import pandas as pd
from config.test_registry import TestRegistry
from dashboard.theme import init_theme, apply_theme, theme_toggle_button
from dashboard.status import render_status_indicator, is_test_running

st.set_page_config(
    page_title="ERP Test Automation",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_theme()
apply_theme()

tests = TestRegistry.get_all()
categories = TestRegistry.get_categories()

RESULTS_DIR = BASE_DIR / "reports" / "results"


@st.cache_data(ttl=5)
def load_recent_runs(limit=5):
    runs = []
    if not RESULTS_DIR.exists():
        return runs
    for f in sorted(RESULTS_DIR.glob("summary_*.json"), reverse=True)[:limit]:
        try:
            with open(f, "r", encoding="utf-8") as fp:
                runs.append(json.load(fp))
        except Exception:
            pass
    return runs


recent_runs = load_recent_runs()

# ==================== Header ====================
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🧪 ERP Test Automation")
    st.caption("منصة أتمتة اختبارات نظام ERP • Selenium + Pytest + Streamlit")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    render_status_indicator()

st.markdown("---")

# ==================== Auto-refresh (if test running) ====================
if is_test_running():
    st.info("🔄 فيه اختبار شغال حالياً. الصفحة بتتحدث تلقائياً كل 5 ثواني...")
    import time
    time.sleep(5)
    st.rerun()

# ==================== Live Stats ====================
st.subheader("📊 نظرة عامة")

col1, col2, col3, col4 = st.columns(4)

total_runs = len(recent_runs)
total_passed = sum(r.get("passed", 0) for r in recent_runs)
total_failed = sum(r.get("failed", 0) + r.get("errors", 0) for r in recent_runs)
success_rate = round((total_passed / (total_passed + total_failed) * 100) if (total_passed + total_failed) > 0 else 0, 1)

with col1:
    st.metric("🧪 الاختبارات", len(tests))
with col2:
    st.metric("📁 إجمالي التشغيلات", total_runs)
with col3:
    st.metric("✅ إجمالي ناجح", total_passed)
with col4:
    st.metric("📈 نسبة النجاح", f"{success_rate}%")

st.markdown("---")

# ==================== Tests Grid ====================
st.subheader("📋 الاختبارات المتاحة")

for test in tests:
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"### {test['icon']} {test['name']}")
            st.caption(test['description'])

            tags_html = " ".join([f"`{tag.upper()}`" for tag in test.get("tags", [])])
            if tags_html:
                st.markdown(tags_html)

        with col2:
            st.metric("المدة المتوقعة", f"{test['duration_estimate']} ث", label_visibility="collapsed")
            st.caption("⏱️ ثانية")

        with st.expander("📝 تفاصيل الخطوات"):
            st.markdown(f"**المسار:** `{test['test_path']}`")
            for i, step in enumerate(test.get("steps", []), 1):
                st.markdown(f"**{i}.** {step}")

st.markdown("---")

# ==================== Recent Runs ====================
if recent_runs:
    st.subheader("🕐 آخر التشغيلات")

    cols = st.columns(min(len(recent_runs), 5))
    for i, run in enumerate(recent_runs[:5]):
        with cols[i]:
            passed = run.get("passed", 0)
            failed = run.get("failed", 0) + run.get("errors", 0)
            duration = int(run.get("duration_seconds", 0))
            timestamp = run.get("timestamp", "")

            if len(timestamp) >= 13:
                time_str = f"{timestamp[9:11]}:{timestamp[11:13]}"
            else:
                time_str = timestamp

            with st.container(border=True):
                st.caption(f"⏰ {time_str}")
                if failed == 0 and passed > 0:
                    st.markdown(f"### ✅ {passed}")
                    st.caption(f"نجح • {duration} ث")
                else:
                    st.markdown(f"### ❌ {failed}")
                    st.caption(f"فشل • {duration} ث")

    st.markdown("---")

# ==================== Quick Guide ====================
st.subheader("🚀 كيف تبدأ؟")

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("#### 🏃 تشغيل الاختبارات")
        st.caption("اختر الاختبارات وشغلها من صفحة **Run Tests**")

with col2:
    with st.container(border=True):
        st.markdown("#### 📊 التقارير")
        st.caption("اعرض النتائج التفصيلية من صفحة **Reports**")

with col3:
    with st.container(border=True):
        st.markdown("#### 📸 الصور")
        st.caption("شوف لقطات الشاشة من صفحة **Screenshots**")

st.markdown("---")
st.caption("ERP Test Automation v3.0 • Powered by Streamlit + Selenium")

# ==================== Sidebar ====================
with st.sidebar:
    st.markdown("### 🧪 ERP Automation")
    st.caption("لوحة التحكم المتقدمة")
    st.markdown("---")

    theme_toggle_button()

    st.markdown("---")
    st.markdown("### 📊 الإحصائيات")
    st.metric("اختبارات", len(tests))
    st.metric("فئات", len(categories))

    st.markdown("---")
    st.markdown("### ℹ️ معلومات")
    st.caption("**الإصدار:** v3.0")
    st.caption("**البيئة:** Test Site")
    st.caption("**الحالة:** 🟢 يعمل")
