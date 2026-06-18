-- Revenue by Payment Method—
SELECT 
Dim_Contract.Payment_Method,
CASE 
    WHEN SUM(Fact_Telecom_Company.Total_Revenue) >= 1000000 
        THEN CONCAT(ROUND(SUM(Fact_Telecom_Company.Total_Revenue)/1000000,2), ' M')
	
    WHEN SUM(Fact_Telecom_Company.Total_Revenue) >= 1000 
        THEN CONCAT(ROUND(SUM(Fact_Telecom_Company.Total_Revenue)/1000,2), ' K')
        
    ELSE FORMAT(SUM(Fact_Telecom_Company.Total_Revenue),2)
END AS Total_Revenue
FROM Fact_Telecom_Company
JOIN Dim_Contract 
ON Fact_Telecom_Company.Contract_Key = Dim_Contract.Contract_Key
GROUP BY Dim_Contract.Payment_Method;
-- =====================================================================================================
-- Revenue by Contract Duration
SELECT 
Dim_Contract.Contract,
CONCAT(ROUND(SUM(Fact_Telecom_Company.Total_Revenue)/1000000,2),' M') AS Total_Revenue
FROM Fact_Telecom_Company
JOIN Dim_Contract 
ON Fact_Telecom_Company.Contract_Key = Dim_Contract.Contract_Key
GROUP BY Dim_Contract.Contract
ORDER BY SUM(Fact_Telecom_Company.Total_Revenue) DESC;
-- =====================================================================================================
-- Customer Preference for Payment Method
SELECT 
Dim_Contract.Payment_Method,
COUNT(DISTINCT Fact_Telecom_Company.customer_id) AS Customer_Count
FROM Fact_Telecom_Company
JOIN Dim_Contract 
ON Fact_Telecom_Company.Contract_Key = Dim_Contract.Contract_Key
GROUP BY Dim_Contract.Payment_Method
ORDER BY Customer_Count DESC;
-- =====================================================================================================
-- KPIs
-- Total Customers—
SELECT COUNT(*) AS Total_Customers 
FROM Fact_Telecom_Company;
-- Churn Rate %—
SELECT 
 ROUND(100.0 * SUM(CASE WHEN Fact_Telecom_Company.Churn = 
'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS 
Churn_Rate_Percentage
FROM Fact_Telecom_Company
JOIN Dim_Churn ON Fact_Telecom_Company.Churn_key = 
Dim_Churn.Churn_key;

-- Total Churned—
SELECT COUNT(*) AS Total_Churned
FROM Fact_Telecom_Company
JOIN Dim_Churn ON Fact_Telecom_Company.Churn_Key = 
Dim_Churn.Churn_Key
WHERE Fact_Telecom_Company.Churn = 'Yes';
-- Revenue Loss—
SELECT 
CONCAT(ROUND(SUM(Total_Revenue)/1000000, 2), ' M') AS Revenue_Lost
FROM Fact_Telecom_Company
JOIN Dim_Churn 
ON Fact_Telecom_Company.Churn_Key = Dim_Churn.Churn_Key
WHERE Fact_Telecom_Company.Churn = 'Yes';

-- Total Revenue—
SELECT SUM(Total_Revenue) AS Total_Revenue 
FROM Fact_Telecom_Company;
