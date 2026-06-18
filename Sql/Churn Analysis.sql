-- Top 5 Cities by Churn Count
SELECT 
 Dim_City.City,
 COUNT(*) AS Churn_Count
FROM Fact_Telecom_Company
JOIN Dim_City ON Fact_Telecom_Company.City_Key = 
Dim_City.City_Key
JOIN Dim_Churn ON Fact_Telecom_Company.Churn_key = 
Dim_Churn.Churn_key
WHERE Fact_Telecom_Company.Churn = 'Yes'
GROUP BY Dim_City.City
ORDER BY Churn_Count DESC
LIMIT 5;

-- =====================================================================================================
-- Churn Rate by Tenure Bucket
SELECT 
 CASE 
 WHEN Fact_Telecom_Company.Tenure <= 12 THEN '0-12 
months'
 WHEN Fact_Telecom_Company.Tenure <= 24 THEN '13-24 
months'
 WHEN Fact_Telecom_Company.Tenure <= 48 THEN '25-48 
months'
 ELSE '49-72 months'
 END AS Tenure_Bucket,
 ROUND(100.0 * SUM(CASE WHEN Fact_Telecom_Company.Churn  = 
'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS Churn_Rate
FROM Fact_Telecom_Company
JOIN Dim_Churn ON Fact_Telecom_Company.Churn_key = 
Dim_Churn.Churn_key
GROUP BY Tenure_Bucket
ORDER BY Tenure_Bucket;

-- =====================================================================================================
-- Churn by Contract
SELECT 
 Dim_Contract.Contract,
 ROUND(100.0 * SUM(CASE WHEN Fact_Telecom_Company.Churn = 
'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS Churn_Rate
FROM Fact_Telecom_Company
JOIN Dim_Contract ON Fact_Telecom_Company.Contract_key  = 
Dim_Contract.Contract_key 
JOIN Dim_Churn ON Fact_Telecom_Company.Churn_key  = 
Dim_Churn.Churn_key 
GROUP BY Dim_Contract.Contract;
-- =====================================================================================================
-- Top 5 Churn Reasons
SELECT 
 Dim_Churn.Churn_Reason,
 COUNT(*) AS Reason_Count
FROM Fact_Telecom_Company
JOIN Dim_Churn ON Fact_Telecom_Company.Churn_key = 
Dim_Churn.Churn_key
WHERE Fact_Telecom_Company.Churn = 'Yes'
GROUP BY Dim_Churn.Churn_Reason
ORDER BY Reason_Count DESC
LIMIT 5;
-- =====================================================================================================
-- Count of Total Revenue Category—
SELECT 
 Dim_Churn.Churn_Category,
 COUNT(*) AS Category_Count
FROM Fact_Telecom_Company
JOIN Dim_Churn ON Fact_Telecom_Company.Churn_key = 
Dim_Churn.Churn_key
GROUP BY Dim_Churn.Churn_Category;

-- =====================================================================================================
-- Revenue Lost by Churn Category—
SELECT 
 Dim_Churn.Churn_Category,
SUM(Fact_Telecom_Company.Total_Revenue) AS Revenue_Lost
FROM Fact_Telecom_Company
JOIN Dim_Churn ON Fact_Telecom_Company.Churn_key = 
Dim_Churn.Churn_key
WHERE Fact_Telecom_Company.Churn = 'Yes'
GROUP BY Dim_Churn.Churn_Category;
-- =====================================================================================================
-- Customer Churn Distribution by Category
SELECT 
Dim_Churn.Churn_Category,
COUNT(Fact_Telecom_Company.customer_id) AS Customer_Count
FROM Fact_Telecom_Company
JOIN Dim_Churn 
ON Fact_Telecom_Company.Churn_key = Dim_Churn.Churn_key
WHERE Fact_Telecom_Company.Churn = 'Yes'
GROUP BY Dim_Churn.Churn_Category
ORDER BY Customer_Count DESC;
