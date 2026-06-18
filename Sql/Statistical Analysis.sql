USE final_project;
-- =====================================================================================================
-- Descriptive Stat
-- monthly_charges
SELECT
    ROUND(AVG(monthly_charges), 2) AS Mean,
    ROUND(STDDEV(monthly_charges), 2) AS Std_Dev,
    ROUND(VARIANCE(monthly_charges), 2) AS Variance,
    ROUND(MIN(monthly_charges), 2) AS Minimum,
    ROUND(MAX(monthly_charges), 2) AS Maximum,
    ROUND(MAX(monthly_charges) - MIN(monthly_charges), 2) AS `Range`,
    COUNT(*) AS `Count`,
    ROUND(SUM(monthly_charges), 2) AS `Sum`
FROM Fact_Telecom_Company;
-- tenure
SELECT
    ROUND(AVG(tenure), 2) AS Mean,
    ROUND(STDDEV(tenure), 2) AS Std_Dev,
    ROUND(VARIANCE(tenure), 2) AS Variance,
    MIN(tenure) AS Minimum,
    MAX(tenure) AS Maximum,
    (MAX(tenure) - MIN(tenure)) AS `Range`,
    COUNT(*) AS `Count`,
    SUM(tenure) AS `Sum`
FROM Fact_Telecom_Company;

-- Median monthly_charges
SELECT ROUND(AVG(monthly_charges), 2) AS Median_monthly_charges
FROM (
    SELECT monthly_charges,
           ROW_NUMBER() OVER (ORDER BY monthly_charges) AS rn,
           COUNT(*) OVER () AS total
    FROM fact_telecom_company
) t
WHERE rn IN (FLOOR((total+1)/2), CEIL((total+1)/2));

-- Median tenure
SELECT ROUND(AVG(tenure), 0) AS Median_tenure
FROM (
    SELECT tenure,
           ROW_NUMBER() OVER (ORDER BY tenure) AS rn,
           COUNT(*) OVER () AS total
    FROM fact_telecom_company
) t
WHERE rn IN (FLOOR((total+1)/2), CEIL((total+1)/2));

-- Quartiles tenure (Q1=9, Q2=29, Q3=55, IQR=46)
SELECT
    ROUND(AVG(CASE WHEN rn BETWEEN FLOOR(total*0.25) AND CEIL(total*0.25) THEN tenure END), 0) AS Q1,
    ROUND(AVG(CASE WHEN rn BETWEEN FLOOR(total*0.50) AND CEIL(total*0.50) THEN tenure END), 0) AS Q2_Median,
    ROUND(AVG(CASE WHEN rn BETWEEN FLOOR(total*0.75) AND CEIL(total*0.75) THEN tenure END), 0) AS Q3,
    ROUND(AVG(CASE WHEN rn BETWEEN FLOOR(total*0.75) AND CEIL(total*0.75) THEN tenure END), 0) -
    ROUND(AVG(CASE WHEN rn BETWEEN FLOOR(total*0.25) AND CEIL(total*0.25) THEN tenure END), 0) AS IQR
FROM (
    SELECT tenure,
           ROW_NUMBER() OVER (ORDER BY tenure) AS rn,
           COUNT(*) OVER () AS total
    FROM fact_telecom_company
) t;

-- Quartiles monthly_charges (Q1=35.5, Q2=70.35, Q3=89.85, IQR=54.35)
SELECT
    ROUND(AVG(CASE WHEN rn BETWEEN FLOOR(total*0.25) AND CEIL(total*0.25) THEN monthly_charges END), 2) AS Q1,
    ROUND(AVG(CASE WHEN rn BETWEEN FLOOR(total*0.50) AND CEIL(total*0.50) THEN monthly_charges END), 2) AS Q2_Median,
    ROUND(AVG(CASE WHEN rn BETWEEN FLOOR(total*0.75) AND CEIL(total*0.75) THEN monthly_charges END), 2) AS Q3,
    ROUND(AVG(CASE WHEN rn BETWEEN FLOOR(total*0.75) AND CEIL(total*0.75) THEN monthly_charges END), 2) -
    ROUND(AVG(CASE WHEN rn BETWEEN FLOOR(total*0.25) AND CEIL(total*0.25) THEN monthly_charges END), 2) AS IQR
