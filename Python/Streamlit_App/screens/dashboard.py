import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys
import os

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
    <style>
    .block-container {{
    padding-top: 4rem !important;
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


def kpi_card(col, label, value, color=TEAL, help_text=None):
    title_attr = f' title="{help_text}"' if help_text else ''
    col.markdown(f"""
    <div class='kpi-card' style='background:{CARD_BG};border:1px solid {BORDER};
                border-top:4px solid {color};border-radius:12px;
                padding:10px 12px;text-align:center;height:74px'{title_attr}>
        <div style='font-size:10px;color:{SUBTEXT};margin-bottom:5px;
                    text-transform:uppercase;font-weight:800;letter-spacing:.04em'>{label}</div>
        <div style='font-size:22px;font-weight:900;color:{color}'>{value}</div>
    </div>
    """, unsafe_allow_html=True)


def show():
    compact_css()
    df_full = load_full()
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

    # Header
    st.markdown(f"""
    <div style='background:{CARD_BG};border:1px solid {BORDER};border-radius:13px;
                padding:14px 18px;margin-bottom:8px'>
        <div style='font-size:22px;font-weight:900;color:{TEXT}'>
            📡 Telecom Churn Intelligence
        </div>
        <div style='font-size:12px;color:{SUBTEXT};margin-top:3px'>
            Executive Dashboard — 7,043 Customer Records
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Filters
    f1, f2, f3, f4 = st.columns([3, 3, 3, 1])

    with f1:
        contract_f = st.multiselect(
            "Contract Type",
            df_full['Contract'].unique().tolist(),
            default=df_full['Contract'].unique().tolist(),
            key='dash_contract_filter'
        )

    with f2:
        gender_f = st.multiselect(
            "Gender",
            df_full['gender'].unique().tolist(),
            default=df_full['gender'].unique().tolist(),
            key='dash_gender_filter'
        )

    with f3:
        senior_f = st.multiselect(
            "Senior Citizen",
            [0, 1],
            format_func=lambda x: "Senior" if x == 1 else "Non-Senior",
            default=[0, 1],
            key='dash_senior_filter'
        )

    with f4:
        st.markdown("<div style='height:17px'></div>", unsafe_allow_html=True)
        if st.button("🔄 Reset", key='dash_reset_btn', width='stretch'):
            for k in ['dash_contract_filter', 'dash_gender_filter', 'dash_senior_filter']:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

    df = df_full[
        df_full['Contract'].isin(contract_f) &
        df_full['gender'].isin(gender_f) &
        df_full['SeniorCitizen'].isin(senior_f)
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
            file_name="executive_dashboard_filtered.csv",
            mime='text/csv',
            key='dash_download_btn',
            width='stretch'
        )

    kpis = load_kpis(df)

    # KPI Row
    k1, k2, k3, k4, k5 = st.columns(5)

    kpi_card(k1, "Total Customers", f"{kpis['total_customers']:,}", BLUE, "Full dataset")
    kpi_card(k2, "Churned", f"{kpis['churned']:,}", RED, "Lost customers")
    kpi_card(k3, "Churn Rate", f"{kpis['churn_rate']}%", RED, "Of total base")
    kpi_card(k4, "Total Revenue", f"${kpis['total_revenue']/1e6:.1f}M", GREEN, "All customers")
    kpi_card(k5, "Revenue Lost", f"${kpis['revenue_lost']/1e6:.1f}M", ORANGE, "Revenue lost from churned customers")

    # Main dashboard layout like Customer page
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

    left, mid, right = st.columns([1.05, 1.15, 2.25])

    # LEFT COLUMN
    with left:
        chart_title("Top 5 Cities by Churn Count")

        cdf_city = (
            df[df['churn'] == 'Yes']
            .groupby('City')
            .size()
            .reset_index(name='Churn_Count')
            .sort_values('Churn_Count', ascending=False)
            .head(5)
            .sort_values('Churn_Count', ascending=True)
        )

        fig0 = go.Figure(go.Bar(
            x=cdf_city['Churn_Count'],
            y=cdf_city['City'],
            orientation='h',
            marker_color=RED,
            marker_line_width=0,
            text=cdf_city['Churn_Count'],
            textposition='outside',
            textfont=dict(color=TEXT, size=10),
            cliponaxis=False,
            hovertemplate='%{y}<br>Churned Customers: %{x}<extra></extra>'
        ))

        max_city = cdf_city['Churn_Count'].max() if not cdf_city.empty else 1

        fig0.update_layout(
            **BASE,
            height=150,
            xaxis=dict(**AX, range=[0, max_city * 1.28]),
            yaxis=dict(**AX),
            margin=dict(t=6, b=18, l=95, r=45)
        )

        st.plotly_chart(fig0, width='stretch', config={'displayModeBar': False})

        chart_title("Churn Vs Retention by Contract")

        cdf = (
            df.groupby('Contract')
            .apply(lambda x: round(100 * (x['churn'] == 'Yes').sum() / len(x), 1), include_groups=False)
            .reset_index(name='Churn_Rate')
            .sort_values('Churn_Rate', ascending=False)
        )
        cdf['Retain_Rate'] = (100 - cdf['Churn_Rate']).round(1)

        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=cdf['Contract'],
            y=cdf['Retain_Rate'],
            name='Retained',
            marker_color=TEAL,
            marker_line_width=0,
            text=[f"{v}%" for v in cdf['Retain_Rate']],
            textposition='outside',
            textfont=dict(color=TEXT, size=10),
            cliponaxis=False
        ))
        fig1.add_trace(go.Bar(
            x=cdf['Contract'],
            y=cdf['Churn_Rate'],
            name='Churned',
            marker_color=RED,
            marker_line_width=0,
            text=[f"{v}%" for v in cdf['Churn_Rate']],
            textposition='outside',
            textfont=dict(color=TEXT, size=10),
            cliponaxis=False
        ))

        fig1.update_layout(
        **BASE,
        height=200,
        barmode='group',
        bargap=0.3,
         bargroupgap=0.1,
          xaxis=dict(**AX),
          yaxis=dict(**AX, range=[0, 115], title=''),
        legend=dict(
         title=None,
         font=dict(color=TEXT, size=10),
         orientation='h',
         x=0.98,
         y=1.28,
         xanchor='right',
         yanchor='top',
         bgcolor='rgba(0,0,0,0)'
       ),
       margin=dict(t=35, b=41, l=25, r=5)
       )       

        st.plotly_chart(fig1, width='stretch', config={'displayModeBar': False})

    # MIDDLE COLUMN
    with mid:
        chart_title("Churn by Tenure")

        TORDER = ['0-12 months', '13-24 months', '25-48 months', '49-72 months']
        tdf = (
            df.groupby('Tenure_Group')
            .apply(lambda x: round(100 * (x['churn'] == 'Yes').sum() / len(x), 1), include_groups=False)
            .reset_index(name='Churn_Rate')
        )
        tdf['Tenure_Group'] = pd.Categorical(tdf['Tenure_Group'], categories=TORDER, ordered=True)
        tdf = tdf.sort_values('Tenure_Group')
        tdf['Retain_Rate'] = (100 - tdf['Churn_Rate']).round(1)

        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=tdf['Tenure_Group'],
            y=tdf['Retain_Rate'],
            mode='lines+markers+text',
            name='Retained',
            line=dict(color=TEAL, width=3),
            marker=dict(size=9, color=TEAL),
            text=[f"{v}%" for v in tdf['Retain_Rate']],
            textposition='top center',
            textfont=dict(color=TEXT, size=11),
            hovertemplate='%{x}<br>Retained: %{y:.1f}%<extra></extra>'
        ))
        fig3.add_trace(go.Scatter(
            x=tdf['Tenure_Group'],
            y=tdf['Churn_Rate'],
            mode='lines+markers+text',
            name='Churned',
            line=dict(color=RED, width=3),
            marker=dict(size=9, color=RED),
            text=[f"{v}%" for v in tdf['Churn_Rate']],
            textposition='bottom center',
            textfont=dict(color=TEXT, size=11),
            hovertemplate='%{x}<br>Churned: %{y:.1f}%<extra></extra>'
        ))

        fig3.update_layout(
            **BASE,
            height=330,
            xaxis=dict(**AX, tickangle=0),
            yaxis=dict(**AX, range=[0, 105]),
            legend=dict(
                title=None,
                orientation='h',
                font=dict(size=10, color=TEXT),
                x=0.5,
                y=1.08,
                xanchor='center'
            ),
            margin=dict(t=18, b=45, l=35, r=15)
        )

        st.plotly_chart(fig3, width='stretch', config={'displayModeBar': False})

    # RIGHT SIDE: DONUT + REASONS SIDE BY SIDE, INSIGHTS UNDER THEM
    with right:
        donut_col, reasons_col = st.columns([1.05, 1.15])

        with donut_col:
            chart_title("Churn Category Breakdown")

            catdf = (
                df[df['churn'] == 'Yes']
                .query("Churn_Category != 'No churn'")
                .groupby('Churn_Category')
                .size()
                .reset_index(name='Count')
                .sort_values('Count', ascending=False)
            )

            total_cat = int(catdf['Count'].sum()) if not catdf.empty else 0
            if total_cat > 0:
                catdf['Percent'] = (catdf['Count'] / total_cat * 100).round(1)
                donut_text = [f"{p}%" for p in catdf['Percent']]
            else:
                catdf['Percent'] = 0
                donut_text = []

            fig2 = go.Figure(go.Pie(
                labels=catdf['Churn_Category'],
                values=catdf['Count'],
                hole=0.52,
                marker=dict(
                    colors=[RED, ORANGE, GOLD, TEAL, BLUE],
                    line=dict(color=BG, width=2)
                ),
                text=donut_text,
                textinfo='text',
                textposition='inside',
                insidetextorientation='horizontal',
                textfont=dict(color=TEXT, size=11),
                domain=dict(x=[0.00, 0.70], y=[0.2, 1.00]),
                hovertemplate='%{label}<br>%{value} customers (%{percent})<extra></extra>'
            ))

            fig2.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=TEXT, size=10),
                showlegend=True,
                legend=dict(
                    title=None,
                    orientation='v',
                    font=dict(color=TEXT, size=9),
                    x=0.76,
                    y=0.50,
                    xanchor='left',
                    yanchor='middle'
                ),
                margin=dict(t=0, b=0, l=0, r=0),
                height=275,
                annotations=[dict(
                    text=f"{total_cat:,}",
                    x=0.35,
                    y=0.60,
                    showarrow=False,
                    font=dict(size=18, color=TEXT)
                )]
            )

            st.plotly_chart(fig2, width='stretch', config={'displayModeBar': False})

        with reasons_col:
            chart_title("Top 5 Churn Reasons")

            rdf = (
                df[df['churn'] == 'Yes']
                .query("Churn_Reason != 'No churn'")
                .groupby('Churn_Reason')
                .size()
                .reset_index(name='Count')
                .sort_values('Count', ascending=True)
                .tail(5)
            )

            fig4 = go.Figure(go.Bar(
                x=rdf['Count'],
                y=rdf['Churn_Reason'],
                orientation='h',
                marker_color=GOLD,
                marker_line_width=0,
                text=rdf['Count'],
                textposition='outside',
                textfont=dict(color=TEXT, size=10),
                cliponaxis=False,
                hovertemplate='%{y}<br>Customers: %{x}<extra></extra>'
            ))

            max_reason = rdf['Count'].max() if not rdf.empty else 1

            fig4.update_layout(
                **BASE,
                height=275,
                xaxis=dict(**AX, range=[0, max_reason * 1.28]),
                yaxis=dict(**AX),
                margin=dict(t=4, b=44, l=150, r=34)
            )

            st.plotly_chart(fig4, width='stretch', config={'displayModeBar': False})

        insight_left, insight_right = st.columns([1.05, 1.15])

        with insight_left:
           st.markdown(f"""
           <div style='margin-top:-49px'>
           <div class='chart-title' style='margin-bottom:10px'>Key Insights</div>

           <div style='font-size:11px;color:{TEXT};line-height:1.5;padding:0 0 0 4px'>
            <div style='background:rgba(251,113,133,0.08);border-left:3px solid {RED};
                        border-radius:8px;padding:8px 10px;margin-bottom:8px'>
                🔻 <b>Month-to-Month:</b><br>
                Highest churn risk segment.
             </div>
                <div style='background:rgba(251,113,133,0.08);border-left:3px solid {RED};
                            border-radius:8px;padding:8px 10px'>
                    🔻 <b>First 12 Months:</b><br>
                    Needs stronger onboarding.
                </div>
            </div>
            """, unsafe_allow_html=True)

        with insight_right:
         st.markdown(f"""
         <div style='margin-top:-20px'>
          <div style='font-size:11px;color:{TEXT};line-height:1.5;padding:0 0 0 4px'>
            <div style='background:rgba(52,211,153,0.08);border-left:3px solid {GREEN};
                        border-radius:8px;padding:8px 10px;margin-bottom:8px'>
                ▲ <b>Two-Year Contracts:</b><br>
                Stronger retention.
            </div>
            <div style='background:rgba(251,191,36,0.08);border-left:3px solid {GOLD};
                        border-radius:8px;padding:8px 10px'>
                ▲ <b>Competitor Impact:</b><br>
                Needs pricing action.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
