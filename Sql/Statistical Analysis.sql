-- Correlation referrals vs tenure 
SELECT 
    ROUND(
        (COUNT(*) * SUM(Number_of_Referrals * tenure)
        - SUM(Number_of_Referrals) * SUM(tenure))
        /
        SQRT(
            (COUNT(*) * SUM(Number_of_Referrals * Number_of_Referrals)
            - POW(SUM(Number_of_Referrals),2))
            *
            (COUNT(*) * SUM(tenure * tenure)
            - POW(SUM(tenure),2))
        )
    ,4) AS Corr_Referrals_Tenure,
    'Customers who bring referrals stay longer.' AS Insight
FROM fact_telecom_company;

-- Correlation monthly_charges vs tenure 

SELECT 
    ROUND(
        (COUNT(*) * SUM(monthly_charges * tenure) - SUM(monthly_charges) * SUM(tenure))
        / SQRT(
            (COUNT(*) * SUM(monthly_charges * monthly_charges) - POW(SUM(monthly_charges), 2)) *
            (COUNT(*) * SUM(tenure * tenure) - POW(SUM(tenure), 2))
        )
    , 4) AS Corr_Monthly_Charges_Tenure,
    'Charges have a weaker correlation with tenure.' AS Insight
FROM fact_telecom_company;

-- =====================================================================================================
-- inferntial Stat (chi square)
-- Senior vs Churn

SELECT
    CASE
        WHEN dc.SeniorCitizen = 0 THEN 'Non-Senior'
        ELSE 'Senior'
    END AS Group_Name,
    f.Churn,
    COUNT(*) AS Observed,
    ROUND(
        SUM(COUNT(*)) OVER (PARTITION BY dc.SeniorCitizen)
        * SUM(COUNT(*)) OVER (PARTITION BY f.Churn)
        / SUM(COUNT(*)) OVER ()
    ,2) AS Expected,
    CASE
        WHEN dc.SeniorCitizen = 1 AND f.Churn = 'Yes' THEN 'Seniors churn significantly more than expected.'
        WHEN dc.SeniorCitizen = 0 AND f.Churn = 'Yes' THEN 'Non-seniors churn less than expected.'
        WHEN dc.SeniorCitizen = 1 AND f.Churn = 'No' THEN 'Seniors show lower retention rates.'
        ELSE 'Non-seniors show higher retention loyalty.'
    END AS Insight
FROM Fact_Telecom_Company f
JOIN Dim_Customer dc
ON f.customer_id = dc.customer_id
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
    , 2) AS Expected,
    CASE
        WHEN f.Churn = 'Yes' THEN 'Gender shows no significant impact on churn.'
        ELSE 'Retention rates are similar across genders.'
    END AS Insight
FROM Fact_Telecom_Company f
JOIN Dim_Customer dc
    ON f.customer_id = dc.customer_id
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
    , 2) AS Expected,
    CASE 
        WHEN dc.Married = 'Yes' AND f.Churn = 'Yes'
            THEN 'Married customers churn less than expected.'
        WHEN dc.Married = 'No' AND f.Churn = 'Yes'
            THEN 'Unmarried customers churn more than expected.'
        WHEN dc.Married = 'Yes' AND f.Churn = 'No'
            THEN 'Married customers show higher retention.'
        ELSE 'Unmarried customers have lower retention.'
    END AS Insight
FROM Fact_Telecom_Company f
JOIN Dim_Customer dc
    ON f.customer_id = dc.customer_id
GROUP BY dc.Married, f.Churn
ORDER BY dc.Married, f.Churn;



-- =====================================================================================================
-- t test
-- Group Stats

SELECT
    Churn,
    COUNT(*)                               AS N,
    ROUND(AVG(monthly_charges), 2)         AS Mean_Charges,
    ROUND(VARIANCE(monthly_charges), 2)   AS Variance_Charges,
    CASE 
        WHEN Churn = 'Yes' THEN 'Churned paid higher charges.'
        ELSE 'Retained paid lower charges.'
    END                                    AS Charges_Insight,
    ROUND(AVG(tenure), 2)                  AS Mean_Tenure,
    ROUND(VARIANCE(tenure), 2)             AS Variance_Tenure,
    CASE 
        WHEN Churn = 'Yes' THEN 'Churned had shorter tenure.'
        ELSE 'Retained had longer tenure.'
    END                                    AS Tenure_Insight
FROM fact_telecom_company
GROUP BY Churn;


-- t-statistic monthly_charges 
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
, 3) AS t_stat_monthly_charges,
    'Churned customers paid higher monthly charges.' AS Insight
FROM stats;

-- t-statistic tenure 

WITH stats AS (
    SELECT 
        churn, 
        COUNT(*) AS n,
        AVG(tenure) AS mean,
        VARIANCE(tenure) AS var
    FROM fact_telecom_company 
    GROUP BY churn
)
SELECT 
    ROUND(
        (MAX(CASE WHEN churn = 'Yes' THEN mean END) - MAX(CASE WHEN churn = 'No' THEN mean END))
        / SQRT(
            MAX(CASE WHEN churn = 'Yes' THEN var / n END) 
            + MAX(CASE WHEN churn = 'No' THEN var / n END)
        )
    , 3) AS t_stat_tenure,
    'Churned customers have shorter tenure.' AS Insight
FROM stats;

