import os
import sys

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import auc, confusion_matrix, precision_score, recall_score, f1_score, roc_curve, accuracy_score
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.base import clone

from xgboost import XGBClassifier
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.under_sampling import RandomUnderSampler

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.load_data import load_full

# ── Colors ────────────────────────────────────────────
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

BASE = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color=TEXT, family='Inter, sans-serif'),
    margin=dict(t=10, b=28, l=40, r=20)
)
AX = dict(gridcolor=BORDER, zerolinecolor=BORDER, tickfont=dict(color=SUBTEXT))

# Raw columns needed from the loaded dataframe.
# Total_Revenue is kept for business ranking/revenue at risk,
# but the final best ML feature set does NOT use it directly.
RAW_FEATURES = [
    'tenure', 'monthly_charges', 'Total_Revenue',
    'SeniorCitizen', 'Number_of_Referrals',
    'Contract', 'Internet_Type', 'Payment_Method',
    'Online_Security', 'Premium_Tech_Support', 'Married'
]

CAT_COLS = [
    'Contract', 'Internet_Type', 'Payment_Method',
    'Online_Security', 'Premium_Tech_Support', 'Married'
]

BASE_NUM_COLS = [
    'tenure', 'monthly_charges',
    'SeniorCitizen', 'Number_of_Referrals'
]

ENGINEERED_NUM_COLS = [
    'Charges_x_Tenure',
    'No_Referrals_Flag',
    'New_Customer_Flag',
    'Low_Tenure_Flag',
    'Long_Tenure_Flag',
    'High_Charges_Flag',
    'Very_High_Charges_Flag',
    'Is_Month_to_Month',
    'Is_Fiber',
    'No_Security',
    'No_Tech_Support',
    'Risk_Combo_M2M_Fiber_NoSecurity',
    'Risk_Combo_M2M_NoSupport',
    'Risk_Combo_Full'
]

NUM_COLS = BASE_NUM_COLS + ENGINEERED_NUM_COLS
FEATURES = NUM_COLS + CAT_COLS
BEST_THRESHOLD = 0.66


# ── Small UI helpers ──────────────────────────────────
def chart_title(t):
    st.markdown(
        f"<div style='font-size:12px;font-weight:600;color:{SUBTEXT};"
        f"text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px'>{t}</div>",
        unsafe_allow_html=True
    )


def section_title(t):
    st.markdown(
        f"<div style='font-size:16px;font-weight:600;color:{TEXT};"
        f"margin:14px 0 8px;padding-left:10px;border-left:3px solid {TEAL}'>{t}</div>",
        unsafe_allow_html=True
    )


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


def insight_card(title, body, color=TEAL, icon="💡"):
    st.markdown(f"""
    <div style='background:{CARD_BG};border:1px solid {BORDER};border-left:4px solid {color};
                border-radius:12px;padding:14px 16px;margin-top:10px'>
        <div style='font-size:14px;font-weight:700;color:{TEXT};margin-bottom:6px'>{icon} {title}</div>
        <div style='font-size:12px;color:{SUBTEXT};line-height:1.65'>{body}</div>
    </div>
    """, unsafe_allow_html=True)


# ── ML helpers ────────────────────────────────────────
def _make_onehot_encoder():
    """Compatible with old/new sklearn versions."""
    try:
        return OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown='ignore', sparse=False)


