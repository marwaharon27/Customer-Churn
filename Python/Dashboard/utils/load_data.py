import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'telecom_churn.db')

def get_connection():
    return sqlite3.connect(DB_PATH)

def load_fact():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM Fact_Telecom_Company", conn)
    conn.close()
    return df

def load_full():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT 
            f.customer_id, f.tenure, f.Tenure_Group, f.Age_Group,
            f.monthly_charges, f.total_charges, f.Total_Revenue,
            f.Total_Refunds, f.Number_of_Referrals,
            f.Avg_Monthly_GB_Download,
            f.Total_Extra_Data_Charges,
            f.Total_Long_Distance_Charges,
            f.churn,
            dc.City, dc.Latitude, dc.Longitude,
            dct.Contract, dct.Payment_Method, dct.Offer, dct.Paperless_Billing,
            ds.Internet_Service, ds.Internet_Type, ds.Online_Security,
            ds.Online_Backup, ds.Device_Protection, ds.Premium_Tech_Support,
            ds.Streaming_TV, ds.Streaming_Movies, ds.Phone_Service,
            ds.Multiple_Lines, ds.Streaming_Music, ds.Unlimited_Data,
            dch.Churn_Category, dch.Churn_Reason,
            cu.gender, cu.SeniorCitizen, cu.Age, cu.Married,
            cu.Number_of_Dependents
        FROM Fact_Telecom_Company f
        LEFT JOIN Dim_City dc ON f.City_Key = dc.City_Key
        LEFT JOIN Dim_Contract dct ON f.Contract_Key = dct.Contract_Key
        LEFT JOIN Dim_Services ds ON f.Services_Key = ds.Services_Key
        LEFT JOIN Dim_Churn dch ON f.Churn_Key = dch.Churn_Key
        LEFT JOIN Dim_Customer cu ON f.customer_id = cu.customer_id
    """, conn)
    conn.close()
    return df

def load_kpis(df):
    total = len(df)
    churned = (df['churn'] == 'Yes').sum()
    churn_rate = round(100 * churned / total, 1)
    total_rev = df['Total_Revenue'].sum()
    rev_lost = df[df['churn'] == 'Yes']['Total_Revenue'].sum()
    avg_tenure = round(df['tenure'].mean(), 1)
    return {
        'total_customers': total,
        'churned': churned,
        'churn_rate': churn_rate,
        'total_revenue': total_rev,
        'revenue_lost': rev_lost,
        'avg_tenure': avg_tenure
    }