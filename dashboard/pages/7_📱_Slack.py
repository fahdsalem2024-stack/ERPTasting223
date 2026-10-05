"""
Slack Notifications Settings
"""
import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from dashboard.theme import init_theme, apply_theme, theme_toggle_button
from config.slack_notifier import load_config, save_config

st.set_page_config(page_title="Slack", page_icon="📱", layout="wide")
init_theme()
apply_theme()

st.title("📱 Slack Notifications")
st.caption("إشعارات Slack عند نجاح أو فشل الاختبارات")
st.markdown("---")

config = load_config() or {}

st.subheader("🎛️ الحالة")
enabled = st.toggle("تفعيل إشعارات Slack", value=config.get("enabled", False))

st.markdown("---")

st.subheader("🔗 Webhook")
webhook_url = st.text_input(
    "Slack Webhook URL",
    value=config.get("webhook_url", ""),
    type="password",
    placeholder="https://hooks.slack.com/services/...",
)

st.markdown("---")

st.subheader("🔔 متى يرسل؟")
notify_on = st.radio(
    "اختر الحالة",
    ["failure", "success", "always"],
    format_func=lambda x: {
        "failure": "❌ عند الفشل فقط",
        "success": "✅ عند النجاح فقط",
        "always": "🔔 دائماً",
    }[x],
    index=["failure", "success", "always"].index(config.get("notify_on", "failure")),
)

st.markdown("---")

if st.button("💾 حفظ الإعدادات", type="primary", use_container_width=True):
    new_config = {
        "enabled": enabled,
        "webhook_url": webhook_url,
        "notify_on": notify_on,
    }
    save_config(new_config)
    st.success("✅ تم الحفظ")

st.markdown("---")

st.subheader("🧪 اختبار الإرسال")
if st.button("📨 إرسال رسالة تجريبية"):
    if not webhook_url:
        st.error("❌ محتاج Webhook URL")
    else:
        try:
            from slack_sdk.webhook import WebhookClient
            client = WebhookClient(webhook_url)
            resp = client.send(text="🧪 ERP Test Automation - Test Message")
            if resp.status_code == 200:
                st.success("✅ تم الإرسال!")
            else:
                st.error(f"❌ فشل: {resp.status_code}")
        except Exception as e:
            st.error(f"❌ خطأ: {e}")

st.markdown("---")

st.info("""
**كيف تحصل على Webhook؟**

1. افتح https://api.slack.com/messaging/webhooks
2. Create your Slack app
3. Incoming Webhooks → Activate
4. Add New Webhook
5. انسخ الـ URL والصقه
""")

with st.sidebar:
    theme_toggle_button()