def add_business_features(df_input):
    """Create the exact business feature set that won the diagnostics test."""
    df_ml = df_input.copy()

    # Numeric safety
    for col in ['tenure', 'monthly_charges', 'Total_Revenue', 'SeniorCitizen', 'Number_of_Referrals']:
        if col not in df_ml.columns:
            df_ml[col] = 0
        df_ml[col] = pd.to_numeric(df_ml[col], errors='coerce').fillna(0)

    for col in CAT_COLS:
        if col not in df_ml.columns:
            df_ml[col] = 'Unknown'
        df_ml[col] = df_ml[col].astype(str).fillna('Unknown')

    df_ml['Charges_x_Tenure'] = df_ml['monthly_charges'] * df_ml['tenure']
    df_ml['No_Referrals_Flag'] = (df_ml['Number_of_Referrals'] == 0).astype(int)
    df_ml['New_Customer_Flag'] = (df_ml['tenure'] <= 12).astype(int)
    df_ml['Low_Tenure_Flag'] = (df_ml['tenure'] <= 6).astype(int)
    df_ml['Long_Tenure_Flag'] = (df_ml['tenure'] >= 48).astype(int)

    median_charge = df_ml['monthly_charges'].median()
    q75_charge = df_ml['monthly_charges'].quantile(0.75)
    df_ml['High_Charges_Flag'] = (df_ml['monthly_charges'] >= median_charge).astype(int)
    df_ml['Very_High_Charges_Flag'] = (df_ml['monthly_charges'] >= q75_charge).astype(int)

    df_ml['Is_Month_to_Month'] = (df_ml['Contract'] == 'Month-to-Month').astype(int)
    df_ml['Is_Fiber'] = (df_ml['Internet_Type'] == 'Fiber Optic').astype(int)
    df_ml['No_Security'] = (df_ml['Online_Security'] == 'No').astype(int)
    df_ml['No_Tech_Support'] = (df_ml['Premium_Tech_Support'] == 'No').astype(int)

    df_ml['Risk_Combo_M2M_Fiber_NoSecurity'] = (
        (df_ml['Contract'] == 'Month-to-Month') &
        (df_ml['Internet_Type'] == 'Fiber Optic') &
        (df_ml['Online_Security'] == 'No')
    ).astype(int)

    df_ml['Risk_Combo_M2M_NoSupport'] = (
        (df_ml['Contract'] == 'Month-to-Month') &
        (df_ml['Premium_Tech_Support'] == 'No')
    ).astype(int)

    df_ml['Risk_Combo_Full'] = (
        (df_ml['Contract'] == 'Month-to-Month') &
        (df_ml['Internet_Type'] == 'Fiber Optic') &
        (df_ml['Online_Security'] == 'No') &
        (df_ml['Premium_Tech_Support'] == 'No')
    ).astype(int)

    return df_ml


def _clean_ml_frame(df):
    """Keep needed raw columns clean, then create engineered features."""
    df_ml = df[RAW_FEATURES + ['churn']].copy()
    df_ml = add_business_features(df_ml)
    df_ml['churn'] = df_ml['churn'].astype(str)
    return df_ml


def build_preprocessor():
    numeric_pipe = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
    ])
    categorical_pipe = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', _make_onehot_encoder()),
    ])
    return ColumnTransformer([
        ('num', numeric_pipe, NUM_COLS),
        ('cat', categorical_pipe, CAT_COLS),
    ])


def build_best_pipeline():
    """Best diagnostics result: XGBoost + RandomUnderSampler + business features without Total_Revenue."""
    return ImbPipeline([
        ('preprocess', build_preprocessor()),
        ('sampler', RandomUnderSampler(random_state=42)),
        ('model', XGBClassifier(
            n_estimators=280,
            max_depth=3,
            learning_rate=0.04,
            subsample=0.9,
            colsample_bytree=0.85,
            objective='binary:logistic',
            eval_metric='logloss',
            random_state=42,
            n_jobs=-1,
        )),
    ])


def aggregate_feature_importance(pipe, raw_features):
    """Aggregate one-hot importances back to readable raw feature names."""
    try:
        transformed_names = pipe.named_steps['preprocess'].get_feature_names_out()
        importances = pipe.named_steps['model'].feature_importances_
    except Exception:
        return np.ones(len(raw_features)) / max(len(raw_features), 1)

    scores = {f: 0.0 for f in raw_features}
    for name, imp in zip(transformed_names, importances):
        clean = name.replace('num__', '').replace('cat__', '')
        raw = clean
        for cat in CAT_COLS:
            if clean.startswith(cat + '_'):
                raw = cat
                break
        if raw in scores:
            scores[raw] += float(imp)

    values = np.array([scores.get(f, 0.0) for f in raw_features])
    total = values.sum()
    if total > 0:
        values = values / total
    return values


class ThresholdModel:
    """Wrapper so the app uses the tuned threshold instead of default 0.50."""
    def __init__(self, pipeline, threshold=BEST_THRESHOLD, feature_importances=None, cv_scores=None):
        self.pipeline = pipeline
        self.threshold = threshold
        self.feature_importances_ = feature_importances
        self.cv_scores_ = cv_scores or []

    def predict_proba(self, X):
        Xp = encode_features(X, FEATURES, None)
        return self.pipeline.predict_proba(Xp)

    def predict(self, X):
        prob = self.predict_proba(X)[:, 1]
        return (prob >= self.threshold).astype(int)

    def score(self, X, y):
        return accuracy_score(y, self.predict(X))


