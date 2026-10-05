"""
Test Comparison Page
"""
import sys
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dashboard.theme import init_theme, apply_theme, theme_toggle_button

st.set_page_config(page_title="Compare", page_icon="🔍", layout="wide")
init_theme()
apply_theme()

RESULTS_DIR = BASE_DIR / "reports" / "results"


@st.cache_data(ttl=5)
def load_summaries():
    summaries = []
    if not RESULTS_DIR.exists():
        return summaries
    for f in sorted(RESULTS_DIR.glob("summary_*.json"), reverse=True):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                summaries.append(json.load(fp))
        except Exception:
            pass
    return summaries


st.title("🔍 مقارنة التشغيلات")
st.caption("قارن بين تشغيلين لمعرفة الفرق")
st.markdown("---")

summaries = load_summaries()

if len(summaries) < 2:
    st.info("📭 محتاج على الأقل تشغيلين للمقارنة. شغّل اختبارات من صفحة **Run Tests**.")
    st.stop()

# ==================== Select 2 runs ====================
def format_run(s):
    ts = s.get("timestamp", "")
    if len(ts) >= 13:
        return f"{ts[:4]}-{ts[4:6]}-{ts[6:8]} {ts[9:11]}:{ts[11:13]}"
    return ts


run_options = [format_run(s) for s in summaries[:30]]

col1, col2 = st.columns(2)
with col1:
    idx1 = st.selectbox("🅰️ التشغيل الأول", range(len(run_options)), format_func=lambda i: run_options[i], index=0)
with col2:
    idx2 = st.selectbox("🅱️ التشغيل الثاني", range(len(run_options)), format_func=lambda i: run_options[i], index=min(1, len(run_options) - 1))

run1 = summaries[idx1]
run2 = summaries[idx2]

st.markdown("---")

# ==================== Comparison ====================
st.subheader("📊 المقارنة")

def get_metrics(run):
    total = run.get("total", 0)
    passed = run.get("passed", 0)
    failed = run.get("failed", 0) + run.get("errors", 0)
    duration = run.get("duration_seconds", 0)
    rate = round((passed / total * 100) if total > 0 else 0, 1)
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "duration": duration,
        "rate": rate,
    }

m1 = get_metrics(run1)
m2 = get_metrics(run2)

# Side by side
col1, col2, col3 = st.columns([2, 1, 2])

with col1:
    st.markdown(f"### 🅰️ {format_run(run1)}")
    st.metric("📊 الإجمالي", m1['total'])
    st.metric("✅ ناجح", m1['passed'])
    st.metric("❌ فاشل", m1['failed'])
    st.metric("📈 النسبة", f"{m1['rate']}%")
    st.metric("⏱️ المدة", f"{int(m1['duration'])} ث")

