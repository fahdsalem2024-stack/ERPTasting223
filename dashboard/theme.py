"""
Theme utilities - Dark/Light mode
"""
import streamlit as st

# Theme definitions
THEMES = {
    "light": {
        "bg": "#ffffff",
        "secondary_bg": "#f8fafc",
        "text": "#0f172a",
        "muted": "#64748b",
        "border": "#e2e8f0",
        "accent": "#2563eb",
        "success": "#10b981",
        "error": "#ef4444",
    },
    "dark": {
        "bg": "#0a0e27",
        "secondary_bg": "#111633",
        "text": "#ffffff",
        "muted": "#94a3b8",
        "border": "rgba(255,255,255,0.08)",
        "accent": "#00d4ff",
        "success": "#10b981",
        "error": "#ef4444",
    }
}


def init_theme():
    """Initialize theme in session state"""
    if "theme" not in st.session_state:
        st.session_state.theme = "light"


def toggle_theme():
    """Toggle between light and dark"""
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"


def get_theme():
    """Get current theme colors"""
    return THEMES[st.session_state.get("theme", "light")]


def apply_theme():
    """Apply theme CSS"""
    theme = get_theme()
    is_dark = st.session_state.get("theme") == "light" if False else st.session_state.get("theme", "light") == "dark"

    st.markdown(f"""
    <style>
        .stApp {{
            background: {theme['bg']} !important;
            color: {theme['text']} !important;
        }}
        
        [data-testid="stSidebar"] {{
            background: {theme['secondary_bg']} !important;
        }}
        
        .stApp p, .stApp span, .stApp label, .stApp div {{
            color: {theme['text']};
        }}
        
        .stCaption, [data-testid="stCaptionContainer"] {{
            color: {theme['muted']} !important;
        }}
        
        [data-testid="stMetric"] {{
            background: {theme['secondary_bg']};
            border: 1px solid {theme['border']};
            border-radius: 12px;
            padding: 1.2rem;
            transition: all 0.3s ease;
        }}
        
        [data-testid="stMetric"]:hover {{
            border-color: {theme['accent']};
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        }}
        
        [data-testid="stMetricValue"] {{
            color: {theme['accent']} !important;
            font-weight: 800 !important;
        }}
        
        [data-testid="stMetricLabel"] {{
            color: {theme['muted']} !important;
        }}
        
        .stButton > button {{
            background: {theme['accent']} !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.2s !important;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        }}
        
        [data-testid="stContainer"][border] {{
            background: {theme['secondary_bg']};
            border: 1px solid {theme['border']} !important;
            border-radius: 12px;
        }}
        
        hr {{
            border-color: {theme['border']} !important;
        }}
        
        [data-testid="stAlert"] {{
            border-radius: 10px !important;
        }}
    </style>
    """, unsafe_allow_html=True)


def theme_toggle_button():
    """Render the theme toggle button in sidebar"""
    theme_icon = "☀️" if st.session_state.get("theme", "light") == "dark" else "🌙"
    theme_text = "Light Mode" if st.session_state.get("theme", "light") == "dark" else "Dark Mode"

    if st.sidebar.button(f"{theme_icon} {theme_text}", use_container_width=True):
        toggle_theme()
        st.rerun()