FROM (
    SELECT monthly_charges,
           ROW_NUMBER() OVER (ORDER BY monthly_charges) AS rn,
           COUNT(*) OVER () AS total
    FROM fact_telecom_company
) t;

-- Correlation monthly_charges vs tenure (0.2476)
SELECT ROUND(
    (COUNT(*) * SUM(monthly_charges * tenure) - SUM(monthly_charges) * SUM(tenure))
    / SQRT(
        (COUNT(*) * SUM(monthly_charges*monthly_charges) - POW(SUM(monthly_charges),2)) *
        (COUNT(*) * SUM(tenure*tenure) - POW(SUM(tenure),2))
    )
, 4) AS Corr_Charges_Tenure
FROM fact_telecom_company;

-- Correlation referrals vs tenure (0.3270)
SELECT ROUND(
    (COUNT(*) * SUM(Number_of_Referrals * tenure) - SUM(Number_of_Referrals) * SUM(tenure))
    / SQRT(
        (COUNT(*) * SUM(Number_of_Referrals*Number_of_Referrals) - POW(SUM(Number_of_Referrals),2)) *
        (COUNT(*) * SUM(tenure*tenure) - POW(SUM(tenure),2))
    )
, 4) AS Corr_Referrals_Tenure
FROM fact_telecom_company;

-- =====================================================================================================
-- inferntial Stat (chi square)
-- Senior vs Churn
SELECT
    CASE WHEN dc.SeniorCitizen = 0 THEN 'Non-Senior' ELSE 'Senior' END AS Group_Name,
    f.Churn,
    COUNT(*) AS Observed,
    ROUND(
        SUM(COUNT(*)) OVER (PARTITION BY dc.SeniorCitizen)
        * SUM(COUNT(*)) OVER (PARTITION BY f.Churn)
        / SUM(COUNT(*)) OVER ()
    , 2) AS Expected
FROM fact_telecom_company f
JOIN dim_customer dc ON f.customer_id = dc.customer_id
GROUP BY dc.SeniorCitizen, f.Churn
ORDER BY dc.SeniorCitizen, f.Churn;

-- Gender vs Churn
SELECT
    dc.gender,
    f.Churn,
    COUNT(*) AS Observed,
    ROUND(
        SUM(COUNT(*)) OVER (PARTITION BY dc.gender)
        * SUM(COUNT(*)) OVER (PARTITION BY f.Churn)
        / SUM(COUNT(*)) OVER ()
    , 2) AS Expected
FROM fact_telecom_company f
JOIN dim_customer dc ON f.customer_id = dc.customer_id
GROUP BY dc.gender, f.Churn
ORDER BY dc.gender, f.Churn;

-- Married vs Churn
SELECT
    dc.Married,
    f.Churn,
    COUNT(*) AS Observed,
    ROUND(
        SUM(COUNT(*)) OVER (PARTITION BY dc.Married)
        * SUM(COUNT(*)) OVER (PARTITION BY f.Churn)
        / SUM(COUNT(*)) OVER ()
    , 2) AS Expected
FROM fact_telecom_company f
JOIN dim_customer dc ON f.customer_id = dc.customer_id
GROUP BY dc.Married, f.Churn
ORDER BY dc.Married, f.Churn;

-- Contract vs Churn
SELECT
    ct.Contract,
    f.Churn,
    COUNT(*) AS Observed,
    ROUND(
        SUM(COUNT(*)) OVER (PARTITION BY ct.Contract)
        * SUM(COUNT(*)) OVER (PARTITION BY f.Churn)
        / SUM(COUNT(*)) OVER ()
    , 2) AS Expected
FROM fact_telecom_company f
JOIN dim_contract ct ON f.Contract_Key = ct.Contract_Key
GROUP BY ct.Contract, f.Churn
ORDER BY ct.Contract, f.Churn;
-- =====================================================================================================
-- t test
-- Group Stats
SELECT
    Churn,
    COUNT(*)                             AS N,
    ROUND(AVG(monthly_charges), 2)       AS Mean_Charges,
    ROUND(VARIANCE(monthly_charges), 2)  AS Variance_Charges,
    ROUND(AVG(tenure), 2)                AS Mean_Tenure,
    ROUND(VARIANCE(tenure), 2)           AS Variance_Tenure
FROM fact_telecom_company
GROUP BY Churn;

