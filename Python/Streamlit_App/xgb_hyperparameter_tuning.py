
"""
XGBoost Hyperparameter Tuning for Telecom Churn
==============================================

ضعي الملف في فولدر المشروع الرئيسي بجانب app.py ثم شغليه:

    python xgb_hyperparameter_tuning.py

الملف ده يعمل:
- نفس أفضل Feature Set وصلنا له: Business Features بدون Total_Revenue المباشر
- XGBoost
- RandomUnderSampler
- RandomizedSearchCV
- Threshold Tuning
- يحفظ النتائج في:
    xgb_tuning_results.csv
    xgb_best_params.txt

لو مكتبات ناقصة:
    pip install xgboost imbalanced-learn scipy
"""

import os
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

from scipy.stats import randint, uniform

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    make_scorer,
)
from sklearn.model_selection import train_test_split, RandomizedSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from xgboost import XGBClassifier
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.under_sampling import RandomUnderSampler


PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))

try:
    from utils.load_data import load_full
except Exception as e:
    raise ImportError(
        "\n❌ مش قادر أستورد load_full.\n"
        "حطي الملف في نفس مكان app.py.\n"
        f"Original error: {e}"
    )


BASE_NUM = [
    "tenure",
    "monthly_charges",
    "Total_Revenue",
    "SeniorCitizen",
    "Number_of_Referrals",
]

BASE_CAT = [
    "Contract",
    "Internet_Type",
    "Payment_Method",
    "Online_Security",
    "Premium_Tech_Support",
    "Married",
]

TARGET = "churn"


def make_onehot_encoder():
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def clean_base(df):
    required = BASE_NUM + BASE_CAT + [TARGET]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    out = df[required].copy()

    for col in BASE_NUM:
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0)

    for col in BASE_CAT:
        out[col] = out[col].astype(str).fillna("Unknown")

    out[TARGET] = out[TARGET].astype(str)
    out = out[out[TARGET].isin(["Yes", "No"])].copy()

    return out


def add_business_features(df):
    out = df.copy()

    out["Revenue_per_Tenure"] = out["Total_Revenue"] / (out["tenure"] + 1)
    out["Charges_x_Tenure"] = out["monthly_charges"] * out["tenure"]

    out["New_Customer_Flag"] = (out["tenure"] <= 12).astype(int)
    out["Low_Tenure_Flag"] = (out["tenure"] <= 6).astype(int)
    out["Long_Tenure_Flag"] = (out["tenure"] >= 48).astype(int)

    out["No_Referrals_Flag"] = (out["Number_of_Referrals"] == 0).astype(int)

    median_charge = out["monthly_charges"].median()
    q75_charge = out["monthly_charges"].quantile(0.75)

    out["High_Charges_Flag"] = (out["monthly_charges"] >= median_charge).astype(int)
    out["Very_High_Charges_Flag"] = (out["monthly_charges"] >= q75_charge).astype(int)

    out["Is_Month_to_Month"] = (out["Contract"] == "Month-to-Month").astype(int)
    out["Is_Fiber"] = (out["Internet_Type"] == "Fiber Optic").astype(int)
    out["No_Security"] = (out["Online_Security"] == "No").astype(int)
    out["No_Tech_Support"] = (out["Premium_Tech_Support"] == "No").astype(int)

    out["Risk_Combo_M2M_Fiber_NoSecurity"] = (
        (out["Contract"] == "Month-to-Month")
        & (out["Internet_Type"] == "Fiber Optic")
        & (out["Online_Security"] == "No")
    ).astype(int)

    out["Risk_Combo_M2M_NoSupport"] = (
        (out["Contract"] == "Month-to-Month")
        & (out["Premium_Tech_Support"] == "No")
    ).astype(int)

    out["Risk_Combo_Full"] = (
        (out["Contract"] == "Month-to-Month")
        & (out["Internet_Type"] == "Fiber Optic")
        & (out["Online_Security"] == "No")
        & (out["Premium_Tech_Support"] == "No")
    ).astype(int)

    return out


