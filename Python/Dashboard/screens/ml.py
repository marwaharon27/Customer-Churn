import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (confusion_matrix, roc_curve,
                              auc, classification_report)
from sklearn.preprocessing import LabelEncoder
import sys, os
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

BASE = dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=TEXT, family='Inter, sans-serif'),
            margin=dict(t=10, b=28, l=40, r=20))
AX   = dict(gridcolor=BORDER, zerolinecolor=BORDER, tickfont=dict(color=SUBTEXT))


def chart_title(t):
    st.markdown(f"<div style='font-size:12px;font-weight:600;color:{SUBTEXT};"
                f"text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px'>{t}</div>",
                unsafe_allow_html=True)

def section_title(t):
    st.markdown(f"<div style='font-size:16px;font-weight:600;color:{TEXT};"
                f"margin:14px 0 8px;padding-left:10px;border-left:3px solid {TEAL}'>{t}</div>",
                unsafe_allow_html=True)

def kpi_card(col, label, value, sub=None, color=TEAL, help_text=None):
    title_attr = f' title="{help_text}"' if help_text else ''
    col.markdown(f"""
    <div class='kpi-card' style='background:{CARD_BG};border:1px solid {BORDER};
                border-top:3px solid {color};border-radius:12px;
                padding:12px 17px;text-align:center'{title_attr}>
        <div style='font-size:11px;color:{SUBTEXT};margin-bottom:6px;
                    text-transform:uppercase;letter-spacing:.05em'>{label}</div>
        <div style='font-size:24px;font-weight:700;color:{color}'>{value}</div>
        {'<div style="font-size:11px;color:'+SUBTEXT+';margin-top:4px">'+sub+'</div>' if sub else ''}
    </div>""", unsafe_allow_html=True)


@st.cache_resource
def train_model(df):
    features = [
        'tenure', 'monthly_charges', 'Total_Revenue',
        'SeniorCitizen', 'Number_of_Referrals',
        'Contract', 'Internet_Type', 'Payment_Method',
        'Online_Security', 'Premium_Tech_Support', 'Married'
    ]
    df_ml = df[features + ['churn']].copy()
    df_ml['churn_binary'] = (df_ml['churn'] == 'Yes').astype(int)

    # Encode categoricals
    encoders = {}
    cat_cols = ['Contract', 'Internet_Type', 'Payment_Method',
                'Online_Security', 'Premium_Tech_Support', 'Married']
    for col in cat_cols:
        le = LabelEncoder()
        df_ml[col] = le.fit_transform(df_ml[col].astype(str))
        encoders[col] = le

    X = df_ml[features]
    y = df_ml['churn_binary']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    model = RandomForestClassifier(
        n_estimators=100, random_state=42, n_jobs=-1
    )
    model.fit(X_train, y_train)

    return model, X_test, y_test, features, encoders


