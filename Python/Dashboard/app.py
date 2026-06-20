import streamlit as st
from streamlit_option_menu import option_menu

# Decide the sidebar's initial state BEFORE set_page_config
_last_page = st.session_state.get("main_nav", "Overview")
_sidebar_state = "expanded" if _last_page == "Overview" else "collapsed"

st.set_page_config(
    page_title="Telecom Churn Intelligence",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state=_sidebar_state
)

# ── Global Dark Mode + Compact CSS ────────────────────
st.markdown("""
<style>
    /* Auto-hide Streamlit top navbar: hidden normally, appears on mouse hover */
header[data-testid="stHeader"] {
    height: 35px !important;
    min-height: 35px !important;
    max-height: 35px !important;
    background-color: #0B1220 !important;

    opacity: 0 !important;
    transform: translateY(-34px) !important;
    transition: opacity 0.18s ease, transform 0.18s ease !important;

    pointer-events: auto !important;
}

/* Show navbar when mouse goes to the top area */
header[data-testid="stHeader"]:hover {
    opacity: 1 !important;
    transform: translateY(0) !important;
}

/* Keep Deploy / toolbar available when navbar appears */
div[data-testid="stToolbar"] {
    display: flex !important;
    opacity: 1 !important;
    visibility: visible !important;
}

/* Hide only the colored Streamlit decoration line */
div[data-testid="stDecoration"] {
    display: none !important;
}

/* Keep footer hidden */
footer {
    visibility: hidden !important;
}

    /* Main background */
    [data-testid="stAppViewContainer"],
    [data-testid="stApp"] {
        background-color: #0F172A !important;
        color: #F1F5F9 !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B !important;
    }

    /* All text */
    .stMarkdown, .stText, p, span, label, div {
        color: #F1F5F9 !important;
    }

    /* Compact page padding */
    .block-container {
        padding-top: 0.3rem !important;
        padding-bottom: 0rem !important;
        padding-left: 2.2rem !important;
        padding-right: 2.2rem !important;
        animation: fadeInUp 0.35s ease-out;
    }

    /* Reduce vertical gaps */
    div[data-testid="stVerticalBlock"] {
        gap: 0.45rem !important;
    }

    div[data-testid="column"] {
        gap: 0.25rem !important;
    }

    /* Hide Streamlit auto sidebar nav */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* Multiselect */
    [data-testid="stMultiSelect"] > div {
        background-color: #1E293B !important;
        border-color: #334155 !important;
        color: #F1F5F9 !important;
    }

    .stMultiSelect span {
        background-color: #334155 !important;
        color: #F1F5F9 !important;
    }

    /* Selectbox */
    [data-testid="stSelectbox"] > div {
        background-color: #1E293B !important;
        border-color: #334155 !important;
    }

    /* Inputs compact */
    .stSlider {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }

    .stSelectbox {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }

    label {
        font-size: 11px !important;
    }

    /* Slider */
    [data-testid="stSlider"] {
        color: #2DD4BF !important;
    }

    /* Metric */
    [data-testid="metric-container"] {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: #2DD4BF !important;
        color: #0F172A !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
    }

    .stButton > button:hover {
        background-color: #14B8A6 !important;
    }

    /* Download button */
    .stDownloadButton > button {
        background-color: #2DD4BF !important;
        color: #0F172A !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
    }

    /* Plotly chart bg */
    .js-plotly-plot {
        border-radius: 10px;
    }

    /* Spinner */
    [data-testid="stSpinner"] {
        color: #2DD4BF !important;
    }

    /* Scrollbar */
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

    /* KPI card hover */
    .kpi-card {
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        cursor: default;
    }

    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(0,0,0,0.30);
    }

    /* Fade animation */
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
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:14px 0 10px'>
        <div style='font-size:34px'>📡</div>
        <div style='font-size:15px; font-weight:700; color:#F1F5F9;
                    margin-top:5px; line-height:1.3'>
            Telecom Churn<br>Intelligence
        </div>
        <div style='font-size:10px; color:#94A3B8; margin-top:6px;
                    background:#1E293B; padding:4px 12px; border-radius:20px;
                    display:inline-block'>
            DEPI — Data Analysis Track
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<hr style='border-color:#1E293B;margin:0 0 10px'>",
        unsafe_allow_html=True
    )

    pages = ["Overview", "Executive Dashboard", "Customer & Revenue", "ML Prediction"]

    selected = option_menu(
        menu_title=None,
        options=pages,
        icons=["house-fill", "bar-chart-fill", "people-fill", "robot"],
        default_index=pages.index(_last_page),
        key="main_nav",
        styles={
            "container": {
                "background-color": "#0F172A",
                "padding": "0"
            },
            "icon": {
                "color": "#FBBF24",
                "font-size": "14px"
            },
            "nav-link": {
                "font-size": "12px",
                "color": "#94A3B8",
                "border-radius": "8px",
                "margin": "2px 0",
                "padding": "9px 13px"
            },
            "nav-link-selected": {
                "background-color": "#2DD4BF20",
                "color": "#2DD4BF",
                "font-weight": "600",
                "border": "1px solid #2DD4BF40"
            },
        }
    )

    st.markdown(
        "<hr style='border-color:#1E293B;margin:12px 0 10px'>",
        unsafe_allow_html=True
    )

    st.markdown("""
    <div style='background:#1E293B; border-radius:10px; padding:10px 13px;
                margin-bottom:10px'>
        <div style='font-size:10px; color:#94A3B8; text-transform:uppercase;
                    letter-spacing:0.05em; margin-bottom:7px'>Dataset</div>
        <div style='display:flex; justify-content:space-between;
                    font-size:11px; color:#F1F5F9; margin-bottom:4px'>
            <span>Total Customers</span><span style='color:#2DD4BF'>7,043</span>
        </div>
        <div style='display:flex; justify-content:space-between;
                    font-size:11px; color:#F1F5F9; margin-bottom:4px'>
            <span>Features</span><span style='color:#2DD4BF'>38</span>
        </div>
        <div style='display:flex; justify-content:space-between;
                    font-size:11px; color:#F1F5F9'>
            <span>Churn Rate</span>
            <span style='color:#FB7185; font-weight:600'>26.5%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='font-size:10.5px; color:#475569; text-align:center;
                line-height:1.6; padding-bottom:8px'>
        <span style='color:#94A3B8'>Team:</span><br>
        Salma · Marwa · Noor<br>Shahd · Mariam<br>
        <span style='color:#FBBF24'>Instructor: Amal Mahmoud</span>
    </div>
    """, unsafe_allow_html=True)

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