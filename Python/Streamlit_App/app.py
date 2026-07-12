import os
import base64
import streamlit as st
from streamlit_option_menu import option_menu

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo.png")

_last_page = st.session_state.get("main_nav", "Overview")
_sidebar_state = "expanded" if _last_page == "Overview" else "collapsed"

st.set_page_config(
    page_title="Telecom Churn Intelligence",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state=_sidebar_state,
)


def image_to_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


st.markdown("""
<style>
    [data-testid="stAppViewContainer"],
    [data-testid="stApp"] {
        background-color: #0F172A !important;
        color: #F1F5F9 !important;
    }

    /* ───────── Top Toolbar (Deploy bar) ───────── */
    [data-testid="stHeader"] {
        height: 25px !important;
        min-height: 25px !important;
    }

    [data-testid="stToolbar"] {
        right: 8px !important;
    }

    /* ───────── Sidebar Width ───────── */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B !important;
        width: 215px !important;
        min-width: 215px !important;
        max-width: 215px !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        width: 215px !important;
        min-width: 215px !important;
        max-width: 215px !important;
    }

    /* ───────── Sidebar Top Space ───────── */
    [data-testid="stSidebarHeader"] {
        height: 20px !important;
        min-height: 20px !important;
        padding: 0px 8px !important;
        margin: 0px !important;
    }

   [data-testid="stSidebarHeader"] button {
    margin-top: 2px !important;
    transform: scale(0.75) !important;
    transform-origin: center !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #94A3B8 !important;
    opacity: 0.65 !important;
}

[data-testid="stSidebarHeader"] button:hover {
    background: #1E293B !important;
    opacity: 1 !important;
    border-radius: 6px !important;
}

    [data-testid="stSidebarUserContent"] {
        padding-top: 0px !important;
        padding-left: 0.85rem !important;
        padding-right: 0.85rem !important;
        margin-top: -8px !important;
    }

    [data-testid="stSidebarContent"] {
        padding-top: 0px !important;
        margin-top: 0px !important;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.45rem !important;
    }

    [data-testid="stSidebar"][aria-expanded="false"] {
        width: 0px !important;
        min-width: 0px !important;
        max-width: 0px !important;
    }

    [data-testid="stSidebarNav"] {
        display: none;
    }

    /* ───────── General Theme ───────── */
    .stMarkdown, .stText, p, span, label, div {
        color: #F1F5F9 !important;
    }

    [data-testid="stMultiSelect"] > div,
    [data-testid="stSelectbox"] > div,
    [data-testid="stNumberInput"] > div,
    [data-testid="stTextInput"] > div {
        background-color: #1E293B !important;
        border-color: #334155 !important;
        color: #F1F5F9 !important;
    }

    .stMultiSelect span {
        background-color: #334155 !important;
        color: #F1F5F9 !important;
    }

    [data-testid="stSlider"] {
        color: #2DD4BF !important;
    }

    [data-testid="metric-container"] {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        padding: 14px !important;
    }

    .stButton > button {
        background-color: #2DD4BF !important;
        color: #0F172A !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 10px 20px !important;
    }

    .stButton > button:hover {
        background-color: #14B8A6 !important;
    }

    .block-container {
        padding-top: 0.1rem !important;
        padding-bottom: 1rem !important;
                margin-top: -0.8rem !important;
                    max-width: 100% !important;
        animation: fadeInUp 0.35s ease-out;
    }

    .js-plotly-plot {
        border-radius: 10px;
    }

    [data-testid="stSpinner"] {
        color: #2DD4BF !important;
    }

    ::-webkit-scrollbar {
        width: 6px;
    }

    ::-webkit-scrollbar-track {
        background: #0F172A;
    }

    ::-webkit-scrollbar-thumb {
        background: #334155;
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #475569;
    }

    .kpi-card {
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        cursor: default;
    }

    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 18px rgba(0,0,0,0.35);
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(6px);
        }

        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* ───────── Custom Sidebar Elements ───────── */
    .side-logo-box {
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 0px;
        margin-bottom: 6px;
    }

    .side-logo {
    width: 205px !important;
    max-width: none !important;
    height: auto !important;
    display: block !important;
    object-fit: contain !important;
}

    .side-logo-missing {
        width: 135px;
        height: 80px;
        border: 1px dashed #334155;
        border-radius: 10px;
        background: #111827;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        color: #94A3B8 !important;
        font-size: 10px;
        line-height: 1.4;
    }

    .side-title {
        text-align: center;
        margin-bottom: 8px;
    }

    .side-title-main {
        font-size: 16px;
        font-weight: 800;
        line-height: 1.35;
        color: #F8FAFC !important;
        margin-bottom: 8px;
    }

    .side-badge {
        display: inline-block;
        background: #1E293B;
        color: #CBD5E1 !important;
        padding: 5px 12px;
        border-radius: 18px;
        font-size: 9px;
        font-weight: 600;
        border: 1px solid #334155;
        white-space: nowrap;
    }

    .side-divider {
        height: 1px;
        background: #334155;
        margin: 16px 0 14px 0;
        opacity: 0.8;
    }

    /* Divider right before the Dataset card only — tighter spacing
       so the Dataset/Team block moves up, nothing else is affected */
    .side-divider-tight {
        height: 1px;
        background: #334155;
        margin: -30px 0 6px 0;
        opacity: 0.8;
    }

    .side-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 11px;
        padding: 12px;
        margin-top: -20px;
        margin-bottom: 14px;
        width: 100%;
        box-sizing: border-box;
    }

    .side-card-title {
        font-size: 9px;
        color: #94A3B8 !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 800;
        margin-bottom: 10px;
    }

    .side-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 7px;
        width: 100%;
    }

    .side-row:last-child {
        margin-bottom: 0px;
    }

    .side-label {
        font-size: 10px;
        color: #CBD5E1 !important;
        font-weight: 600;
    }

    .side-value {
        font-size: 11px;
        color: #2DD4BF !important;
        font-weight: 900;
    }

    .side-value-red {
        font-size: 11px;
        color: #FB7185 !important;
        font-weight: 900;
    }

    .team-box {
        text-align: center;
        font-size: 10px;
        line-height: 1.55;
        color: #CBD5E1 !important;
        margin-top: 2px;
        padding-bottom: 8px;
    }

    .team-title {
        color: #94A3B8 !important;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .team-instructor {
        color: #FBBF24 !important;
        font-weight: 700;
        margin-top: 6px;
    }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────
with st.sidebar:
    # Logo
    if os.path.exists(LOGO_PATH):
        logo_b64 = image_to_base64(LOGO_PATH)
        st.markdown(
            f"""
<div class="side-logo-box">
<img src="data:image/png;base64,{logo_b64}" class="side-logo">
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
<div class="side-logo-box">
<div class="side-logo-missing">
Add logo<br>assets/logo.png
</div>
</div>
""",
            unsafe_allow_html=True,
        )

    # Title
    st.markdown(
        """
<div class="side-title">
<div class="side-title-main">
Telecom Churn<br>Intelligence
</div>
<div class="side-badge">
DEPI — Data Analysis Track
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-divider"></div>', unsafe_allow_html=True)

    # Navigation
    pages = [
        "Overview",
        "Executive Dashboard",
        "Customer & Revenue",
        "ML Prediction",
    ]

    selected = option_menu(
        menu_title=None,
        options=pages,
        icons=["house-fill", "bar-chart-fill", "people-fill", "robot"],
        default_index=pages.index(_last_page) if _last_page in pages else 0,
        key="main_nav",
        styles={
            "container": {
                "background-color": "#0F172A",
                "padding": "0",
                "margin": "0",
            },
            "icon": {
                "color": "#FBBF24",
                "font-size": "13px",
            },
            "nav-link": {
                "font-size": "12px",
                "color": "#94A3B8",
                "border-radius": "8px",
                "margin": "2px 0",
                "padding": "8px 10px",
                "font-weight": "500",
            },
            "nav-link-selected": {
                "background-color": "#2DD4BF20",
                "color": "#2DD4BF",
                "font-weight": "700",
                "border": "1px solid #2DD4BF40",
            },
        },
    )

    # Tighter divider — only this one moves the Dataset/Team block up
    st.markdown('<div class="side-divider-tight"></div>', unsafe_allow_html=True)

    # Dataset Card
    st.markdown(
        f"""
<div class="side-card">
<div class="side-card-title">Dataset</div>
<div class="side-row">
<div class="side-label">Total Customers</div>
<div class="side-value">7,043</div>
</div>
<div class="side-row">
<div class="side-label">Features</div>
<div class="side-value">38</div>
</div>
<div class="side-row">
<div class="side-label">Churn Rate</div>
<div class="side-value-red">26.5%</div>
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Team Card
    st.markdown(
        """
<div class="team-box">
<div class="team-title">Team</div>
<div>Salma · Marwa · Noor</div>
<div>Shahd · Mariam</div>
<div class="team-instructor">Instructor: Amal Mahmoud</div>
</div>
""",
        unsafe_allow_html=True,
    )


# ── Page Routing ──────────────────────────────────────
import screens.overview as overview_page
import screens.dashboard as dash_page
import screens.customer as cust_page
import screens.ml as ml_page

if selected == "Overview":
    overview_page.show()

elif selected == "Executive Dashboard":
    dash_page.show()

elif selected == "Customer & Revenue":
    cust_page.show()

elif selected == "ML Prediction":
    ml_page.show()