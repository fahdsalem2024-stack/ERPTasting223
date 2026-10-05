"""
Email Notifications Settings
"""
import sys
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from dashboard.theme import init_theme, apply_theme, theme_toggle_button

st.set_page_config(page_title="Email", page_icon="📧", layout="wide")
init_theme()
apply_theme()

EMAIL_CONFIG_FILE = BASE_DIR / "config" / "email_config.json"


def load_email_config():
    if not EMAIL_CONFIG_FILE.exists():
        return {
            "enabled": False,
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "",
            "sender_password": "",
            "recipients": [],
            "notify_on": "failure",
        }
    try:
        with open(EMAIL_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_email_config(config):
    EMAIL_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EMAIL_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


st.title("📧 إشعارات البريد الإلكتروني")
st.caption("إعدادات إرسال الإشعارات عند نجاح أو فشل الاختبارات")
st.markdown("---")

config = load_email_config()

# ==================== Enable ====================
st.subheader("🎛️ الحالة")
enabled = st.toggle("تفعيل إشعارات البريد", value=config.get("enabled", False))

st.markdown("---")

# ==================== SMTP Settings ====================
st.subheader("⚙️ إعدادات SMTP")

col1, col2 = st.columns(2)
with col1:
    smtp_host = st.text_input("SMTP Host", value=config.get("smtp_host", "smtp.gmail.com"))
    sender_email = st.text_input("البريد المرسل", value=config.get("sender_email", ""))
with col2:
    smtp_port = st.number_input("SMTP Port", value=config.get("smtp_port", 587), min_value=1, max_value=65535)
    sender_password = st.text_input("كلمة المرور", value=config.get("sender_password", ""), type="password")

st.markdown("---")

# ==================== Recipients ====================
st.subheader("👥 المستقبلين")

recipients_text = st.text_area(
    "البريد الإلكتروني (كل بريد في سطر)",
    value="\n".join(config.get("recipients", [])),
    height=100,
    placeholder="user1@example.com\nuser2@example.com",
)

st.markdown("---")

# ==================== Notify On ====================
st.subheader("🔔 متى يرسل الإشعار؟")

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

# ==================== Save ====================
if st.button("💾 حفظ الإعدادات", type="primary", use_container_width=True):
    new_config = {
        "enabled": enabled,
        "smtp_host": smtp_host,
        "smtp_port": smtp_port,
        "sender_email": sender_email,
        "sender_password": sender_password,
        "recipients": [r.strip() for r in recipients_text.split("\n") if r.strip()],
        "notify_on": notify_on,
    }
    save_email_config(new_config)
    st.success("✅ تم حفظ الإعدادات")

st.markdown("---")

# ==================== Test Email ====================
st.subheader("🧪 اختبار الإرسال")

if st.button("📨 إرسال بريد تجريبي"):
    if not config.get("sender_email") or not config.get("sender_password"):
        st.error("❌ محتاج تدخل بيانات المرسل أولاً")
    elif not config.get("recipients"):
        st.error("❌ محتاج تضيف مستقبل واحد على الأقل")
    else:
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = ", ".join(config["recipients"])
            msg["Subject"] = "🧪 ERP Test Automation - Test Email"

            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #2563eb;">🧪 اختبار إشعار البريد</h2>
                <p>ده بريد تجريبي من <strong>ERP Test Automation</strong>.</p>
                <p>التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </body>
            </html>
            """
            msg.attach(MIMEText(body, "html"))

            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)

            st.success("✅ تم إرسال البريد بنجاح!")
        except Exception as e:
            st.error(f"❌ فشل الإرسال: {str(e)}")

st.markdown("---")

# ==================== Info ====================
st.info("""
**ℹ️ ملاحظات مهمة:**

- **Gmail:** محتاج [App Password](https://myaccount.google.com/apppasswords) مش كلمة المرور العادية
- **Outlook:** `smtp-mail.outlook.com` port `587`
- **Yahoo:** `smtp.mail.yahoo.com` port `587`

بعد الحفظ، الإشعارات هتشتغل تلقائياً عند تشغيل الاختبارات من الداشبورد.
""")

with st.sidebar:
    theme_toggle_button()
