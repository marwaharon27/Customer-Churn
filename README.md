<div align="center">

<img
src="https://github.com/user-attachments/assets/219a453f-cdc4-4bb0-ad8a-61299051de77"
width="650"
/>

</div>

> **When 1 in 4 customers leaves every month — the answer is in the data.**

A full end-to-end data analysis project built as part of the **Digital Egypt Pioneers Initiative (DEPI) — Data Analysis Specialist Track**, analyzing 7,043 IBM telecom customer records across **5 tools** to identify churn drivers, quantify revenue impact, and deliver actionable retention strategies.

---

## 👥 Team Members

| Name | Role | Responsibilities |
|------|------|-----------------|
| **Marwa Haron** | Team Leader & Data Analyst | Project management, data preprocessing & cleaning, star schema data modeling, ML model development, Streamlit dashboard |
| **Salma Ahmed** | Data Analyst | Data preprocessing & cleaning, star schema data modeling, ML model development, Streamlit dashboard |
| **Noor Kamal** | Data Analyst | Descriptive statistics & inferential statistics — source of insights and key findings |
| **Shahd Tawfik** | Data Analyst | Pivot tables & analytical queries — source of insights and key findings |
| **Mariam Ahmed** | Data Analyst | Interactive dashboard design across Excel, Power BI & Tableau — source of insights and key findings |

**Instructor:** Dr. Amal Mahmoud

**Track:** Data Analysis Specialist (DEPI × YAT Learning Centers)

---

## 🏆 Project Highlights

- 🧑‍🤝‍🧑 **7,043** Customer Records
- 📋 **38** Features per Customer
- 🛠 **5 Tools** — Full Independent Implementation per Tool
- ⭐ **Star Schema** — 1 Fact Table + 5 Dimension Tables
- 📊 **3 Interactive Dashboards** (Excel, Power BI, Tableau)
- 🤖 **XGBoost ML Model** with Overfitting Detection & 5-Fold CV
- 🔮 **What-If Business Simulator** — Real retention strategy testing
- 🚨 **Priority Customer Watchlist** — Risk × Revenue ranking
- 📈 **Inferential Statistics** — T-Test, Chi-Square, ANOVA, Regression

---

## ❓ The Core Question

**Who leaves — and why?**

Traditional churn analysis describes the problem.
This project goes further: it predicts it, simulates solutions, and ranks which customers to save first.

---

## 🎯 Objectives

- Identify the root causes of telecom customer churn
- Quantify the financial impact across customer segments
- Build a Star Schema data model across multiple platforms
- Apply statistical analysis to validate findings
- Train a machine learning model to predict churn probability
- Simulate retention strategies and estimate their business impact
- Deliver interactive dashboards for both technical and executive audiences

---

## 💡 Key Insights

| Insight | Finding |
|---------|---------|
| 🔴 **The Loyalty Paradox** | Churned customers paid $74/mo vs $61 for retained — premium customers leave more |
| ⏱ **The 12-Month Cliff** | 47.4% churn in year 1 drops to 9.5% after year 4 |
| 🔒 **The Security Effect** | Online Security cuts churn from 41.8% → 14.6% (3× reduction) |
| 👴 **Senior Citizen Risk** | Seniors churn at 41.7% vs 23.6% for non-seniors |
| 🏆 **Competitor Gap** | 45% of churners left for competitors — no single dominant reason |
| 📋 **Contract Impact** | Month-to-Month = 45.8% churn vs 2.5% for Two-Year contracts |

---

## 🚀 Implementations

Each tool covers the **complete analytics lifecycle** independently — from raw data to final insights.

### 📊 Excel 
- Data Cleaning & Merging via Power Query
- Star Schema (1 Fact + 4 Dims) in Power Pivot
- Pivot Tables & Interactive Dashboards
- Descriptive Statistics + T-Test, Chi-Square, ANOVA, Regression
- Business Insights & Recommendations

### 🗄 SQL (MySQL) 
- Full Data Cleaning & Dataset Merging
- Star Schema (1 Fact + 5 Dims) with FK Constraints & Surrogate Keys
- Analytical Queries, Views & Stored Procedures
- Churn Risk Scoring Query
- FK Integrity Validation

