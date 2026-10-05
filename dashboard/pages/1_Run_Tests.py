"""
Run Tests Page - with Email Notifications
"""
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from config.test_registry import TestRegistry
from config.test_runner import get_runner
from config.emailer import send_test_notification
from dashboard.theme import init_theme, apply_theme, theme_toggle_button

st.set_page_config(page_title="Run Tests", page_icon="🏃", layout="wide")
init_theme()
apply_theme()

tests = TestRegistry.get_all()
categories = TestRegistry.get_categories()

st.title("🏃 تشغيل الاختبارات")
st.caption("اختر الاختبارات واضغط زر التشغيل")
st.markdown("---")

# ==================== Filters ====================
col1, col2 = st.columns([1, 3])
with col1:
    selected_category = st.selectbox("فلتر بالفئة", ["كل الفئات"] + categories)

filtered = tests if selected_category == "كل الفئات" else TestRegistry.get_by_category(selected_category)

# ==================== Selection ====================
st.subheader("✨ اختيار الاختبارات")

col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    if st.button("✅ اختار الكل", use_container_width=True):
        for t in tests:
            st.session_state[f"test_{t['id']}"] = True
        st.rerun()
with col2:
    if st.button("❌ إلغاء الكل", use_container_width=True):
        for t in tests:
            st.session_state[f"test_{t['id']}"] = False
        st.rerun()

selected_tests = []
for test in filtered:
    key = f"test_{test['id']}"
    if key not in st.session_state:
        st.session_state[key] = False

    checked = st.checkbox(
        f"{test['icon']} **{test['name']}** — {test['description']}",
        key=key,
    )
    if checked:
        selected_tests.append(test)

st.markdown("---")

# ==================== Summary ====================
st.subheader("📊 ملخص الاختيار")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🎯 المختار", len(selected_tests))
with col2:
    total_est = sum(t['duration_estimate'] for t in selected_tests)
    st.metric("⏱️ الوقت المتوقع", f"{total_est // 60} د {total_est % 60} ث" if selected_tests else "0 ث")
with col3:
    st.metric("📂 الفئات", len(set(t['category'] for t in selected_tests)))

st.markdown("---")

# ==================== Options ====================
st.subheader("⚙️ خيارات")

col1, col2 = st.columns(2)

with col1:
    send_email = st.checkbox(
        "📧 إرسال إشعار بالبريد بعد الانتهاء",
        value=True,
        help="هيتم إرسال إيميل بالنتيجة حسب إعدادات صفحة Email"
    )

with col2:
    if send_email:
        # Check if email is configured
        from config.emailer import load_config
        cfg = load_config()
        if cfg and cfg.get("enabled"):
            st.success("✅ إعدادات الإيميل مفعّلة")
        else:
            st.warning("⚠️ الإيميل مش مفعّل — روح لصفحة 📧 Email")

st.markdown("---")

# ==================== Run ====================
run_clicked = st.button(
    "🚀 شغّل الاختبارات",
    type="primary",
    use_container_width=True,
    disabled=len(selected_tests) == 0,
)

if run_clicked:
    runner = get_runner()
    st.markdown("---")
    st.subheader("📊 النتيجة")

    progress_bar = st.progress(0, text="جاري التحضير...")
    status_area = st.empty()

    total_tests = len(selected_tests)

    for idx, test in enumerate(selected_tests):
        progress_pct = int((idx / total_tests) * 100)
        progress_bar.progress(progress_pct, text=f"⏳ {test['name']} ({idx+1}/{total_tests})")
        status_area.info(f"🔄 جاري تشغيل: **{test['name']}**")

        result = runner.run_test(test['test_path'], test_name=test['name'])

        summary = result.get("summary", {})
        passed = summary.get("passed", 0)
        failed = summary.get("failed", 0) + summary.get("errors", 0)
        total = summary.get("total", 0)
        duration = summary.get("duration_seconds", 0)

        if result.get("success") and failed == 0:
            st.success(f"✅ **{test['name']}** — نجح! ({int(duration)} ثانية)")
        else:
            st.error(f"❌ **{test['name']}** — فشل ({failed} من {total})")

        # ==================== Slack Notification ====================
        try:
            from config.slack_notifier import send_test_notification as send_slack
            slack_sent = send_slack(summary, test_name=test['name'])
            if slack_sent:
                st.info(f"📱 تم إرسال إشعار Slack لـ **{test['name']}**")
        except Exception as e:
            logger.warning(f"Slack: {str(e)[:100]}")

        # ==================== Details ====================
        with st.expander(f"📋 تفاصيل — {test['name']}"):
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("✅ ناجح", passed)
            col2.metric("❌ فاشل", failed)
            col3.metric("⏱️ المدة", f"{int(duration)} ث")
            col4.metric("📁 إجمالي", total)

            if summary.get("tests"):
                st.markdown("**تفاصيل:**")
                for t in summary["tests"]:
                    icon = "✅" if t["outcome"] == "passed" else "❌"
                    st.markdown(f"{icon} `{t['name']}` — {t['duration']} ث")

            with st.expander("📜 سجل التشغيل"):
                st.code(result.get("stdout", "لا يوجد")[-5000:], language="text")

    progress_bar.progress(100, text="✅ اكتمل التشغيل!")
    status_area.success(f"🎉 تم تشغيل {total_tests} اختبار")

with st.sidebar:
    st.markdown("### ℹ️ معلومات")
    st.metric("إجمالي الاختبارات", len(tests))
    st.metric("مختار", len(selected_tests))
    st.markdown("---")
    theme_toggle_button()

