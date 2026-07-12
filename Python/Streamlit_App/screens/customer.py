import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.load_data import load_full

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

AX = dict(
    showgrid=False,
    zeroline=False,
    tickfont=dict(color=SUBTEXT, size=10)
)

BASE = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color=TEXT, family='Inter, sans-serif', size=10),
)


def compact_css():
    st.markdown(f"""
    <style>
    .block-container {{
    padding-top: 0.5rem !important;
    padding-left: 1.6rem !important;
    padding-right: 1.6rem !important;
    padding-bottom: 0rem !important;
                
    }}

    div[data-testid="stVerticalBlock"] {{
        gap: 0.3rem !important;
    }}

    div[data-testid="column"] {{
        gap: 0.4rem !important;
    }}

    label {{
        font-size: 10px !important;
        margin-bottom: 0px !important;
    }}

    .stMultiSelect, .stSelectbox {{
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }}

    [data-testid="stMultiSelect"] {{
        min-height: 30px !important;
    }}

    .stButton > button,
    .stDownloadButton > button {{
        padding: 5px 10px !important;
        min-height: 30px !important;
        font-size: 11px !important;
    }}

    .chart-title {{
        font-size: 15px;
        font-weight: 800;
        color: {TEXT};
        letter-spacing: .01em;
        margin-top: 0px;
        margin-bottom: 14px;
        text-align: left;
        border-left: 3px solid {TEAL};
        padding: 2px 0 2px 10px;
        line-height: 1.3;
    }}
    </style>
    """, unsafe_allow_html=True)


def chart_title(t):
    st.markdown(
        f"<div class='chart-title'>{t}</div>",
        unsafe_allow_html=True
    )


def section_title(t):
    st.markdown(
        f"<div style='font-size:14px;font-weight:800;color:{TEXT};"
        f"margin:14px 0 14px;padding-left:8px;border-left:4px solid {TEAL}'>{t}</div>",
        unsafe_allow_html=True
    )


def kpi_mini(col, label, value, color=TEAL):
    col.markdown(f"""
    <div class='kpi-card' style='background:{CARD_BG};border:1px solid {BORDER};
                border-top:4px solid {color};border-radius:12px;
                padding:10px 12px;text-align:center;height:74px'>
        <div style='font-size:10px;color:{SUBTEXT};margin-bottom:5px;
                    text-transform:uppercase;font-weight:800;letter-spacing:.04em'>{label}</div>
        <div style='font-size:22px;font-weight:900;color:{color}'>{value}</div>
    </div>
    """, unsafe_allow_html=True)


def start_card():
    pass


def end_card():
    pass


