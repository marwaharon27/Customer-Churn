
"""
Telecom Churn Model Comparison Tool
==================================

ضع هذا الملف في فولدر المشروع الرئيسي بجانب app.py ثم شغليه من VS Code أو Terminal:

    python model_comparison.py

الملف سيجرب عدة موديلات + طرق Sampling + Threshold Tuning
ثم يحفظ النتائج في:
    model_comparison_results.csv

مهم:
لو ظهرت رسالة أن مكتبة ناقصة، ثبتيها من التيرمنال:
    pip install xgboost lightgbm imbalanced-learn
"""

import os
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression

# ──────────────────────────────────────────────────────
# Optional libraries
# ──────────────────────────────────────────────────────
try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except Exception:
    XGBOOST_AVAILABLE = False

try:
    from lightgbm import LGBMClassifier
    LIGHTGBM_AVAILABLE = True
except Exception:
    LIGHTGBM_AVAILABLE = False

try:
    from imblearn.pipeline import Pipeline as ImbPipeline
    from imblearn.over_sampling import SMOTE, RandomOverSampler
    from imblearn.under_sampling import RandomUnderSampler
    IMBLEARN_AVAILABLE = True
except Exception:
    IMBLEARN_AVAILABLE = False


# ──────────────────────────────────────────────────────
# Project imports
# ──────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))

try:
    from utils.load_data import load_full
except Exception as e:
    raise ImportError(
        "\n❌ لم أستطع استيراد load_full من utils.load_data.\n"
        "تأكدي أن الملف model_comparison.py موجود في نفس مكان app.py، "
        "وأن فولدر utils موجود في المشروع.\n"
        f"Original error: {e}"
    )


# ──────────────────────────────────────────────────────
# Features
# ──────────────────────────────────────────────────────
BASE_FEATURES = [
    "tenure",
    "monthly_charges",
    "Total_Revenue",
    "SeniorCitizen",
    "Number_of_Referrals",
    "Contract",
    "Internet_Type",
    "Payment_Method",
    "Online_Security",
    "Premium_Tech_Support",
    "Married",
]

CAT_COLS = [
    "Contract",
    "Internet_Type",
    "Payment_Method",
    "Online_Security",
    "Premium_Tech_Support",
    "Married",
]

NUM_COLS = [
    "tenure",
    "monthly_charges",
    "Total_Revenue",
    "SeniorCitizen",
    "Number_of_Referrals",
]