@st.cache_resource
def train_model(df):
    df_ml = _clean_ml_frame(df)
    df_ml['churn_binary'] = (df_ml['churn'] == 'Yes').astype(int)

    # Keep encoders only for safe dropdown fallbacks and allowed value checks.
    encoders = {}
    for col in CAT_COLS:
        le = LabelEncoder()
        le.fit(df_ml[col].astype(str))
        encoders[col] = le

    X = df_ml[FEATURES]
    y = df_ml['churn_binary']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipe = build_best_pipeline()
    pipe.fit(X_train, y_train)

    # 5-fold CV using the selected pipeline. This is for reliability display only.
    cv_scores = []
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    for tr_idx, val_idx in skf.split(X_train, y_train):
        cv_pipe = build_best_pipeline()
        cv_pipe.fit(X_train.iloc[tr_idx], y_train.iloc[tr_idx])
        val_prob = cv_pipe.predict_proba(X_train.iloc[val_idx])[:, 1]
        val_pred = (val_prob >= BEST_THRESHOLD).astype(int)
        cv_scores.append(accuracy_score(y_train.iloc[val_idx], val_pred))

    feature_importances = aggregate_feature_importance(pipe, FEATURES)
    model = ThresholdModel(pipe, threshold=BEST_THRESHOLD,
                           feature_importances=feature_importances,
                           cv_scores=cv_scores)

    return model, X_train, X_test, y_train, y_test, FEATURES, encoders


@st.cache_resource
def run_overfitting_check(_model, _X_train, _y_train, _X_test, _y_test):
    """Train vs Test accuracy gap + stored 5-Fold Cross Validation."""
    train_acc = round(100 * _model.score(_X_train, _y_train), 1)
    test_acc  = round(100 * _model.score(_X_test, _y_test), 1)
    gap = round(train_acc - test_acc, 1)

    cv_scores = getattr(_model, 'cv_scores_', []) or []
    cv_mean = round(100 * np.mean(cv_scores), 1) if cv_scores else test_acc
    cv_std = round(100 * np.std(cv_scores), 1) if cv_scores else 0.0

    is_overfitting = gap > 7

    return {
        'train_acc': train_acc,
        'test_acc': test_acc,
        'gap': gap,
        'cv_scores': [round(100 * s, 1) for s in cv_scores] if cv_scores else [test_acc],
        'cv_mean': cv_mean,
        'cv_std': cv_std,
        'is_overfitting': is_overfitting
    }


def encode_features(df_input, features, encoders=None):
    """Prepare raw/sample dataframe by creating business features and keeping final feature order."""
    df_encoded = df_input.copy()

    # Total_Revenue may not be used by the model, but it helps derive some legacy fields safely.
    if 'Total_Revenue' not in df_encoded.columns:
        df_encoded['Total_Revenue'] = pd.to_numeric(df_encoded.get('monthly_charges', 0), errors='coerce').fillna(0) * pd.to_numeric(df_encoded.get('tenure', 0), errors='coerce').fillna(0)

    df_encoded = add_business_features(df_encoded)

    for col in features:
        if col not in df_encoded.columns:
            df_encoded[col] = 0 if col in NUM_COLS else 'Unknown'

    return df_encoded[features]


def safe_option(encoders, col, preferred):
    classes = list(encoders[col].classes_)
    return preferred if preferred in classes else classes[0]


def risk_level(prob):
    if prob >= 0.60:
        return "High Risk"
    if prob >= 0.35:
        return "Medium Risk"
    return "Low Risk"


def risk_color(prob):
    if prob >= 0.60:
        return RED
    if prob >= 0.35:
        return ORANGE
    return GREEN


def build_customer_recommendation(row):
    """Simple business rules that explain what the company should offer each risky customer."""
    actions = []

    contract = str(row.get('Contract', ''))
    internet = str(row.get('Internet_Type', ''))
    security = str(row.get('Online_Security', ''))
    support = str(row.get('Premium_Tech_Support', ''))
    tenure = float(row.get('tenure', 0) or 0)
    charges = float(row.get('monthly_charges', 0) or 0)

    if contract == 'Month-to-Month':
        actions.append('Offer One-Year Contract')
    if security == 'No':
        actions.append('Free Online Security')
    if support == 'No':
        actions.append('Premium Tech Support')
    if internet == 'Fiber Optic' and charges >= 70:
        actions.append('Service Quality Check')
    if tenure <= 12:
        actions.append('Onboarding / Loyalty Call')
    if charges >= 85:
        actions.append('Targeted Discount')

    if not actions:
        actions.append('Monitor + Loyalty Message')

    # Keep it readable inside the table.
    return ' + '.join(actions[:3])