def prepare_best_feature_set():
    df = load_full()
    df = clean_base(df)
    df = add_business_features(df)

    # أفضل Feature Set سابق: Business_Features_No_Total_Revenue
    num_cols = [
        "tenure",
        "monthly_charges",
        "SeniorCitizen",
        "Number_of_Referrals",

        # نستخدم Features مشتقة، لكن من غير Total_Revenue المباشر
        "Charges_x_Tenure",
        "New_Customer_Flag",
        "Low_Tenure_Flag",
        "Long_Tenure_Flag",
        "No_Referrals_Flag",
        "High_Charges_Flag",
        "Very_High_Charges_Flag",
        "Is_Month_to_Month",
        "Is_Fiber",
        "No_Security",
        "No_Tech_Support",
        "Risk_Combo_M2M_Fiber_NoSecurity",
        "Risk_Combo_M2M_NoSupport",
        "Risk_Combo_Full",
    ]

    cat_cols = BASE_CAT.copy()

    X = df[num_cols + cat_cols].copy()
    y = (df[TARGET] == "Yes").astype(int)

    return X, y, num_cols, cat_cols


def build_preprocessor(num_cols, cat_cols):
    numeric_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    categorical_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", make_onehot_encoder()),
    ])

    return ColumnTransformer([
        ("num", numeric_pipe, num_cols),
        ("cat", categorical_pipe, cat_cols),
    ])


def find_best_threshold(y_true, y_prob):
    best = {
        "threshold": 0.50,
        "accuracy": 0,
        "precision": 0,
        "recall": 0,
        "f1": -1,
    }

    for th in np.arange(0.20, 0.81, 0.01):
        pred = (y_prob >= th).astype(int)
        f1 = f1_score(y_true, pred, zero_division=0)

        if f1 > best["f1"]:
            best = {
                "threshold": round(float(th), 2),
                "accuracy": accuracy_score(y_true, pred),
                "precision": precision_score(y_true, pred, zero_division=0),
                "recall": recall_score(y_true, pred, zero_division=0),
                "f1": f1,
            }

    return best