-- t-statistic monthly_charges (النتيجة: 18.41)
WITH stats AS (
    SELECT 
        churn,
        COUNT(*) AS n,
        AVG(monthly_charges) AS mean,
        VARIANCE(monthly_charges) AS var
    FROM fact_telecom_company 
    GROUP BY churn
)
SELECT ROUND(
    (MAX(CASE WHEN churn='Yes' THEN mean END) - MAX(CASE WHEN churn='No' THEN mean END))
    / SQRT(MAX(CASE WHEN churn='Yes' THEN var/n END) + MAX(CASE WHEN churn='No' THEN var/n END))
, 3) AS t_stat_monthly_charges
FROM stats;

-- t-statistic tenure (النتيجة: -34.88)
WITH stats AS (
    SELECT 
        churn, 
        COUNT(*) AS n,
        AVG(tenure) AS mean,
        VARIANCE(tenure) AS var
    FROM fact_telecom_company 
    GROUP BY churn
)
SELECT ROUND(
    (MAX(CASE WHEN churn = 'Yes' THEN mean END) - MAX(CASE WHEN churn = 'No' THEN mean END))
    / SQRT(
        MAX(CASE WHEN churn = 'Yes' THEN var / n END) 
        + MAX(CASE WHEN churn = 'No' THEN var / n END)
    )
, 3) AS t_stat_tenure
FROM stats;
-- =====================================================================================================
-- ANOVA test
-- Group Summary (Month-to-Month: 66.40, One Year: 65.05, Two Year: 60.77)
SELECT
    c.Contract,
    COUNT(*)                              AS Count,
    ROUND(AVG(c.monthly_charges), 2)      AS Average,
    ROUND(VARIANCE(c.monthly_charges), 2) AS Variance
FROM churn c
GROUP BY c.Contract;

-- F-Statistic
WITH grp AS (
    SELECT c.Contract, COUNT(*) AS n, AVG(c.monthly_charges) AS gm
    FROM churn c
    GROUP BY c.Contract
),
grand AS (SELECT AVG(monthly_charges) AS gm FROM churn),
ssb AS (
    SELECT SUM(g.n * POW(g.gm - gr.gm, 2)) AS SSB, COUNT(*)-1 AS dfB
    FROM grp g, grand gr
),
ssw AS (
    SELECT SUM(POW(c.monthly_charges - gs.gm, 2)) AS SSW, COUNT(*)-3 AS dfW
    FROM churn c
    JOIN grp gs ON c.Contract = gs.Contract
)
SELECT
    ROUND(SSB/dfB, 2)              AS MS_Between,
    ROUND(SSW/dfW, 2)              AS MS_Within,
    ROUND((SSB/dfB)/(SSW/dfW), 3) AS F_Statistic,
    ROUND(SSB+SSW, 2)              AS SS_Total
FROM ssb, ssw;
-- =====================================================================================================
-- Correlations (Referrals: -0.257, Tenure: -0.357, Charges: +0.193)
SELECT
    ROUND(
        (COUNT(*) * SUM(cn * Number_of_Referrals) - SUM(cn) * SUM(Number_of_Referrals))
        / SQRT(
            (COUNT(*) * SUM(cn*cn) - POW(SUM(cn),2)) *
            (COUNT(*) * SUM(Number_of_Referrals*Number_of_Referrals) - POW(SUM(Number_of_Referrals),2))
        )
    , 4) AS Corr_Churn_Referrals,
    ROUND(
        (COUNT(*) * SUM(cn * tenure) - SUM(cn) * SUM(tenure))
        / SQRT(
            (COUNT(*) * SUM(cn*cn) - POW(SUM(cn),2)) *
            (COUNT(*) * SUM(tenure*tenure) - POW(SUM(tenure),2))
        )
    , 4) AS Corr_Churn_Tenure,
    ROUND(
        (COUNT(*) * SUM(cn * monthly_charges) - SUM(cn) * SUM(monthly_charges))
        / SQRT(
            (COUNT(*) * SUM(cn*cn) - POW(SUM(cn),2)) *
            (COUNT(*) * SUM(monthly_charges*monthly_charges) - POW(SUM(monthly_charges),2))
        )
    , 4) AS Corr_Churn_Charges
FROM (
    SELECT
        CASE WHEN Churn='Yes' THEN 1 ELSE 0 END AS cn,
        Number_of_Referrals, tenure, monthly_charges
    FROM fact_telecom_company
) t;