### 🐍 Python 
- Data Cleaning & Feature Engineering (pandas)
- SQLite3 Star Schema Implementation
- EDA & Statistical Analysis
- XGBoost ML Model + 5-Fold Cross Validation
- Overfitting Detection (Train vs Test Gap)
- Streamlit Multi-Page Dashboard:
  - Executive Overview
  - Customer & Revenue Analytics
  - ML Prediction + Individual Customer Predictor
  - Priority Retention Watchlist
  - What-If Business Strategy Simulator

### 📈 Power BI 
- Power Query ETL Pipeline
- Data Modeling & DAX Measures
- Interactive Multi-Page Dashboard
- KPI Cards, Drill-Through Reports
- Executive Insights & Recommendations

### 📊 Tableau 
- Interactive Visual Analytics
- Geographic Churn Analysis
- Customer Segmentation Storytelling
- KPI Visualization & Risk Analysis

---

## 🗂 Data Sources

| Dataset | Source |
|---------|--------|
| Telco Customer Churn (IBM) | [Kaggle — blastchar](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) |
| Telecom Customer Churn by Maven Analytics | [Kaggle — shilongzhuang](https://www.kaggle.com/datasets/shilongzhuang/telecom-customer-churn-by-maven-analytics) |

---

## 🏗 Data Model — Star Schema
                Dim_Customer
                     │
      Dim_City ──── Fact_Telecom_Company ──── Dim_Contract
                     │
           Dim_Churn ── Dim_Services

| Table | Description |
|-------|-------------|
| `Fact_Telecom_Company` | Measures: charges, revenue, tenure, churn flag |
| `Dim_City` | City, Zip Code, Latitude, Longitude |
| `Dim_Contract` | Contract type, Payment Method, Billing, Offer |
| `Dim_Services` | 12 service-related attributes |
| `Dim_Churn` | Churn Category & Churn Reason |
| `Dim_Customer` | Demographics: age, gender, marital status, senior citizen |

> **Note:** Dim_Customer has a 1:1 relationship with the Fact Table enforced via UNIQUE constraint. All other Dims are 1:many.

---

## 🧹 Data Preprocessing

| Step | Action |
|------|--------|
| Merge | LEFT JOIN on `customer_id` across 2 IBM datasets |
| Deduplication | Removed all duplicate records |
| Null Handling | Context-aware: "No internet service", 0 for charges, "No churn" for retained |
| Standardization | Married → Married/Not Married, whitespace trimming |
| Feature Engineering | `Tenure_Group`, `Age_Group`, `Senior_Label` |
| Revenue Calculation | `(Monthly Charges × Tenure) + Extra Charges - Refunds` |

---

## 🤖 Machine Learning

**Model:** XGBoost Classifier
**Approach:** Business Feature Engineering + RandomUnderSampler + Tuned Threshold (0.66)

### Engineered Features include:
- `Charges_x_Tenure` — total spend proxy
- `New_Customer_Flag` — first 12 months indicator
- `Risk_Combo_M2M_Fiber_NoSecurity` — highest-risk customer combination
- `Risk_Combo_Full` — all 4 risk factors combined

### Model Results:

| Metric | Score |
|--------|-------|
| Accuracy | ~84% |
| Recall | ~73% |
| F1 Score | ~71% |
| Train-Test Gap | ~0.7 pts (No Overfitting) |
| 5-Fold CV Mean | ~83% |

---

## 📢 Recommendations

| Priority | Recommendation |
|----------|---------------|
| 🔴 High | Launch 6-month onboarding program to cut first-year churn |
| 🔴 High | Incentivize Month-to-Month → Annual contract migration |
| 🟡 Medium | Bundle Online Security in default packages (reduces churn 3×) |
| 🟡 Medium | Dedicated Senior Citizen retention plan |
| 🟡 Medium | Quarterly competitive pricing benchmarks |
| 🟢 Standard | Structured exit survey program |

---

## 🛠 Tech Stack

![Excel](https://img.shields.io/badge/Excel-217346?style=flat&logo=microsoft-excel&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat&logo=mysql&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?style=flat&logo=powerbi&logoColor=black)
![Tableau](https://img.shields.io/badge/Tableau-E97627?style=flat&logo=tableau&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-FF6600?style=flat&logoColor=white)

---

## 🇪🇬 About DEPI

This project was developed as part of the **Digital Egypt Pioneers Initiative (DEPI)** — a national program by the **Egyptian Ministry of Communications and Information Technology (MCIT)** in partnership with **YAT Learning Centers**, aiming to qualify the next generation of Egyptian data professionals.

---

> *Churn isn't random. It's predictable. And with the right data pipeline — it's preventable.*
