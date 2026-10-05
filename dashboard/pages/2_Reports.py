"""
Reports Page - with Filters & Charts
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dashboard.theme import init_theme, apply_theme, theme_toggle_button

st.set_page_config(page_title="Reports", page_icon="📊", layout="wide")
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
                data = json.load(fp)
                # Parse timestamp
                ts = data.get("timestamp", "")
                if len(ts) >= 15:
                    try:
                        data["_datetime"] = datetime.strptime(ts[:15], "%Y%m%d_%H%M%S")
                    except Exception:
                        data["_datetime"] = None
                summaries.append(data)
        except Exception:
            pass
    return summaries


st.title("📊 التقارير")
st.caption("سجل التشغيلات والنتائج التفصيلية")
st.markdown("---")

all_summaries = load_summaries()

if not all_summaries:
    st.info("📭 لا توجد تقارير. روح لصفحة **🏃 Run Tests** وشغّل اختبارات.")
    st.stop()

# ==================== Filters ====================
st.subheader("🎛️ الفلاتر")

col1, col2, col3 = st.columns(3)

with col1:
    date_filter = st.selectbox(
        "📅 الفترة الزمنية",
        ["الكل", "آخر ساعة", "آخر 24 ساعة", "آخر 7 أيام", "آخر 30 يوم", "مخصص"],
        index=0,
    )

with col2:
    if date_filter == "مخصص":
        custom_start = st.date_input("من", value=datetime.now() - timedelta(days=7))
        custom_end = st.date_input("إلى", value=datetime.now())
    else:
        custom_start = None
        custom_end = None
        st.write("")  # spacing

with col3:
    status_filter = st.selectbox(
        "✅ الحالة",
        ["الكل", "ناجحة فقط", "فاشلة فقط"],
        index=0,
    )

# Apply filters
summaries = all_summaries.copy()
now = datetime.now()

if date_filter != "الكل" and date_filter != "مخصص":
    delta_map = {
        "آخر ساعة": timedelta(hours=1),
        "آخر 24 ساعة": timedelta(hours=24),
        "آخر 7 أيام": timedelta(days=7),
        "آخر 30 يوم": timedelta(days=30),
    }
    cutoff = now - delta_map[date_filter]
    summaries = [s for s in summaries if s.get("_datetime") and s["_datetime"] >= cutoff]

elif date_filter == "مخصص" and custom_start and custom_end:
    start_dt = datetime.combine(custom_start, datetime.min.time())
    end_dt = datetime.combine(custom_end, datetime.max.time())
    summaries = [
        s for s in summaries
        if s.get("_datetime") and start_dt <= s["_datetime"] <= end_dt
    ]

if status_filter == "ناجحة فقط":
    summaries = [s for s in summaries if s.get("failed", 0) + s.get("errors", 0) == 0]
elif status_filter == "فاشلة فقط":
    summaries = [s for s in summaries if s.get("failed", 0) + s.get("errors", 0) > 0]

st.caption(f"📁 **{len(summaries)}** تشغيل بعد الفلترة (من إجمالي {len(all_summaries)})")

if not summaries:
    st.warning("⚠️ لا توجد تشغيلات تطابق الفلتر")
    st.stop()

st.markdown("---")

latest = summaries[0]
total = latest.get("total", 0)
passed = latest.get("passed", 0)
failed = latest.get("failed", 0) + latest.get("errors", 0)
rate = round((passed / total * 100) if total > 0 else 0, 1)

# ==================== Metrics ====================
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("✅ ناجح", passed)
with col2:
    st.metric("❌ فاشل", failed)
with col3:
    st.metric("📊 نسبة النجاح", f"{rate}%")
with col4:
    st.metric("📁 إجمالي التشغيلات", len(summaries))

st.markdown("---")

# ==================== Charts ====================
if len(summaries) >= 2:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📈 تطور نسبة النجاح")

        trend_data = []
        for s in reversed(summaries[:20]):
            t = s.get("total", 0)
            p = s.get("passed", 0)
            r = round((p / t * 100) if t > 0 else 0, 1)
            trend_data.append({
                "التشغيل": s.get("timestamp", "")[-6:],
                "نسبة النجاح": r,
            })

        df_trend = pd.DataFrame(trend_data)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_trend["التشغيل"],
            y=df_trend["نسبة النجاح"],
            mode="lines+markers",
            line=dict(color="#2563eb", width=3),
            marker=dict(size=10, color="#2563eb"),
            fill="tozeroy",
            fillcolor="rgba(37, 99, 235, 0.1)",
            name="نسبة النجاح",
        ))

        fig.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=20, b=0),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, color="#64748b"),
            yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)", color="#64748b", range=[0, 105]),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🥧 آخر تشغيل")

        if total > 0:
            fig = go.Figure(data=[go.Pie(
                labels=["ناجح", "فاشل"],
                values=[passed, failed],
                hole=0.65,
                marker=dict(colors=["#10b981", "#ef4444"]),
                textinfo="label+percent",
                textfont=dict(size=12),
            )])
            fig.update_layout(
                height=350,
                margin=dict(l=0, r=0, t=20, b=0),
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

# ==================== History ====================
st.subheader("📚 سجل التشغيلات")

history = []
for s in summaries[:50]:
    t = s.get("total", 0)
    p = s.get("passed", 0)
    f = s.get("failed", 0) + s.get("errors", 0)
    r = round((p / t * 100) if t > 0 else 0, 1)
    dt = s.get("_datetime")
    date_str = dt.strftime("%Y-%m-%d %H:%M") if dt else s.get("timestamp", "")

    history.append({
        "⏰ التاريخ": date_str,
        "📊 الإجمالي": t,
        "✅ ناجح": p,
        "❌ فاشل": f,
        "📈 النسبة": f"{r}%",
        "⏱️ المدة (ث)": int(s.get("duration_seconds", 0)),
    })

df_history = pd.DataFrame(history)
st.dataframe(df_history, use_container_width=True, hide_index=True)

with st.sidebar:
    theme_toggle_button()