def show():
    compact_css()
    df = load_full()
    st.markdown("<div style='height:35px'></div>", unsafe_allow_html=True)

    # Header
    st.markdown(f"""
    <div style='background:{CARD_BG};border:1px solid {BORDER};border-radius:13px;
                padding:14px 18px;margin-bottom:8px'>
        <div style='font-size:22px;font-weight:900;color:{TEXT}'>
            👥 Customer & Revenue Analytics
        </div>
        <div style='font-size:12px;color:{SUBTEXT};margin-top:3px'>
            Who is at risk — and what does it cost?
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Filters
    f1, f2, f3, f4 = st.columns([3, 3, 3, 1])

    with f1:
        contract_f = st.multiselect(
            "Contract Type",
            df['Contract'].unique().tolist(),
            default=df['Contract'].unique().tolist(),
            key='cust_contract_filter'
        )

    with f2:
        gender_f = st.multiselect(
            "Gender",
            df['gender'].unique().tolist(),
            default=df['gender'].unique().tolist(),
            key='cust_gender_filter'
        )

    with f3:
        senior_f = st.multiselect(
            "Senior Citizen",
            [0, 1],
            format_func=lambda x: "Senior" if x == 1 else "Non-Senior",
            default=[0, 1],
            key='cust_senior_filter'
        )

    with f4:
        st.markdown("<div style='height:17px'></div>", unsafe_allow_html=True)
        if st.button("🔄 Reset", key='cust_reset_btn', width='stretch'):
            for k in ['cust_contract_filter', 'cust_gender_filter', 'cust_senior_filter']:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

    df = df[
        df['Contract'].isin(contract_f) &
        df['gender'].isin(gender_f) &
        df['SeniorCitizen'].isin(senior_f)
    ]

    cs1, cs2 = st.columns([5, 1])
    with cs1:
        st.markdown(
            f"<p style='color:{SUBTEXT};font-size:10px;margin:0'>Showing {len(df):,} customers</p>",
            unsafe_allow_html=True
        )
    with cs2:
        st.download_button(
            "⬇️ CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name="customer_revenue_filtered.csv",
            mime='text/csv',
            key='cust_download_btn',
            width='stretch'
        )

    # KPI Row
    m1, m2, m3, m4 = st.columns(4)

    senior_churn = round(
        100 * (df[df['SeniorCitizen'] == 1]['churn'] == 'Yes').sum() /
        max(len(df[df['SeniorCitizen'] == 1]), 1), 1
    )

    married_rev = df[df['Married'] == 'Married']['Total_Revenue'].mean()
    non_mar_rev = df[df['Married'] != 'Married']['Total_Revenue'].mean()
    rev_lost = df[df['churn'] == 'Yes']['Total_Revenue'].sum()

    kpi_mini(m1, "Senior Churn Rate", f"{senior_churn}%", RED)
    kpi_mini(m2, "Avg Rev — Married", f"${married_rev:,.0f}", GREEN)
    kpi_mini(m3, "Avg Rev — Not Married", f"${non_mar_rev:,.0f}", BLUE)
    kpi_mini(m4, "Revenue Lost", f"${rev_lost/1e6:.2f}M", ORANGE)

    # Main dashboard layout like Excel
    
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

    left, mid, right = st.columns([1.05, 1.15, 1.45])    

    # LEFT COLUMN
    with left:
        start_card()
        chart_title("Avg Revenue by Married Status")

        mdf = (
            df.groupby('Married')['Total_Revenue']
            .mean()
            .reset_index(name='Avg_Revenue')
            .sort_values('Avg_Revenue', ascending=True)
        )

        fig1 = go.Figure(go.Bar(
            x=mdf['Avg_Revenue'],
            y=mdf['Married'],
            orientation='h',
            marker_color=[BLUE, GREEN],
            text=[f"${v/1000:.1f}K" for v in mdf['Avg_Revenue']],
            textposition='outside',
            textfont=dict(color=TEXT, size=11),
            cliponaxis=False
        ))

        fig1.update_layout(
            **BASE,
            height=150,
            xaxis=dict(**AX),
            yaxis=dict(**AX),
            margin=dict(t=6, b=12, l=75, r=45)
        )
        st.plotly_chart(fig1, width='stretch', config={'displayModeBar': False})
        end_card()

        start_card()
        chart_title("Churn Rate: Senior Vs Non-Senior")

        sdf = (
            df.assign(Senior=df['SeniorCitizen'].map({1: 'Senior', 0: 'Non-Senior'}))
            .groupby('Senior')
            .apply(lambda x: round(100 * (x['churn'] == 'Yes').sum() / len(x), 1),
                   include_groups=False)
            .reset_index(name='Churn_Rate')
            .sort_values('Churn_Rate', ascending=False)
        )
        sdf['Retain_Rate'] = (100 - sdf['Churn_Rate']).round(1)

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=sdf['Senior'],
            y=sdf['Retain_Rate'],
            name='No',
            marker_color=TEAL,
            text=[f"{v}%" for v in sdf['Retain_Rate']],
            textposition='outside',
            textfont=dict(color=TEXT, size=10)
        ))
        fig2.add_trace(go.Bar(
            x=sdf['Senior'],
            y=sdf['Churn_Rate'],
            name='Yes',
            marker_color=RED,
            text=[f"{v}%" for v in sdf['Churn_Rate']],
            textposition='outside',
            textfont=dict(color=TEXT, size=10)
        ))

        fig2.update_layout(
            **BASE,
            height=175,
            barmode='group',
            xaxis=dict(**AX),
            yaxis=dict(**AX, range=[0, 100]),
            legend=dict(title=None, font=dict(size=10, color=TEXT), x=0.78, y=1.10),
            margin=dict(t=8, b=38, l=30, r=5)
        )
        st.plotly_chart(fig2, width='stretch', config={'displayModeBar': False})
        end_card()

    # MIDDLE COLUMN
    with mid:
        start_card()
        chart_title("Revenue Lost by Churn Category")

        rldf = (
            df[df['churn'] == 'Yes']
            .query("Churn_Category != 'No churn'")
            .groupby('Churn_Category')['Total_Revenue']
            .sum()
            .reset_index(name='Revenue_Lost')
            .sort_values('Revenue_Lost', ascending=False)
        )

        fig3 = go.Figure(go.Pie(
            labels=rldf['Churn_Category'],
            values=rldf['Revenue_Lost'],
            hole=0.58,
            marker=dict(
                colors=[RED, ORANGE, GOLD, TEAL, BLUE],
                line=dict(color=BG, width=2)
            ),
            textfont=dict(color=TEXT, size=10),
            textinfo='percent',
            domain=dict(x=[0.08, 0.62], y=[0, 1])
        ))

        fig3.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=TEXT, size=10),
            showlegend=True,
            legend=dict(
                title=None,
                font=dict(color=TEXT, size=10),
                x=0.68,
                y=0.5,
                xanchor='left',
                yanchor='middle',
            ),
            margin=dict(t=0, b=0, l=0, r=0),
            height=330,
            annotations=[dict(
                text=f"${rldf['Revenue_Lost'].sum()/1e6:.2f}M",
                x=0.35,
                y=0.5,
                showarrow=False,
                font=dict(size=18, color=TEXT)
            )]
        )
        st.plotly_chart(fig3, width='stretch', config={'displayModeBar': False})
        end_card()

    # RIGHT COLUMN
    with right:
        r1, r2 = st.columns([1, 1.35])

        with r1:
            start_card()
            chart_title("Revenue by Payment Method")

            pdf = (
                df.groupby('Payment_Method')['Total_Revenue']
                .sum()
                .reset_index(name='Revenue')
                .sort_values('Revenue', ascending=False)
            )

            pdf['Payment_Method_Wrapped'] = pdf['Payment_Method'].str.replace(' ', '<br>')

            fig4 = go.Figure(go.Bar(
                x=pdf['Payment_Method_Wrapped'],
                y=pdf['Revenue'],
                marker_color=TEAL,
                text=[f"${v/1e6:.1f}M" if v >= 1e6 else f"${v/1000:.0f}K" for v in pdf['Revenue']],
                textposition='outside',
                textfont=dict(color=TEXT, size=10)
            ))

            fig4.update_layout(
                **BASE,
                height=150,
                xaxis=dict(**AX, tickangle=0),
                yaxis=dict(**AX),
                margin=dict(t=8, b=45, l=25, r=5)
            )
            st.plotly_chart(fig4, width='stretch', config={'displayModeBar': False})
            end_card()

        with r2:
            start_card()
            chart_title("Churn Rate Analysis by Age Group")

            AGE_ORDER = ['18-30', '31-45', '46-60', '60+']
            adf = (
                df.groupby('Age_Group')
                .apply(lambda x: round(100 * (x['churn'] == 'Yes').sum() / len(x), 1),
                       include_groups=False)
                .reset_index(name='Churn_Rate')
            )
            adf['Age_Group'] = pd.Categorical(adf['Age_Group'], categories=AGE_ORDER, ordered=True)
            adf = adf.sort_values('Age_Group')
            adf['Retain_Rate'] = (100 - adf['Churn_Rate']).round(1)

            fig5 = go.Figure()
            fig5.add_trace(go.Bar(
                x=adf['Age_Group'],
                y=adf['Retain_Rate'],
                name='No',
                marker_color=TEAL,
                text=[f"{v}%" for v in adf['Retain_Rate']],
                textposition='outside',
                textfont=dict(color=TEXT, size=10)
            ))
            fig5.add_trace(go.Bar(
                x=adf['Age_Group'],
                y=adf['Churn_Rate'],
                name='Yes',
                marker_color=RED,
                text=[f"{v}%" for v in adf['Churn_Rate']],
                textposition='outside',
                textfont=dict(color=TEXT, size=10)
            ))

            fig5.update_layout(
                **BASE,
                height=150,
                barmode='group',
                xaxis=dict(**AX),
                yaxis=dict(**AX, range=[0, 100]),
                legend=dict(title=None, font=dict(size=10, color=TEXT), x=0.82, y=1.10),
                margin=dict(t=8, b=20, l=25, r=5)
            )
            st.plotly_chart(fig5, width='stretch', config={'displayModeBar': False})
            end_card()

        r3, r4 = st.columns([1, 1])

        with r3:
            start_card()
            chart_title("Tech Support Requested by Internet Type")

            st.markdown(f"""
            <div style='display:flex;gap:14px;align-items:center;
                        margin-top:-15px;margin-bottom:-18px;margin-left:110px;
                        font-size:10px;color:{TEXT}'>
                <span style='display:flex;align-items:center;gap:4px'>
                    <span style='width:8px;height:8px;background:{RED};
                                 display:inline-block;border-radius:1px'></span>
                    Yes
                </span>
                <span style='display:flex;align-items:center;gap:4px'>
                    <span style='width:8px;height:8px;background:{TEAL};
                                 display:inline-block;border-radius:1px'></span>
                    No
                </span>
            </div>
            """, unsafe_allow_html=True)

            tdf = (
                df[df['Internet_Service'] == 'Yes']
                .groupby(['Internet_Type', 'Premium_Tech_Support'])
                .size()
                .reset_index(name='Count')
            )

            no_df = tdf[tdf['Premium_Tech_Support'] == 'No']
            yes_df = tdf[tdf['Premium_Tech_Support'] == 'Yes']

            fig6 = go.Figure()
            fig6.add_trace(go.Bar(
                x=no_df['Internet_Type'],
                y=no_df['Count'],
                name='No',
                marker_color=TEAL,
                text=no_df['Count'],
                textposition='inside',
                textfont=dict(color='white', size=13)
            ))
            fig6.add_trace(go.Bar(
                x=yes_df['Internet_Type'],
                y=yes_df['Count'],
                name='Yes',
                marker_color=RED,
                text=yes_df['Count'],
                textposition='inside',
                textfont=dict(color='white', size=13)
            ))

            fig6.update_layout(
                **BASE,
                height=215,
                barmode='stack',
                xaxis=dict(**AX),
                yaxis=dict(**AX, domain=[0.10, 1.0]),
                showlegend=False,
                margin=dict(t=0, b=70, l=25, r=5)
            )
            st.plotly_chart(fig6, width='stretch', config={'displayModeBar': False})
            end_card()

        with r4:
            start_card()
            chart_title("Key Recommendations")

            st.markdown(f"""
            <div style='font-size:11.5px;color:{TEXT};line-height:1.55;padding:4px 6px;margin-top:-5px'>
                <div style='margin-bottom:5px'>
                    🔻 <b>Senior Citizens Retention:</b><br>
                    Senior churn is <b>41.7%</b>, so they need special retention offers.
                </div>
                <div style='margin-bottom:5px'>
                    🔻 <b>Competitor Impact:</b><br>
                    Competitors caused around <b>$1.69M</b> revenue loss.
                </div>
                <div style='margin-bottom:5px'>
                    ▲ <b>Premium Segment:</b><br>
                    Married customers average <b>$4,010</b> revenue.
                </div>
                <div>
                    ▲ <b>Security Service:</b><br>
                    Online security can reduce churn risk clearly.
                </div>
            </div>
            """, unsafe_allow_html=True)
            end_card()