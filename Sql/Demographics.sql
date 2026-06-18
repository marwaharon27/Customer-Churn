-- Avg Revenue by Married Status
SELECT 
 Dim_Customer.Married,
 ROUND(AVG(Fact_Telecom_Company.Total_Revenue), 2) AS Avg_Revenue
FROM Fact_Telecom_Company
JOIN Dim_Customer 
ON Fact_Telecom_Company.customer_id = Dim_Customer.customer_id
GROUP BY Dim_Customer.Married;
-- =====================================================================================================
-- Churn Rate Analysis by Age Group
SELECT 
 CASE 
 WHEN Dim_Customer.Age <= 30 THEN '18-30'
 WHEN Dim_Customer.Age <= 45 THEN '31-45'
 WHEN Dim_Customer.Age <= 60 THEN '46-60'
 ELSE '60+'
 END AS Age_Group,
 ROUND(100.0 * SUM(CASE WHEN Fact_Telecom_Company.Churn = 
'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS Churn_Rate
FROM Fact_Telecom_Company
JOIN Dim_Churn ON Fact_Telecom_Company.Churn_key = Dim_Churn.Churn_key
JOIN Dim_Customer ON Fact_Telecom_Company.customer_id = Dim_Customer.customer_id
GROUP BY Age_Group
ORDER BY Age_Group;
-- =====================================================================================================
-- Churn Rate: Senior vs Non-Senior
SELECT 
 Dim_Customer.SeniorCitizen,
 ROUND(100.0 * SUM(CASE WHEN Fact_Telecom_Company.Churn = 
'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS Churn_Rate
FROM Fact_Telecom_Company
JOIN Dim_Churn ON Fact_Telecom_Company.Churn_key = Dim_Churn.Churn_key
JOIN Dim_Customer ON Fact_Telecom_Company.customer_id = Dim_Customer.customer_id
GROUP BY Dim_Customer.SeniorCitizen;
-- =====================================================================================================
-- Avg Revenue Married—-
SELECT ROUND(AVG(Fact_Telecom_Company.Total_Revenue), 2) AS Avg_Revenue_Married
FROM Fact_Telecom_Company
JOIN Dim_Customer 
ON Fact_Telecom_Company.customer_id = Dim_Customer.customer_id
WHERE Dim_Customer.Married = 'Yes';

-- Senior Churn Rate ——
SELECT 
 ROUND(100.0 * SUM(CASE WHEN Fact_Telecom_Company.Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 
 2) AS Senior_Churn_Rate
FROM Fact_Telecom_Company
JOIN Dim_Churn 
ON Fact_Telecom_Company.Churn_Key = Dim_Churn.Churn_Key
JOIN Dim_Customer
ON Fact_Telecom_Company.customer_id = Dim_Customer.customer_id
WHERE Dim_Customer.SeniorCitizen = 1;