def show():
    df = load_full()
    st.markdown("<div style='height:35px'></div>", unsafe_allow_html=True)

    # ── Header ────────────────────────────────────────
    st.markdown(f"""
    <div style='background:{CARD_BG};border:1px solid {BORDER};border-radius:14px;
                padding:14px 22px;margin-bottom:14px'>
        <div style='font-size:22px;font-weight:700;color:{TEXT}'>
            🧠 ML Churn Prediction
        </div>
        <div style='font-size:13px;color:{SUBTEXT};margin-top:4px'>
            Random Forest Model — Predict which customers will churn
        </div>
    </div>""", unsafe_allow_html=True)

    with st.spinner("Training model..."):
        model, X_test, y_test, features, encoders = train_model(df)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    accuracy = round(100 * (y_pred == y_test).mean(), 1)

    # ── MODEL KPIs ────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    kpi_card(k1, "Model Accuracy",    f"{accuracy}%",          "On held-out test set", TEAL,
             help_text="Percentage of test customers correctly classified by the model")
    kpi_card(k2, "Training Samples",  f"{len(X_test)*4:,}",    "80% of dataset",       BLUE,
             help_text="Number of customer records used to train the Random Forest model")
    kpi_card(k3, "Test Samples",      f"{len(X_test):,}",      "20% of dataset",       GOLD,
             help_text="Number of customer records held out to evaluate model performance")
    kpi_card(k4, "Features Used",     f"{len(features)}",      "Model inputs",         ORANGE,
             help_text="Number of customer attributes the model uses to predict churn")

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── ROW 1: Feature Importance + Confusion Matrix ──
    section_title("Model Performance")
    col1, col2 = st.columns(2)

    with col1:
        chart_title("Feature Importance")
        imp_df = pd.DataFrame({
            'Feature': features,
            'Importance': model.feature_importances_
        }).sort_values('Importance', ascending=True)

        fig1 = go.Figure(go.Bar(
            x=imp_df['Importance'], y=imp_df['Feature'], orientation='h',
            marker_color=TEAL, marker_line_width=0,
            text=[f"{v:.3f}" for v in imp_df['Importance']],
            textposition='outside', textfont=dict(color=TEXT, size=11),
            hovertemplate='%{y}<br>Importance: %{x:.3f}<extra></extra>'
        ))
        fig1.update_layout(**BASE, height=280,
                           xaxis=dict(**AX, title='Importance Score'),
                           yaxis=dict(**AX))
        st.plotly_chart(fig1, width='stretch')

    with col2:
        chart_title("Confusion Matrix")
        cm = confusion_matrix(y_test, y_pred)
        fig2 = px.imshow(
            cm,
            labels=dict(x="Predicted", y="Actual", color="Count"),
            x=['Not Churn', 'Churn'],
            y=['Not Churn', 'Churn'],
            color_continuous_scale=[[0, CARD_BG], [1, RED]],
            text_auto=True
        )
        fig2.update_traces(textfont=dict(color=TEXT, size=16))
        fig2.update_layout(**BASE, height=280,
                           xaxis=dict(tickfont=dict(color=SUBTEXT)),
                           yaxis=dict(tickfont=dict(color=SUBTEXT)),
                           coloraxis_colorbar=dict(tickfont=dict(color=SUBTEXT)))
        st.plotly_chart(fig2, width='stretch')

    # ── ROW 2: ROC Curve + Prediction ─────────────────
    section_title("Model Evaluation & Prediction")
    col3, col4 = st.columns(2)

    with col3:
        chart_title("ROC Curve")
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        roc_auc = auc(fpr, tpr)

        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=fpr, y=tpr, mode='lines',
            name=f'AUC = {roc_auc:.3f}',
            line=dict(color=TEAL, width=2.5),
            hovertemplate='FPR: %{x:.2f}<br>TPR: %{y:.2f}<extra></extra>'
        ))
        fig3.add_trace(go.Scatter(
            x=[0, 1], y=[0, 1], mode='lines',
            name='Random',
            line=dict(color=SUBTEXT, dash='dash'),
            hoverinfo='skip'
        ))
        fig3.update_layout(**BASE, height=280,
                           xaxis=dict(**AX, title='False Positive Rate'),
                           yaxis=dict(**AX, title='True Positive Rate'),
                           legend=dict(x=0.55, y=0.08, font=dict(color=TEXT),
                                       bgcolor='rgba(0,0,0,0)'))
        st.plotly_chart(fig3, width='stretch')

    with col4:
        chart_title("🎯 Predict a Customer")
        st.markdown(f"""
        <div style='background:{CARD_BG};border:1px solid {BORDER};
                    border-radius:12px;padding:16px 18px 4px'>
        """, unsafe_allow_html=True)

        tenure_in = st.slider("Tenure (months)", 1, 72, 12)
        charges_in = st.slider("Monthly Charges ($)", 20, 120, 65)
        contract_in = st.selectbox(
            "Contract", ['Month-to-Month', 'One Year', 'Two Year']
        )
        internet_in = st.selectbox(
            "Internet Type", ['Fiber Optic', 'Cable', 'DSL', 'None']
        )
        senior_in = st.selectbox(
            "Senior Citizen", [0, 1],
            format_func=lambda x: "Yes" if x == 1 else "No"
        )
        security_in = st.selectbox("Online Security", ['Yes', 'No'])

        predict_clicked = st.button("🔮 Predict Churn", width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

        if predict_clicked:
            sample = pd.DataFrame([{
                'tenure': tenure_in,
                'monthly_charges': charges_in,
                'Total_Revenue': charges_in * tenure_in,
                'SeniorCitizen': senior_in,
                'Number_of_Referrals': 0,
                'Contract': contract_in,
                'Internet_Type': internet_in,
                'Payment_Method': 'Bank Withdrawal',
                'Online_Security': security_in,
                'Premium_Tech_Support': 'No',
                'Married': 'Not Married'
            }])

            for col in ['Contract', 'Internet_Type', 'Payment_Method',
                        'Online_Security', 'Premium_Tech_Support', 'Married']:
                le = encoders[col]
                val = sample[col].iloc[0]
                if val in le.classes_:
                    sample[col] = le.transform([val])[0]
                else:
                    sample[col] = 0

            prob = model.predict_proba(sample)[0][1]
            risk = "🔴 HIGH RISK" if prob > 0.6 else \
                   "🟡 MEDIUM RISK" if prob > 0.35 else "🟢 LOW RISK"
            color = RED if prob > 0.6 else \
                    ORANGE if prob > 0.35 else GREEN

            st.markdown(f"""
            <div style='background:{color}15; border:2px solid {color};
                        border-radius:12px; padding:20px; text-align:center;
                        margin-top:12px'>
                <div style='font-size:32px; font-weight:700; color:{color}'>
                    {prob*100:.1f}%
                </div>
                <div style='font-size:14px; color:{color}; font-weight:600'>
                    Churn Probability
                </div>
                <div style='font-size:18px; margin-top:8px; color:{TEXT}'>{risk}</div>
            </div>
            """, unsafe_allow_html=True)