with col2:
    st.markdown("<br><br>", unsafe_allow_html=True)

    def delta(a, b, higher_better=True):
        diff = a - b
        if diff == 0:
            return "➖", "gray"
        if higher_better:
            return (f"▲ +{diff:.1f}", "green") if diff > 0 else (f"▼ {diff:.1f}", "red")
        else:
            return (f"▼ {diff:.1f}", "green") if diff < 0 else (f"▲ +{diff:.1f}", "red")

    for label, v1, v2, higher in [
        ("الإجمالي", m1['total'], m2['total'], True),
        ("ناج@'
"""
Test Comparison Page
"""
import sys
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dashboard.theme import init_theme, apply_theme, theme_toggle_button

st.set_page_config(page_title="Compare", page_icon="🔍", layout="wide")
init_theme()
apply_theme()

RESULTS_DIR = BASE_DIR / "reports" / "results"


@st.cache_data(ttl=5)
def load_summaries():
    summaries = []
    if not RESULTS_DIR.exists():
        return summaries
    for f in sorted(RESULTS_DIR.glob("summary_*.json"), reverse=True):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                summaries.append(json.load(fp))
        except Exception:
            pass
    return summaries


st.title("🔍 مقارنة التشغيلات")
st.caption("قارن بين تشغيلين لمعرفة الفرق")
st.markdown("---")

summaries = load_summaries()

if len(summaries) < 2:
    st.info("📭 محتاج على الأقل تشغيلين للمقارنة. شغّل اختبارات من صفحة **Run Tests**.")
    st.stop()

# ==================== Select 2 runs ====================
def format_run(s):
    ts = s.get("timestamp", "")
    if len(ts) >= 13:
        return f"{ts[:4]}-{ts[4:6]}-{ts[6:8]} {ts[9:11]}:{ts[11:13]}"
    return ts


run_options = [format_run(s) for s in summaries[:30]]

col1, col2 = st.columns(2)
with col1:
    idx1 = st.selectbox("🅰️ التشغيل الأول", range(len(run_options)), format_func=lambda i: run_options[i], index=0)
with col2:
    idx2 = st.selectbox("🅱️ التشغيل الثاني", range(len(run_options)), format_func=lambda i: run_options[i], index=min(1, len(run_options) - 1))

run1 = summaries[idx1]
run2 = summaries[idx2]

st.markdown("---")

# ==================== Comparison ====================
st.subheader("📊 المقارنة")

def get_metrics(run):
    total = run.get("total", 0)
    passed = run.get("passed", 0)
    failed = run.get("failed", 0) + run.get("errors", 0)
    duration = run.get("duration_seconds", 0)
    rate = round((passed / total * 100) if total > 0 else 0, 1)
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "duration": duration,
        "rate": rate,
    }

m1 = get_metrics(run1)
m2 = get_metrics(run2)

# Side by side
col1, col2, col3 = st.columns([2, 1, 2])

with col1:
    st.markdown(f"### 🅰️ {format_run(run1)}")
    st.metric("📊 الإجمالي", m1['total'])
    st.metric("✅ ناجح", m1['passed'])
    st.metric("❌ فاشل", m1['failed'])
    st.metric("📈 النسبة", f"{m1['rate']}%")
    st.metric("⏱️ المدة", f"{int(m1['duration'])} ث")

with col2:
    st.markdown("<br><br>", unsafe_allow_html=True)

    def delta(a, b, higher_better=True):
        diff = a - b
        if diff == 0:
            return "➖", "gray"
        if higher_better:
            return (f"▲ +{diff:.1f}", "green") if diff > 0 else (f"▼ {diff:.1f}", "red")
        else:
            return (f"▼ {diff:.1f}", "green") if diff < 0 else (f"▲ +{diff:.1f}", "red")

    for label, v1, v2, higher in [
        ("الإجمالي", m1['total'], m2['total'], True),
        ("ناجح", m1['passed'], m2['passed'], True),
        ("فاشل", m1['failed'], m2['failed'], False),
        ("النسبة %", m1['rate'], m2['rate'], True),
        ("المدة (ث)", m1['duration'], m2['duration'], False),
    ]:
        arrow, color = delta(v1, v2, higher)
        st.markdown(f"<div style='text-align:center;padding:8px;'><span style='color:{color};font-weight:700;'>{arrow}</span></div>", unsafe_allow_html=True)

with col3:
    st.markdown(f"### 🅱️ {format_run(run2)}")
    st.metric("📊 الإجمالي", m2['total'])
    st.metric("✅ ناجح", m2['passed'])
    st.metric("❌ فاشل", m2['failed'])
    st.metric("📈 النسبة", f"{m2['rate']}%")
    st.metric("⏱️ المدة", f"{int(m2['duration'])} ث")

# ==================== Chart ====================
st.markdown("---")
st.subheader("📈 مقارنة بصرية")

categories_chart = ["الإجمالي", "ناجح", "فاشل"]
values1 = [m1['total'], m1['passed'], m1['failed']]
values2 = [m2['total'], m2['passed'], m2['failed']]

fig = go.Figure()
fig.add_trace(go.Bar(name="🅰️ الأول", x=categories_chart, y=values1, marker_color="#2563eb"))
fig.add_trace(go.Bar(name="🅱️ التاني", x=categories_chart, y=values2, marker_color="#a855f7"))
fig.update_layout(
    barmode="group",
    height=350,
    margin=dict(l=0, r=0, t=20, b=0),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
)
st.plotly_chart(fig, use_container_width=True)

with st.sidebar:
    theme_toggle_button()
