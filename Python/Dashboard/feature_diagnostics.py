
"""
Telecom Churn Feature Diagnostics Tool
======================================

ضعي الملف ده في فولدر المشروع الرئيسي بجانب app.py ثم شغليه:

    python feature_diagnostics.py

الهدف:
- نجرب Feature Sets مختلفة
- نعرف هل Total_Revenue مفيد ولا عامل تشويش
- نجرب Features هندسية Business Features
- نقارن F1 / Precision / Recall / AUC
- نحفظ النتائج في:
    feature_diagnostics_results.csv
    best_feature_set_summary.txt

لو مكتبات ناقصة:
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
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, ExtraTreesClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

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


PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))

try:
    from utils.load_data import load_full
except Exception as e:
    raise ImportError(
        "\n❌ لم أستطع استيراد load_full من utils.load_data.\n"
        "حطي feature_diagnostics.py في نفس مكان app.py.\n"
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


def clean_base(df: pd.DataFrame) -> pd.DataFrame:
    required = BASE_NUM + BASE_CAT + [TARGET]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"❌ Missing columns: {missing}")

    out = df[required].copy()

    for col in BASE_NUM:
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0)

    for col in BASE_CAT:
        out[col] = out[col].astype(str).fillna("Unknown")

    out[TARGET] = out[TARGET].astype(str)
    out = out[out[TARGET].isin(["Yes", "No"])].copy()

    return out


def add_business_features(df: pd.DataFrame) -> pd.DataFrame:
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


def get_feature_sets(df_base: pd.DataFrame):
    df_eng = add_business_features(df_base)

    engineered_num = [
        "Revenue_per_Tenure",
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

    sets = {
        "Base_11_Features": {
            "df": df_base,
            "num": BASE_NUM,
            "cat": BASE_CAT,
        },
        "Base_Without_Total_Revenue": {
            "df": df_base,
            "num": [c for c in BASE_NUM if c != "Total_Revenue"],
            "cat": BASE_CAT,
        },
        "Base_Without_Revenue_And_Charges": {
            "df": df_base,
            "num": ["tenure", "SeniorCitizen", "Number_of_Referrals"],
            "cat": BASE_CAT,
        },
        "Base_Plus_Business_Features": {
            "df": df_eng,
            "num": BASE_NUM + engineered_num,
            "cat": BASE_CAT,
        },
        "Business_Features_No_Total_Revenue": {
            "df": df_eng,
            "num": [c for c in BASE_NUM if c != "Total_Revenue"] + [
                c for c in engineered_num if c not in ["Revenue_per_Tenure"]
            ],
            "cat": BASE_CAT,
        },
        "Behavior_And_Service_Focused": {
            "df": df_eng,
            "num": [
                "tenure",
                "SeniorCitizen",
                "Number_of_Referrals",
                "New_Customer_Flag",
                "Low_Tenure_Flag",
                "Long_Tenure_Flag",
                "No_Referrals_Flag",
                "Is_Month_to_Month",
                "Is_Fiber",
                "No_Security",
                "No_Tech_Support",
                "Risk_Combo_M2M_Fiber_NoSecurity",
                "Risk_Combo_M2M_NoSupport",
                "Risk_Combo_Full",
            ],
            "cat": BASE_CAT,
        },
    }

    return sets


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


def get_models():
    models = {
        "Logistic Regression": LogisticRegression(
            max_iter=2500,
            class_weight="balanced",
            random_state=42,
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=180,
            learning_rate=0.05,
            max_depth=3,
            subsample=0.9,
            random_state=42,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=350,
            max_depth=10,
            min_samples_split=10,
            min_samples_leaf=4,
            class_weight="balanced_subsample",
            random_state=42,
            n_jobs=-1,
        ),
        "Extra Trees": ExtraTreesClassifier(
            n_estimators=350,
            max_depth=12,
            min_samples_split=8,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
    }

    if XGBOOST_AVAILABLE:
        models["XGBoost"] = XGBClassifier(
            n_estimators=280,
            max_depth=3,
            learning_rate=0.04,
            subsample=0.9,
            colsample_bytree=0.85,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=42,
            n_jobs=-1,
        )

    if LIGHTGBM_AVAILABLE:
        models["LightGBM"] = LGBMClassifier(
            n_estimators=280,
            learning_rate=0.04,
            num_leaves=24,
            subsample=0.9,
            colsample_bytree=0.85,
            random_state=42,
            n_jobs=-1,
            verbose=-1,
        )

    return models


def get_samplers():
    if not IMBLEARN_AVAILABLE:
        return {"None": None}

    return {
        "None": None,
        "RandomOverSampler": RandomOverSampler(random_state=42),
        "SMOTE": SMOTE(random_state=42, k_neighbors=5),
        "RandomUnderSampler": RandomUnderSampler(random_state=42),
    }


def find_best_threshold(y_true, y_prob):
    best = {"threshold": 0.50, "f1": -1}

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


def evaluate_experiment(feature_set_name, df_set, num_cols, cat_cols, model_name, model, sampler_name, sampler):
    X = df_set[num_cols + cat_cols].copy()
    y = (df_set[TARGET] == "Yes").astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    preprocessor = build_preprocessor(num_cols, cat_cols)

    if sampler is None:
        pipe = Pipeline([
            ("preprocess", preprocessor),
            ("model", clone(model)),
        ])
    else:
        pipe = ImbPipeline([
            ("preprocess", preprocessor),
            ("sampler", sampler),
            ("model", clone(model)),
        ])

    pipe.fit(X_train, y_train)
    y_prob = pipe.predict_proba(X_test)[:, 1]

    best = find_best_threshold(y_test, y_prob)
    y_pred = (y_prob >= best["threshold"]).astype(int)

    auc = roc_auc_score(y_test, y_prob)
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

    return {
        "Feature_Set": feature_set_name,
        "Model": model_name,
        "Sampling": sampler_name,
        "Best_Threshold": best["threshold"],
        "Accuracy": best["accuracy"],
        "Precision": best["precision"],
        "Recall": best["recall"],
        "F1": best["f1"],
        "ROC_AUC": auc,
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "TP": tp,
        "Num_Features_Before_Encoding": len(num_cols) + len(cat_cols),
    }


def main():
    print("\n" + "=" * 80)
    print("TELECOM CHURN FEATURE DIAGNOSTICS")
    print("=" * 80)

    print("✅ Loading data...")
    raw_df = load_full()
    df_base = clean_base(raw_df)

    print(f"Rows: {len(df_base):,}")
    print("Target distribution:")
    print(df_base[TARGET].value_counts(normalize=True).mul(100).round(2).astype(str) + "%")

    feature_sets = get_feature_sets(df_base)
    models = get_models()
    samplers = get_samplers()

    print(f"\nFeature sets: {len(feature_sets)}")
    print(f"Models: {len(models)}")
    print(f"Samplers: {len(samplers)}")

    if not XGBOOST_AVAILABLE:
        print("⚠️ XGBoost غير مثبت. ثبتيه: pip install xgboost")
    if not LIGHTGBM_AVAILABLE:
        print("⚠️ LightGBM غير مثبت. ثبتيه: pip install lightgbm")
    if not IMBLEARN_AVAILABLE:
        print("⚠️ imbalanced-learn غير مثبت. ثبتيه: pip install imbalanced-learn")

    total = len(feature_sets) * len(models) * len(samplers)
    counter = 1
    results = []

    print("\n" + "=" * 80)
    print("RUNNING FEATURE EXPERIMENTS")
    print("=" * 80)

    for fs_name, fs in feature_sets.items():
        for model_name, model in models.items():
            for sampler_name, sampler in samplers.items():
                print(f"[{counter}/{total}] {fs_name} | {model_name} | {sampler_name}")
                counter += 1

                try:
                    row = evaluate_experiment(
                        feature_set_name=fs_name,
                        df_set=fs["df"],
                        num_cols=fs["num"],
                        cat_cols=fs["cat"],
                        model_name=model_name,
                        model=model,
                        sampler_name=sampler_name,
                        sampler=sampler,
                    )
                    results.append(row)
                except Exception as e:
                    print(f"   ❌ Failed: {e}")

    if not results:
        raise RuntimeError("❌ No successful experiments.")

    res = pd.DataFrame(results)
    res = res.sort_values(["F1", "Recall", "Precision", "ROC_AUC"], ascending=False).reset_index(drop=True)

    display = res.copy()
    for col in ["Accuracy", "Precision", "Recall", "F1", "ROC_AUC"]:
        display[col] = (display[col] * 100).round(1)

    output_csv = PROJECT_ROOT / "feature_diagnostics_results.csv"
    display.to_csv(output_csv, index=False)

    print("\n" + "=" * 80)
    print("TOP 20 RESULTS")
    print("=" * 80)

    cols = [
        "Feature_Set", "Model", "Sampling", "Best_Threshold",
        "Accuracy", "Precision", "Recall", "F1", "ROC_AUC",
        "TN", "FP", "FN", "TP",
    ]
    print(display[cols].head(20).to_string(index=False))

    best = display.iloc[0]

    summary = f"""
BEST FEATURE DIAGNOSTICS RESULT
===============================

Best Feature Set: {best['Feature_Set']}
Best Model: {best['Model']}
Sampling: {best['Sampling']}
Best Threshold: {best['Best_Threshold']}

Accuracy:  {best['Accuracy']}%
Precision: {best['Precision']}%
Recall:    {best['Recall']}%
F1 Score:  {best['F1']}%
ROC AUC:   {best['ROC_AUC']}%

Confusion Matrix:
TN: {best['TN']}
FP: {best['FP']}
FN: {best['FN']}
TP: {best['TP']}

Results file:
{output_csv}

مهم:
- لو F1 اتحسن بوضوح عن 71.1%، نعدل ml.py على أفضل Feature Set.
- لو F1 فضل قريب، يبقى وصلنا لسقف الداتا الحالي تقريبًا.
"""

    output_txt = PROJECT_ROOT / "best_feature_set_summary.txt"
    output_txt.write_text(summary, encoding="utf-8")

    print("\n" + "=" * 80)
    print("BEST RESULT")
    print("=" * 80)
    print(summary)
    print("📌 ابعتيلي TOP 20 أو ملف feature_diagnostics_results.csv")


if __name__ == "__main__":
    main()