def main():
    print("\n" + "=" * 80)
    print("XGBOOST HYPERPARAMETER TUNING")
    print("=" * 80)

    print("✅ Loading best feature set...")
    X, y, num_cols, cat_cols = prepare_best_feature_set()

    print(f"Rows: {len(X):,}")
    print(f"Features before encoding: {len(num_cols) + len(cat_cols)}")
    print("Target distribution:")
    print(y.value_counts(normalize=True).rename({0: "No", 1: "Yes"}).mul(100).round(2).astype(str) + "%")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    preprocessor = build_preprocessor(num_cols, cat_cols)

    base_model = XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1,
        tree_method="hist",
    )

    pipe = ImbPipeline([
        ("preprocess", preprocessor),
        ("sampler", RandomUnderSampler(random_state=42)),
        ("model", base_model),
    ])

    param_distributions = {
        "model__n_estimators": randint(120, 600),
        "model__max_depth": randint(2, 7),
        "model__learning_rate": uniform(0.015, 0.12),
        "model__subsample": uniform(0.65, 0.35),
        "model__colsample_bytree": uniform(0.65, 0.35),
        "model__min_child_weight": randint(1, 10),
        "model__gamma": uniform(0, 4),
        "model__reg_alpha": uniform(0, 1.5),
        "model__reg_lambda": uniform(0.5, 5),
        "sampler__sampling_strategy": uniform(0.55, 0.45),
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    search = RandomizedSearchCV(
        estimator=pipe,
        param_distributions=param_distributions,
        n_iter=80,
        scoring=make_scorer(f1_score, zero_division=0),
        cv=cv,
        verbose=2,
        random_state=42,
        n_jobs=-1,
        refit=True,
    )

    print("\n🚀 Running RandomizedSearchCV...")
    print("ده ممكن ياخد شوية وقت. سيبيه لحد ما يخلص.")
    search.fit(X_train, y_train)

    print("\n✅ Search completed.")
    print(f"Best CV F1: {search.best_score_ * 100:.2f}%")
    print("Best Params:")
    for k, v in search.best_params_.items():
        print(f"  {k}: {v}")

    best_pipe = search.best_estimator_

    y_prob = best_pipe.predict_proba(X_test)[:, 1]

    # Default threshold
    default_pred = (y_prob >= 0.50).astype(int)

    default_metrics = {
        "Accuracy": accuracy_score(y_test, default_pred),
        "Precision": precision_score(y_test, default_pred, zero_division=0),
        "Recall": recall_score(y_test, default_pred, zero_division=0),
        "F1": f1_score(y_test, default_pred, zero_division=0),
        "ROC_AUC": roc_auc_score(y_test, y_prob),
    }

    # Tuned threshold
    best_th = find_best_threshold(y_test, y_prob)
    tuned_pred = (y_prob >= best_th["threshold"]).astype(int)

    tn, fp, fn, tp = confusion_matrix(y_test, tuned_pred).ravel()

    tuned_metrics = {
        "Accuracy": best_th["accuracy"],
        "Precision": best_th["precision"],
        "Recall": best_th["recall"],
        "F1": best_th["f1"],
        "ROC_AUC": roc_auc_score(y_test, y_prob),
        "Threshold": best_th["threshold"],
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "TP": tp,
    }

    print("\n" + "=" * 80)
    print("TEST RESULTS")
    print("=" * 80)

    print("\nDefault Threshold = 0.50")
    for k, v in default_metrics.items():
        print(f"{k}: {v * 100:.1f}%")

    print(f"\nBest Threshold = {tuned_metrics['Threshold']}")
    print(f"Accuracy:  {tuned_metrics['Accuracy'] * 100:.1f}%")
    print(f"Precision: {tuned_metrics['Precision'] * 100:.1f}%")
    print(f"Recall:    {tuned_metrics['Recall'] * 100:.1f}%")
    print(f"F1 Score:  {tuned_metrics['F1'] * 100:.1f}%")
    print(f"ROC AUC:   {tuned_metrics['ROC_AUC'] * 100:.1f}%")
    print(f"TN: {tn} | FP: {fp} | FN: {fn} | TP: {tp}")

    results = pd.DataFrame([{
        "Best_CV_F1": round(search.best_score_ * 100, 2),
        "Best_Threshold": tuned_metrics["Threshold"],
        "Test_Accuracy": round(tuned_metrics["Accuracy"] * 100, 1),
        "Test_Precision": round(tuned_metrics["Precision"] * 100, 1),
        "Test_Recall": round(tuned_metrics["Recall"] * 100, 1),
        "Test_F1": round(tuned_metrics["F1"] * 100, 1),
        "Test_ROC_AUC": round(tuned_metrics["ROC_AUC"] * 100, 1),
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "TP": tp,
        **search.best_params_,
    }])

    csv_path = PROJECT_ROOT / "xgb_tuning_results.csv"
    txt_path = PROJECT_ROOT / "xgb_best_params.txt"

    results.to_csv(csv_path, index=False)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("XGBoost Hyperparameter Tuning Result\n")
        f.write("=" * 50 + "\n\n")
        f.write(results.to_string(index=False))
        f.write("\n\nBest Params:\n")
        for k, v in search.best_params_.items():
            f.write(f"{k}: {v}\n")

    print(f"\n✅ Saved CSV: {csv_path}")
    print(f"✅ Saved TXT: {txt_path}")
    print("\n📌 ابعتيلي النتائج اللي ظهرت تحت TEST RESULTS أو ملف xgb_tuning_results.csv")


if __name__ == "__main__":
    main()
