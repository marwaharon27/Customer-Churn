-- Tech Support Requested by Internet Type
SELECT
    Dim_Services.Internet_Type,
    SUM(CASE
            WHEN Dim_Services.Premium_Tech_Support = 'Yes'
            THEN 1
            ELSE 0
        END) AS Tech_Support_Yes,
    SUM(CASE
            WHEN Dim_Services.Premium_Tech_Support = 'No'
            THEN 1
            ELSE 0
        END) AS Tech_Support_No
FROM Fact_Telecom_Company
JOIN Dim_Services
ON Fact_Telecom_Company.Services_Key = Dim_Services.Services_Key
WHERE Dim_Services.Internet_Type <> 'No Internet'
GROUP BY Dim_Services.Internet_Type
ORDER BY
    CASE Dim_Services.Internet_Type
        WHEN 'Cable' THEN 1
        WHEN 'DSL' THEN 2
        WHEN 'Fiber Optic' THEN 3
        ELSE 4
    END;
-- =====================================================================================================
-- KPIs
-- Fiber Optic Churned
SELECT 
    SUM(CASE WHEN Dim_Services.Premium_Tech_Support = 'Yes' THEN 1 ELSE 0 END) AS Fiber_Yes
FROM Fact_Telecom_Company
JOIN Dim_Services 
ON Fact_Telecom_Company.Services_Key = Dim_Services.Services_Key
WHERE Dim_Services.Internet_Type = 'Fiber Optic';