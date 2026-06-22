import streamlit as st
from streamlit_option_menu import option_menu

# Decide the sidebar's initial state BEFORE set_page_config:
# expanded on the Overview/Home page, collapsed on every other page.
_last_page = st.session_state.get('main_nav', 'Overview')
_sidebar_state = "expanded" if _last_page == "Overview" else "collapsed"

st.set_page_config(
    page_title="Telecom Churn Intelligence",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state=_sidebar_state
)

# ── Global Dark Mode CSS ──────────────────────────────
st.markdown("""
<style>
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

    /* Hide Streamlit's auto-generated page nav (we use our own option_menu) */
    [data-testid="stSidebarNav"] {
        display: none;
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
        padding: 14px !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: #2DD4BF !important;
        color: #0F172A !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
    }
    .stButton > button:hover {
        background-color: #14B8A6 !important;
    }

    /* Remove default padding */
    .block-container {
        padding-top: 1.1rem !important;
        padding-bottom: 1rem !important;
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
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0F172A; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #475569; }

    /* KPI card hover lift — subtle, professional */
    .kpi-card {
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        cursor: default;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 18px rgba(0,0,0,0.35);
    }

    /* Gentle fade-in when a page loads */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(6px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .block-container {
        animation: fadeInUp 0.35s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:20px 0 14px'>
        <div style='font-size:38px'>📡</div>
        <div style='font-size:16px; font-weight:700; color:#F1F5F9;
                    margin-top:6px; line-height:1.3'>
            Telecom Churn<br>Intelligence
        </div>
        <div style='font-size:11px; color:#94A3B8; margin-top:6px;
                    background:#1E293B; padding:4px 12px; border-radius:20px;
                    display:inline-block'>
            DEPI — Data Analysis Track
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#1E293B;margin:0 0 12px'>",
                unsafe_allow_html=True)

    selected = option_menu(
        menu_title=None,
        options=["Overview", "Executive Dashboard", "Customer & Revenue", "ML Prediction"],
        icons=["house-fill", "bar-chart-fill", "people-fill", "robot"],
        default_index=["Overview", "Executive Dashboard", "Customer & Revenue", "ML Prediction"].index(_last_page),
        key='main_nav',
        styles={
            "container": {
                "background-color": "#0F172A",
                "padding": "0"
            },
            "icon": {
                "color": "#FBBF24",
                "font-size": "15px"
            },
            "nav-link": {
                "font-size": "13px",
                "color": "#94A3B8",
                "border-radius": "8px",
                "margin": "3px 0",
                "padding": "10px 14px"
            },
            "nav-link-selected": {
                "background-color": "#2DD4BF20",
                "color": "#2DD4BF",
                "font-weight": "600",
                "border": "1px solid #2DD4BF40"
            },
        }
    )

    st.markdown("<hr style='border-color:#1E293B;margin:16px 0 12px'>",
                unsafe_allow_html=True)

    # Dataset stats
    st.markdown("""
    <div style='background:#1E293B; border-radius:10px; padding:12px 14px;
                margin-bottom:12px'>
        <div style='font-size:10px; color:#94A3B8; text-transform:uppercase;
                    letter-spacing:0.05em; margin-bottom:8px'>Dataset</div>
        <div style='display:flex; justify-content:space-between;
                    font-size:12px; color:#F1F5F9; margin-bottom:4px'>
            <span>Total Customers</span><span style='color:#2DD4BF'>7,043</span>
        </div>
        <div style='display:flex; justify-content:space-between;
                    font-size:12px; color:#F1F5F9; margin-bottom:4px'>
            <span>Features</span><span style='color:#2DD4BF'>38</span>
        </div>
        <div style='display:flex; justify-content:space-between;
                    font-size:12px; color:#F1F5F9'>
            <span>Churn Rate</span>
            <span style='color:#FB7185; font-weight:600'>26.5%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='font-size:11px; color:#475569; text-align:center;
                line-height:1.7; padding-bottom:10px'>
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