"""
Screenshots Page - Modern Gallery
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from dashboard.theme import init_theme, apply_theme, theme_toggle_button

st.set_page_config(page_title="Screenshots", page_icon="📸", layout="wide")
init_theme()
apply_theme()

SCREENSHOTS_DIR = BASE_DIR / "reports" / "screenshots"

st.title("📸 الصور")
st.caption("لقطات من تشغيل الاختبارات")
st.markdown("---")

if not SCREENSHOTS_DIR.exists():
    st.info("مجلد الصور غير موجود")
    st.stop()

screenshots = sorted(SCREENSHOTS_DIR.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)

if not screenshots:
    st.success("🎉 لا توجد صور")
    st.stop()

# ==================== Filters ====================
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    only_failures = st.checkbox("⚠️ صور الفشل فقط", value=False)
with col2:
    limit = st.selectbox("عدد الصور", [12, 24, 48, 100], index=0)

filtered = [s for s in screenshots if s.name.startswith(("FAIL_", "ERROR"))] if only_failures else screenshots

st.markdown(f"### 📁 **{len(filtered)}** صورة")

# ==================== Gallery ====================
cols = st.columns(3)
for i, img in enumerate(filtered[:limit]):
    with cols[i % 3]:
        st.image(str(img), caption=img.name, use_container_width=True)
        st.caption(f"📦 {img.stat().st_size // 1024} KB")

# ==================== Sidebar ====================
with st.sidebar:
    theme_toggle_button()