def prepare_customer_watchlist(df, model, features, encoders):
    """Score every customer, then rank them by risk and financial value."""
    scored = df.copy()
    X_all = encode_features(scored, features, encoders)
    probs = model.predict_proba(X_all)[:, 1]

    scored['Churn_Probability'] = probs
    scored['Churn_Probability_%'] = (probs * 100).round(1)
    scored['Risk_Level'] = scored['Churn_Probability'].apply(risk_level)
    scored['Total_Revenue'] = pd.to_numeric(scored['Total_Revenue'], errors='coerce').fillna(0)
    scored['Revenue_at_Risk'] = (scored['Churn_Probability'] * scored['Total_Revenue']).round(2)
    scored['Priority_Score'] = scored['Revenue_at_Risk'].round(2)
    scored['Recommended_Action'] = scored.apply(build_customer_recommendation, axis=1)

    return scored.sort_values('Priority_Score', ascending=False)


# ── Sections ──────────────────────────────────────────
def show_overfitting_check(check):
    section_title("Model Reliability Check")

    if check['is_overfitting']:
        banner_color = ORANGE
        banner_icon = "⚠️"
        banner_text = "Potential Overfitting Detected"
        banner_desc = (
            f"Training accuracy is <b>{check['gap']} points</b> higher than testing accuracy. "
            "The model may be memorizing the training data rather than generalizing well."
        )
    else:
        banner_color = GREEN
        banner_icon = "✅"
        banner_text = "No Overfitting Detected"
        banner_desc = (
            f"Training and testing accuracy are close (gap of only <b>{check['gap']} points</b>), "
            "which means the model generalizes well to unseen customers."
        )

    st.markdown(f"""
    <div style='background:{banner_color}15;border:2px solid {banner_color};
                border-radius:14px;padding:16px 20px;margin-bottom:14px'>
        <div style='font-size:17px;font-weight:800;color:{banner_color}'>
            {banner_icon} {banner_text}
        </div>
        <div style='font-size:13px;color:{TEXT};margin-top:6px;line-height:1.6'>
            {banner_desc}
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    kpi_card(c1, "Training Accuracy", f"{check['train_acc']}%", "fit on training data", BLUE)
    kpi_card(c2, "Testing Accuracy", f"{check['test_acc']}%", "fit on unseen data", TEAL)
    kpi_card(c3, "Train-Test Gap", f"{check['gap']} pts",
             "Overfitting" if check['is_overfitting'] else "Healthy gap",
             ORANGE if check['is_overfitting'] else GREEN)
    kpi_card(c4, "5-Fold CV Mean", f"{check['cv_mean']}%", f"± {check['cv_std']} std", GOLD)

    col1, col2 = st.columns(2)

    with col1:
        chart_title("Training vs Testing Accuracy")
        fig = go.Figure(go.Bar(
            x=['Training Accuracy', 'Testing Accuracy'],
            y=[check['train_acc'], check['test_acc']],
            marker_color=[BLUE, TEAL],
            text=[f"{check['train_acc']}%", f"{check['test_acc']}%"],
            textposition='outside',
            hovertemplate='%{x}<br>Accuracy: %{y:.1f}%<extra></extra>'
        ))
        fig.update_layout(**BASE, height=260,
                          yaxis=dict(**AX, title='Accuracy (%)', range=[0, 105]),
                          xaxis=dict(tickfont=dict(color=SUBTEXT)),
                          showlegend=False)
        st.plotly_chart(fig, width='stretch')

    with col2:
        chart_title("5-Fold Cross Validation Scores")
        fold_labels = [f"Fold {i+1}" for i in range(len(check['cv_scores']))]

        # NOTE: fixed version — the mean-line label used to overlap the bar
        # labels (esp. Fold 5). We now draw the dashed mean line WITHOUT its
        # built-in annotation, and place a separate annotation outside the
        # plot area (to the right, anchored to 'paper' coordinates) so it
        # never collides with the bar text labels.
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=fold_labels, y=check['cv_scores'],
            marker_color=GOLD,
            text=[f"{v}%" for v in check['cv_scores']],
            textposition='outside',
            textfont=dict(color=TEXT, size=12),
            cliponaxis=False,
            hovertemplate='%{x}<br>Accuracy: %{y:.1f}%<extra></extra>'
        ))
        fig2.add_hline(
            y=check['cv_mean'], line_dash='dash', line_color=TEAL
        )
        fig2.add_annotation(
            xref='paper', x=1.0, xanchor='left',
            y=check['cv_mean'], yanchor='middle',
            text=f"Mean = {check['cv_mean']}%",
            showarrow=False,
            font=dict(color=TEAL, size=12)
        )

        layout2 = dict(BASE)
        layout2['margin'] = dict(t=30, b=28, l=40, r=95)
        fig2.update_layout(**layout2, height=280,
                           yaxis=dict(**AX, title='Accuracy (%)', range=[0, 115]),
                           xaxis=dict(tickfont=dict(color=SUBTEXT)),
                           showlegend=False)
        st.plotly_chart(fig2, width='stretch')

    insight_card(
        "Why this matters",
        "Overfitting happens when a model performs very well on data it has already seen "
        "but poorly on new data — making it unreliable for real business decisions. "
        f"Cross-validation runs the model on 5 different data splits to confirm the "
        f"<b>{check['cv_mean']}%</b> average accuracy is consistent and not a lucky split, "
        "which builds confidence that this model is production-ready.",
        color=TEAL,
        icon="🔍"
    )


def show_individual_prediction(model, features, encoders):
    chart_title("🎯 Predict a Customer")
    st.markdown(f"""
    <div style='background:{CARD_BG};border:1px solid {BORDER};
                border-radius:12px;padding:16px 18px 4px'>
    """, unsafe_allow_html=True)

    tenure_in = st.slider("Tenure (months)", 1, 72, 12)
    charges_in = st.slider("Monthly Charges ($)", 20, 120, 65)
    contract_in = st.selectbox("Contract", ['Month-to-Month', 'One Year', 'Two Year'])
    internet_in = st.selectbox("Internet Type", ['Fiber Optic', 'Cable', 'DSL', 'No internet'])
    senior_in = st.selectbox(
        "Senior Citizen", [0, 1],
        format_func=lambda x: "Yes" if x == 1 else "No"
    )
    security_in = st.selectbox("Online Security", ['Yes', 'No'])
    support_in = st.selectbox("Premium Tech Support", ['Yes', 'No'])

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
            'Payment_Method': safe_option(encoders, 'Payment_Method', 'Bank Withdrawal'),
            'Online_Security': security_in,
            'Premium_Tech_Support': support_in,
            'Married': safe_option(encoders, 'Married', 'Not Married')
        }])

        sample_encoded = encode_features(sample, features, encoders)
        prob = model.predict_proba(sample_encoded)[0][1]
        color = risk_color(prob)
        risk = "🔴 HIGH RISK" if prob >= 0.60 else "🟡 MEDIUM RISK" if prob >= 0.35 else "🟢 LOW RISK"
        recommendation = build_customer_recommendation(sample.iloc[0])

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

        insight_card(
            "Recommended Action",
            f"For this customer profile, the suggested retention action is: <b>{recommendation}</b>.",
            color=color,
            icon="🎯"
        )


def show_customer_watchlist(df, model, features, encoders):
    section_title("High-Risk Customer Watchlist")
    st.markdown(f"""
    <div style='background:{CARD_BG};border:1px solid {BORDER};border-radius:14px;
                padding:16px 20px;margin-bottom:12px'>
        <div style='font-size:18px;font-weight:700;color:{TEXT};margin-bottom:4px'>
            🚨 Priority Retention List
        </div>
        <div style='font-size:13px;color:{SUBTEXT};line-height:1.6'>
            This list scores every customer using the trained model, then ranks them by both churn risk
            and revenue value. The goal is to tell the business who should be contacted first.
        </div>
    </div>
    """, unsafe_allow_html=True)

    scored = prepare_customer_watchlist(df, model, features, encoders)

    min_risk = st.slider("Minimum Churn Probability (%)", 0, 100, 50, 5)
    top_n = st.slider("Number of customers to show", 5, 50, 10, 5)

    filtered = scored[scored['Churn_Probability_%'] >= min_risk].copy()
    top_customers = filtered.head(top_n)

    if top_customers.empty:
        st.info("No customers match the selected risk threshold.")
        return

    total_revenue_at_risk = top_customers['Revenue_at_Risk'].sum()
    avg_risk = top_customers['Churn_Probability_%'].mean()
    high_risk_count = (top_customers['Risk_Level'] == 'High Risk').sum()

    c1, c2, c3, c4 = st.columns(4)
    kpi_card(c1, "Selected Customers", f"{len(top_customers):,}", "highest priority", BLUE)
    kpi_card(c2, "Avg Churn Risk", f"{avg_risk:.1f}%", "selected list", ORANGE)
    kpi_card(c3, "Revenue at Risk", f"${total_revenue_at_risk/1e6:.2f}M", "probability-weighted", GOLD)
    kpi_card(c4, "High Risk Cases", f"{high_risk_count:,}", ">= 60% risk", RED)

    display_cols = [
        'customer_id', 'Churn_Probability_%', 'Risk_Level', 'Total_Revenue',
        'Revenue_at_Risk', 'Priority_Score', 'Contract', 'Internet_Type',
        'Online_Security', 'Premium_Tech_Support', 'tenure', 'monthly_charges',
        'Recommended_Action'
    ]

    rename_cols = {
        'customer_id': 'Customer ID',
        'Churn_Probability_%': 'Churn Probability %',
        'Risk_Level': 'Risk Level',
        'Total_Revenue': 'Total Revenue',
        'Revenue_at_Risk': 'Revenue at Risk',
        'Priority_Score': 'Priority Score',
        'Contract': 'Contract',
        'Internet_Type': 'Internet Type',
        'Online_Security': 'Online Security',
        'Premium_Tech_Support': 'Tech Support',
        'tenure': 'Tenure',
        'monthly_charges': 'Monthly Charges',
        'Recommended_Action': 'Recommended Action'
    }

    table = top_customers[display_cols].rename(columns=rename_cols)
    st.dataframe(table, width='stretch', hide_index=True)

    csv = table.to_csv(index=False).encode('utf-8')
    st.download_button(
        "⬇️ Download Retention List CSV",
        data=csv,
        file_name="high_risk_customer_watchlist.csv",
        mime="text/csv",
        width='stretch'
    )

    top_10 = top_customers.head(10).sort_values('Priority_Score', ascending=True)
    fig = go.Figure(go.Bar(
        x=top_10['Priority_Score'],
        y=top_10['customer_id'].astype(str),
        orientation='h',
        marker_color=RED,
        text=[f"{v:.0f}" for v in top_10['Priority_Score']],
        textposition='outside',
        hovertemplate='Customer: %{y}<br>Priority Score: %{x:.0f}<extra></extra>'
    ))
    fig.update_layout(
        **BASE,
        height=300,
        xaxis=dict(**AX, title='Priority Score = Churn Probability × Total Revenue'),
        yaxis=dict(**AX, title='Customer ID')
    )
    st.plotly_chart(fig, width='stretch')

    best = top_customers.iloc[0]
    insight_card(
        "Who should the company contact first?",
        f"The top priority customer is <b>{best['customer_id']}</b>. "
        f"Their churn probability is <b>{best['Churn_Probability_%']:.1f}%</b>, "
        f"total revenue is <b>${best['Total_Revenue']:,.0f}</b>, and the suggested action is "
        f"<b>{best['Recommended_Action']}</b>.",
        color=GOLD,
        icon="🏆"
    )


def apply_strategy(df_segment, strategy, encoders):
    scenario = df_segment.copy()

    if strategy == "Convert Month-to-Month customers to One Year contracts":
        scenario['Contract'] = safe_option(encoders, 'Contract', 'One Year')
    elif strategy == "Convert Month-to-Month customers to Two Year contracts":
        scenario['Contract'] = safe_option(encoders, 'Contract', 'Two Year')
    elif strategy == "Add Online Security for customers without it":
        scenario['Online_Security'] = safe_option(encoders, 'Online_Security', 'Yes')
    elif strategy == "Add Premium Tech Support for customers without it":
        scenario['Premium_Tech_Support'] = safe_option(encoders, 'Premium_Tech_Support', 'Yes')
    elif strategy == "Full Retention Bundle":
        scenario['Contract'] = safe_option(encoders, 'Contract', 'One Year')
        scenario['Online_Security'] = safe_option(encoders, 'Online_Security', 'Yes')
        scenario['Premium_Tech_Support'] = safe_option(encoders, 'Premium_Tech_Support', 'Yes')

    return scenario


def show_strategy_simulator(df, model, features, encoders):
    section_title("Business Strategy Simulator")

    st.markdown(f"""
    <div style='background:{CARD_BG};border:1px solid {BORDER};border-radius:14px;
                padding:16px 20px;margin-bottom:12px'>
        <div style='font-size:18px;font-weight:700;color:{TEXT};margin-bottom:4px'>
            🔮 What-If Scenario Simulator
        </div>
        <div style='font-size:13px;color:{SUBTEXT};line-height:1.6'>
            This section simulates a business decision using the trained XGBoost model.
            It compares predicted churn risk before and after applying a retention strategy.
        </div>
    </div>
    """, unsafe_allow_html=True)

    strategy = st.selectbox(
        "Choose a retention strategy",
        [
            "Convert Month-to-Month customers to One Year contracts",
            "Convert Month-to-Month customers to Two Year contracts",
            "Add Online Security for customers without it",
            "Add Premium Tech Support for customers without it",
            "Full Retention Bundle"
        ]
    )

    target = st.selectbox(
        "Target customer segment",
        [
            "All eligible customers",
            "High-risk customers only",
            "High-value high-risk customers"
        ]
    )

    scenario_df = df.copy()

    if "Month-to-Month" in strategy:
        target_mask = scenario_df['Contract'].astype(str).eq('Month-to-Month')
        business_label = "Month-to-Month customers"
    elif strategy == "Add Online Security for customers without it":
        target_mask = scenario_df['Online_Security'].astype(str).eq('No')
        business_label = "customers without Online Security"
    elif strategy == "Add Premium Tech Support for customers without it":
        target_mask = scenario_df['Premium_Tech_Support'].astype(str).eq('No')
        business_label = "customers without Premium Tech Support"
    else:
        target_mask = (
            scenario_df['Contract'].astype(str).eq('Month-to-Month') |
            scenario_df['Online_Security'].astype(str).eq('No') |
            scenario_df['Premium_Tech_Support'].astype(str).eq('No')
        )
        business_label = "customers eligible for a retention bundle"

    target_df = scenario_df[target_mask].copy()

    if target_df.empty:
        st.warning("No customers match this scenario in the dataset.")
        return

    before_encoded = encode_features(target_df, features, encoders)
    before_prob = model.predict_proba(before_encoded)[:, 1]
    target_df['Current_Prob'] = before_prob
    target_df['Total_Revenue'] = pd.to_numeric(target_df['Total_Revenue'], errors='coerce').fillna(0)

    if target == "High-risk customers only":
        target_df = target_df[target_df['Current_Prob'] >= 0.50].copy()
    elif target == "High-value high-risk customers":
        revenue_cutoff = target_df['Total_Revenue'].quantile(0.75)
        target_df = target_df[(target_df['Current_Prob'] >= 0.50) & (target_df['Total_Revenue'] >= revenue_cutoff)].copy()

    if target_df.empty:
        st.info("No customers match the selected target segment.")
        return

    before_prob = target_df['Current_Prob'].values
    after_df = apply_strategy(target_df, strategy, encoders)
    after_encoded = encode_features(after_df, features, encoders)
    after_prob = model.predict_proba(after_encoded)[:, 1]

    current_expected_churn = float(before_prob.sum())
    new_expected_churn = float(after_prob.sum())
    saved_customers = max(current_expected_churn - new_expected_churn, 0)

    revenue = target_df['Total_Revenue'].values
    retained_revenue = float(np.maximum(before_prob - after_prob, 0).dot(revenue))
    before_rate = float(before_prob.mean() * 100)
    after_rate = float(after_prob.mean() * 100)
    rate_drop = max(before_rate - after_rate, 0)

    c1, c2, c3, c4 = st.columns(4)
    kpi_card(c1, "Target Segment", f"{len(target_df):,}", business_label, BLUE)
    kpi_card(c2, "Customers Saved", f"+{saved_customers:,.0f}", "expected reduction", GREEN)
    kpi_card(c3, "Revenue Retained", f"${retained_revenue/1e6:.2f}M", "expected recovery", GOLD)
    kpi_card(c4, "Risk Drop", f"{rate_drop:.1f}%", f"{before_rate:.1f}% → {after_rate:.1f}%", TEAL)

    fig = go.Figure(go.Bar(
        x=['Before Strategy', 'After Strategy'],
        y=[before_rate, after_rate],
        marker_color=[RED, TEAL],
        text=[f"{before_rate:.1f}%", f"{after_rate:.1f}%"],
        textposition='outside',
        hovertemplate='%{x}<br>Average Predicted Churn Risk: %{y:.1f}%<extra></extra>'
    ))
    fig.update_layout(
        **BASE,
        height=260,
        yaxis=dict(**AX, title='Average Predicted Churn Risk (%)'),
        xaxis=dict(tickfont=dict(color=SUBTEXT)),
        showlegend=False
    )
    st.plotly_chart(fig, width='stretch')

    insight_card(
        "AI Business Recommendation",
        f"Based on the trained model, <b>{strategy}</b> applied to <b>{target}</b> "
        f"could reduce average predicted churn risk from <b>{before_rate:.1f}%</b> to "
        f"<b>{after_rate:.1f}%</b>. This may save around <b>{saved_customers:,.0f}</b> "
        f"customers and retain approximately <b>${retained_revenue/1e6:.2f}M</b> in revenue.",
        color=GOLD,
        icon="💡"
    )


# ── Main page ─────────────────────────────────────────
def show():
    df = load_full()
    st.markdown("<div style='height:35px'></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style='background:{CARD_BG};border:1px solid {BORDER};border-radius:14px;
                padding:14px 22px;margin-bottom:14px'>
        <div style='font-size:22px;font-weight:700;color:{TEXT}'>
            🧠 ML Churn Prediction
        </div>
        <div style='font-size:13px;color:{SUBTEXT};margin-top:4px'>
            XGBoost Model — customer risk scoring, prediction, and retention strategy simulation
        </div>
    </div>""", unsafe_allow_html=True)

    with st.spinner("Training model..."):
        model, X_train, X_test, y_train, y_test, features, encoders = train_model(df)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    accuracy = round(100 * (y_pred == y_test).mean(), 1)
    precision = round(100 * precision_score(y_test, y_pred, zero_division=0), 1)
    recall = round(100 * recall_score(y_test, y_pred, zero_division=0), 1)
    f1 = round(100 * f1_score(y_test, y_pred, zero_division=0), 1)

    k1, k2, k3, k4 = st.columns(4)
    kpi_card(k1, "Accuracy", f"{accuracy}%", "overall correctness", TEAL)
    kpi_card(k2, "Precision", f"{precision}%", "quality of churn alerts", BLUE)
    kpi_card(k3, "Recall", f"{recall}%", "churn cases detected", GOLD)
    kpi_card(k4, "F1 Score", f"{f1}%", "balance score", ORANGE)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── OVERFITTING CHECK ──────────────────────────────
    with st.spinner("Running overfitting check + 5-fold cross validation..."):
        overfit_check = run_overfitting_check(model, X_train, y_train, X_test, y_test)
    show_overfitting_check(overfit_check)

    section_title("Model Performance")
    col1, col2 = st.columns(2)

    with col1:
        chart_title("Feature Importance")
        imp_df = pd.DataFrame({
            'Feature': features,
            'Importance': model.feature_importances_
        }).sort_values('Importance', ascending=True)

        # NOTE: fixed version — with 13+ features crammed into a fixed
        # height=280 chart, the outside text labels overlapped each other
        # and the bars. We now size the chart based on the number of
        # features, widen the left margin for the feature names, and pad
        # the x-axis range so the outside text has room to breathe.
        n_features = len(imp_df)
        max_importance = imp_df['Importance'].max() if n_features else 0

        fig1 = go.Figure(go.Bar(
            x=imp_df['Importance'], y=imp_df['Feature'], orientation='h',
            marker_color=TEAL, marker_line_width=0,
            text=[f"{v:.3f}" for v in imp_df['Importance']],
            textposition='outside', textfont=dict(color=TEXT, size=10),
            cliponaxis=False,
            hovertemplate='%{y}<br>Importance: %{x:.3f}<extra></extra>'
        ))

        layout1 = dict(BASE)
        layout1['margin'] = dict(t=10, b=28, l=170, r=40)
        fig1.update_layout(
            **layout1,
            height=max(320, 28 * n_features + 60),
            bargap=0.35,
            xaxis=dict(**AX, title='Importance Score',
                       range=[0, (max_importance * 1.25) if max_importance > 0 else 1]),
            yaxis=dict(**{**AX, 'tickfont': dict(color=SUBTEXT, size=11)})
        )
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

    section_title("Model Evaluation & Individual Prediction")
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
        show_individual_prediction(model, features, encoders)

    show_customer_watchlist(df, model, features, encoders)
    show_strategy_simulator(df, model, features, encoders)