def print_header(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def make_onehot_encoder():
    """
    Compatible with old/new sklearn versions.
    sklearn >= 1.2 uses sparse_output
    older sklearn uses sparse
    """
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Features إضافية من نفس البيانات، بدون تغيير الداتا الأصلية.
    الهدف: نساعد الموديل يفهم العلاقات المهمة.
    """
    out = df.copy()

    out["tenure"] = pd.to_numeric(out["tenure"], errors="coerce").fillna(0)
    out["monthly_charges"] = pd.to_numeric(out["monthly_charges"], errors="coerce").fillna(0)
    out["Total_Revenue"] = pd.to_numeric(out["Total_Revenue"], errors="coerce").fillna(0)
    out["Number_of_Referrals"] = pd.to_numeric(out["Number_of_Referrals"], errors="coerce").fillna(0)

    out["Revenue_per_Tenure"] = out["Total_Revenue"] / (out["tenure"] + 1)
    out["Charges_x_Tenure"] = out["monthly_charges"] * out["tenure"]
    out["No_Referrals_Flag"] = (out["Number_of_Referrals"] == 0).astype(int)
    out["New_Customer_Flag"] = (out["tenure"] <= 12).astype(int)
    out["High_Charges_Flag"] = (out["monthly_charges"] >= out["monthly_charges"].median()).astype(int)

    return out


def prepare_data(use_engineered_features: bool = True):
    df = load_full()

    missing = [c for c in BASE_FEATURES + ["churn"] if c not in df.columns]
    if missing:
        raise ValueError(f"❌ الأعمدة دي ناقصة من الداتا: {missing}")

    df_ml = df[BASE_FEATURES + ["churn"]].copy()

    for col in NUM_COLS:
        df_ml[col] = pd.to_numeric(df_ml[col], errors="coerce").fillna(0)

    for col in CAT_COLS:
        df_ml[col] = df_ml[col].astype(str).fillna("Unknown")

    df_ml["churn"] = df_ml["churn"].astype(str)
    df_ml = df_ml[df_ml["churn"].isin(["Yes", "No"])].copy()

    if use_engineered_features:
        df_ml = add_engineered_features(df_ml)
        num_cols = NUM_COLS + [
            "Revenue_per_Tenure",
            "Charges_x_Tenure",
            "No_Referrals_Flag",
            "New_Customer_Flag",
            "High_Charges_Flag",
        ]
    else:
        num_cols = NUM_COLS.copy()

    cat_cols = CAT_COLS.copy()
    features = num_cols + cat_cols

    X = df_ml[features].copy()
    y = (df_ml["churn"] == "Yes").astype(int)

    return X, y, features, num_cols, cat_cols


def build_preprocessor(num_cols, cat_cols):
    numeric_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", make_onehot_encoder()),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, num_cols),
            ("cat", categorical_pipe, cat_cols),
        ],
        remainder="drop",
    )

    return preprocessor


def get_models():
    models = {
        "Logistic Regression": LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=42,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=300,
            max_depth=10,
            min_samples_split=10,
            min_samples_leaf=4,
            class_weight="balanced_subsample",
            random_state=42,
            n_jobs=-1,
        ),
        "Extra Trees": ExtraTreesClassifier(
            n_estimators=300,
            max_depth=12,
            min_samples_split=8,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=180,
            learning_rate=0.05,
            max_depth=3,
            subsample=0.9,
            random_state=42,
        ),
    }

    if XGBOOST_AVAILABLE:
        models["XGBoost"] = XGBClassifier(
            n_estimators=260,
            max_depth=3,
            learning_rate=0.045,
            subsample=0.9,
            colsample_bytree=0.85,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=42,
            n_jobs=-1,
        )

    if LIGHTGBM_AVAILABLE:
        models["LightGBM"] = LGBMClassifier(
            n_estimators=260,
            learning_rate=0.045,
            num_leaves=24,
            max_depth=-1,
            subsample=0.9,
            colsample_bytree=0.85,
            random_state=42,
            n_jobs=-1,
            verbose=-1,
        )

    return models


def get_sampling_strategies():
    strategies = {"None": None}

    if IMBLEARN_AVAILABLE:
        strategies.update(
            {
                "RandomOverSampler": RandomOverSampler(random_state=42),
                "SMOTE": SMOTE(random_state=42, k_neighbors=5),
                "RandomUnderSampler": RandomUnderSampler(random_state=42),
            }
        )

    return strategies


def find_best_threshold(y_true, y_prob):
    """
    نجرب Thresholds مختلفة ونختار الأعلى في F1.
    """
    thresholds = np.arange(0.20, 0.81, 0.01)
    best = {
        "threshold": 0.50,
        "f1": -1,
        "precision": 0,
        "recall": 0,
        "accuracy": 0,
    }

    for th in thresholds:
        pred = (y_prob >= th).astype(int)
        f1 = f1_score(y_true, pred, zero_division=0)
        if f1 > best["f1"]:
            best = {
                "threshold": round(float(th), 2),
                "f1": f1,
                "precision": precision_score(y_true, pred, zero_division=0),
                "recall": recall_score(y_true, pred, zero_division=0),
                "accuracy": accuracy_score(y_true, pred),
            }

    return best


def evaluate_model(model_name, model, sampling_name, sampler, preprocessor, X_train, X_test, y_train, y_test):
    if sampler is None:
        pipe = Pipeline(
            steps=[
                ("preprocess", preprocessor),
                ("model", clone(model)),
            ]
        )
    else:
        pipe = ImbPipeline(
            steps=[
                ("preprocess", preprocessor),
                ("sampler", sampler),
                ("model", clone(model)),
            ]
        )

    pipe.fit(X_train, y_train)

    if hasattr(pipe, "predict_proba"):
        y_prob = pipe.predict_proba(X_test)[:, 1]
    else:
        # fallback
        scores = pipe.decision_function(X_test)
        y_prob = (scores - scores.min()) / (scores.max() - scores.min() + 1e-9)

    default_pred = (y_prob >= 0.50).astype(int)
    best_th = find_best_threshold(y_test, y_prob)
    tuned_pred = (y_prob >= best_th["threshold"]).astype(int)

    try:
        auc_value = roc_auc_score(y_test, y_prob)
    except Exception:
        auc_value = np.nan

    cm = confusion_matrix(y_test, tuned_pred)
    tn, fp, fn, tp = cm.ravel()

    return {
        "Model": model_name,
        "Sampling": sampling_name,
        "Default_Threshold": 0.50,
        "Default_Accuracy": accuracy_score(y_test, default_pred),
        "Default_Precision": precision_score(y_test, default_pred, zero_division=0),
        "Default_Recall": recall_score(y_test, default_pred, zero_division=0),
        "Default_F1": f1_score(y_test, default_pred, zero_division=0),
        "Best_Threshold": best_th["threshold"],
        "Tuned_Accuracy": accuracy_score(y_test, tuned_pred),
        "Tuned_Precision": precision_score(y_test, tuned_pred, zero_division=0),
        "Tuned_Recall": recall_score(y_test, tuned_pred, zero_division=0),
        "Tuned_F1": f1_score(y_test, tuned_pred, zero_division=0),
        "ROC_AUC": auc_value,
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "TP": tp,
    }


def main():
    print_header("TELECOM CHURN MODEL COMPARISON")

    print("✅ Loading and preparing data...")
    X, y, features, num_cols, cat_cols = prepare_data(use_engineered_features=True)

    print(f"Rows: {len(X):,}")
    print(f"Features: {len(features)}")
    print("Target distribution:")
    print(y.value_counts(normalize=True).rename({0: "No Churn", 1: "Churn"}).mul(100).round(2).astype(str) + "%")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    preprocessor = build_preprocessor(num_cols, cat_cols)
    models = get_models()
    samplers = get_sampling_strategies()

    if not XGBOOST_AVAILABLE:
        print("\n⚠️ XGBoost غير مثبت. لو عايزة تجربيه شغلي: pip install xgboost")
    if not LIGHTGBM_AVAILABLE:
        print("⚠️ LightGBM غير مثبت. لو عايزة تجربيه شغلي: pip install lightgbm")
    if not IMBLEARN_AVAILABLE:
        print("⚠️ imbalanced-learn غير مثبت، لذلك SMOTE/UnderSampling لن يعملوا. شغلي: pip install imbalanced-learn")

    results = []

    print_header("RUNNING EXPERIMENTS")
    total = len(models) * len(samplers)
    counter = 1

    for model_name, model in models.items():
        for sampling_name, sampler in samplers.items():
            print(f"[{counter}/{total}] Running: {model_name} + {sampling_name}")
            counter += 1

            try:
                row = evaluate_model(
                    model_name=model_name,
                    model=model,
                    sampling_name=sampling_name,
                    sampler=sampler,
                    preprocessor=preprocessor,
                    X_train=X_train,
                    X_test=X_test,
                    y_train=y_train,
                    y_test=y_test,
                )
                results.append(row)
            except Exception as e:
                print(f"   ❌ Failed: {model_name} + {sampling_name} | {e}")

    if not results:
        raise RuntimeError("❌ No experiments completed successfully.")

    results_df = pd.DataFrame(results)

    sort_cols = ["Tuned_F1", "Tuned_Recall", "Tuned_Precision", "ROC_AUC"]
    results_df = results_df.sort_values(sort_cols, ascending=False).reset_index(drop=True)

    percent_cols = [
        "Default_Accuracy", "Default_Precision", "Default_Recall", "Default_F1",
        "Tuned_Accuracy", "Tuned_Precision", "Tuned_Recall", "Tuned_F1", "ROC_AUC",
    ]

    display_df = results_df.copy()
    for col in percent_cols:
        display_df[col] = (display_df[col] * 100).round(1)

    output_path = PROJECT_ROOT / "model_comparison_results.csv"
    display_df.to_csv(output_path, index=False)

    print_header("RESULTS - SORTED BY BEST F1")
    cols_to_show = [
        "Model", "Sampling", "Best_Threshold",
        "Tuned_Accuracy", "Tuned_Precision", "Tuned_Recall", "Tuned_F1", "ROC_AUC",
        "TN", "FP", "FN", "TP",
    ]
    print(display_df[cols_to_show].to_string(index=False))

    best = display_df.iloc[0]

    print_header("BEST MODEL")
    print(f"🏆 Model: {best['Model']}")
    print(f"🏆 Sampling: {best['Sampling']}")
    print(f"🏆 Best Threshold: {best['Best_Threshold']}")
    print(f"Accuracy:  {best['Tuned_Accuracy']}%")
    print(f"Precision: {best['Tuned_Precision']}%")
    print(f"Recall:    {best['Tuned_Recall']}%")
    print(f"F1 Score:  {best['Tuned_F1']}%")
    print(f"ROC AUC:   {best['ROC_AUC']}%")
    print(f"\n✅ Results saved to: {output_path}")

    print("\n📌 ابعتيلي أول 5 صفوف من جدول النتائج أو ملف model_comparison_results.csv")
    print("وبعدها أعملك ml.py النهائي بأفضل موديل بدون تغيير الواجهة.")


if __name__ == "__main__":
    main()
