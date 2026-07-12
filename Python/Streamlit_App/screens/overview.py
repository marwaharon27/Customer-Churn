import streamlit as st
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.load_data import load_full, load_kpis

BG      = '#0F172A'
CARD_BG = '#1E293B'
BORDER  = '#334155'
RED     = '#FB7185'
GREEN   = '#34D399'
TEAL    = '#2DD4BF'
BLUE    = '#60A5FA'
GOLD    = '#FBBF24'
ORANGE  = '#FB923C'
TEXT    = '#F1F5F9'
SUBTEXT = '#94A3B8'


def stat_chip(col, label, value, color):
    col.markdown(f"""
    <div class='kpi-card' style='background:{CARD_BG};border:1px solid {BORDER};
                border-top:3px solid {color};border-radius:12px;
                padding:14px 16px;text-align:center'>
        <div style='font-size:22px;font-weight:700;color:{color}'>{value}</div>
        <div style='font-size:11px;color:{SUBTEXT};margin-top:4px;
                    text-transform:uppercase;letter-spacing:.04em'>{label}</div>
    </div>""", unsafe_allow_html=True)


def feature_card(col, icon, title, desc, color):
    col.markdown(f"""
    <div style='background:{CARD_BG};border:1px solid {BORDER};
                border-radius:12px;padding:16px;height:118px'>
        <div style='font-size:22px'>{icon}</div>
        <div style='font-size:14px;font-weight:700;color:{TEXT};margin-top:6px'>{title}</div>
        <div style='font-size:11.5px;color:{SUBTEXT};margin-top:4px;line-height:1.5'>{desc}</div>
    </div>""", unsafe_allow_html=True)


def show():
    df = load_full()
    kpis = load_kpis(df)
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

    # ── Hero ──────────────────────────────────────────
    st.markdown(f"""
    <div style='background:{CARD_BG};border:1px solid {BORDER};border-radius:16px;
                padding:30px 32px;margin-bottom:18px;text-align:center'>
        <div style='font-size:46px'>📡</div>
        <div style='font-size:28px;font-weight:800;color:{TEXT};margin-top:6px'>
            Telecom Churn Intelligence
        </div>
        <div style='font-size:14px;color:{SUBTEXT};margin-top:8px;max-width:680px;
                    margin-left:auto;margin-right:auto;line-height:1.6'>
            A data-driven look at why telecom customers leave — combining executive KPIs,
            customer & revenue segmentation, and a machine learning model to flag
            at-risk customers before they churn.
        </div>
        <div style='font-size:11px;color:{SUBTEXT};margin-top:14px;
                    background:{BG};display:inline-block;padding:5px 14px;
                    border-radius:20px;border:1px solid {BORDER}'>
            DEPI — Data Analysis Track &nbsp;•&nbsp; Instructor: Amal Mahmoud
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Headline stats ────────────────────────────────
    s1, s2, s3, s4 = st.columns(4)
    stat_chip(s1, "Total Customers", f"{kpis['total_customers']:,}", BLUE)
    stat_chip(s2, "Churn Rate", f"{kpis['churn_rate']}%", RED)
    stat_chip(s3, "Total Revenue", f"${kpis['total_revenue']/1e6:.1f}M", GREEN)
    stat_chip(s4, "Avg Tenure", f"{kpis['avg_tenure']} mo", GOLD)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    # ── What's inside ─────────────────────────────────
    st.markdown(f"<div style='font-size:13px;font-weight:600;color:{SUBTEXT};"
                f"text-transform:uppercase;letter-spacing:.06em;margin-bottom:10px'>"
                f"Explore from the sidebar</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    feature_card(c1, "📊", "Executive Dashboard",
                 "High-level churn KPIs, contract & tenure trends, top churn reasons and geography.",
                 TEAL)
    feature_card(c2, "👥", "Customer & Revenue",
                 "Demographic breakdowns, revenue impact, payment methods and service usage.",
                 BLUE)
    feature_card(c3, "🧠", "ML Prediction",
                 "A Random Forest model that scores any customer's churn risk in real time.",
                 ORANGE)

    st.markdown(f"""
    <div style='text-align:center;color:{SUBTEXT};font-size:11px;margin-top:22px'>
        Salma · Marwa · Noor · Shahd · Mariam
    </div>""", unsafe_allow_html=True)