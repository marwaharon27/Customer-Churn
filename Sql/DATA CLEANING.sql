-- Step 2: Rename Raw Tables
-- =====================================================================================================
RENAME TABLE customerchurn TO customerchurn_raw;
RENAME TABLE telecom_customer_churn TO telecom_customer_churn_raw;
-- =====================================================================================================
-- Step 3: Clean Table 1 - Customer Churn
-- ===================================================================================================
CREATE TABLE Churn AS
SELECT
    TRIM(customerID) AS customer_id,
    TRIM(gender) AS gender,
    CAST(SeniorCitizen AS UNSIGNED) AS SeniorCitizen,
    TRIM(Partner) AS Partner,
    TRIM(Dependents) AS Dependents,
    CAST(tenure AS UNSIGNED) AS tenure,
    TRIM(PhoneService) AS PhoneService,
    TRIM(MultipleLines) AS MultipleLines,
    TRIM(InternetService) AS InternetService,
    TRIM(OnlineSecurity) AS OnlineSecurity,
    TRIM(OnlineBackup) AS OnlineBackup,
    TRIM(DeviceProtection) AS DeviceProtection,
    TRIM(TechSupport) AS TechSupport,
    TRIM(StreamingTV) AS StreamingTV,
    TRIM(StreamingMovies) AS StreamingMovies,
    TRIM(Contract) AS Contract,
    TRIM(PaperlessBilling) AS PaperlessBilling,
    TRIM(PaymentMethod) AS PaymentMethod,
    CAST(MonthlyCharges AS DECIMAL(10,2)) AS monthly_charges,
    ROUND(CAST(MonthlyCharges AS DECIMAL(10,2)) * CAST(tenure AS UNSIGNED),2) AS total_charges,
    TRIM(Churn) AS churn

FROM customerchurn_raw;
SELECT * FROM Churn;

-- ===================================================================================================
-- Step 4: Clean Table 2 - Telecom Customer Churn
-- ===================================================================================================
CREATE TABLE telecom_customer_churn AS
SELECT
    TRIM(`Customer ID`) AS customer_id,
    TRIM(`Gender`) AS gender,

    CAST(`Age` AS UNSIGNED) AS Age,
    TRIM(`Married`) AS Married,
    CAST(`Number of Dependents` AS UNSIGNED) AS Number_of_Dependents,

    TRIM(`City`) AS City,
    CAST(`Zip Code` AS UNSIGNED) AS Zip_Code,

    CAST(`Latitude` AS DECIMAL(10,6)) AS Latitude,
    CAST(`Longitude` AS DECIMAL(10,6)) AS Longitude,

    CAST(`Number of Referrals` AS UNSIGNED) AS Number_of_Referrals,
    CAST(`Tenure in Months` AS UNSIGNED) AS tenure,

    TRIM(`Offer`) AS Offer,

    TRIM(`Phone Service`) AS Phone_Service,

    CASE
        WHEN TRIM(`Phone Service`) = 'No' THEN 0
        ELSE CAST(NULLIF(TRIM(`Avg Monthly Long Distance Charges`), '') AS DECIMAL(10,2))
    END AS Avg_Monthly_Long_Distance_Charges,

    CASE
        WHEN TRIM(`Phone Service`) = 'No' THEN 'No phone service'
        ELSE TRIM(`Multiple Lines`)
    END AS Multiple_Lines,

    TRIM(`Internet Service`) AS Internet_Service,

    CASE
        WHEN TRIM(`Internet Service`) = 'No' THEN 'No internet'
        ELSE TRIM(`Internet Type`)
    END AS Internet_Type,

    CASE
        WHEN TRIM(`Internet Service`) = 'No'
             OR TRIM(`Internet Type`) = 'No internet'
        THEN 0
        ELSE CAST(NULLIF(TRIM(`Avg Monthly GB Download`), '') AS UNSIGNED)
    END AS Avg_Monthly_GB_Download,

    CASE WHEN TRIM(`Internet Service`) = 'No' THEN 'No internet service' ELSE TRIM(`Online Security`) END AS Online_Security,
    CASE WHEN TRIM(`Internet Service`) = 'No' THEN 'No internet service' ELSE TRIM(`Online Backup`) END AS Online_Backup,
    CASE WHEN TRIM(`Internet Service`) = 'No' THEN 'No internet service' ELSE TRIM(`Device Protection Plan`) END AS Device_Protection,
    CASE WHEN TRIM(`Internet Service`) = 'No' THEN 'No internet service' ELSE TRIM(`Premium Tech Support`) END AS Premium_Tech_Support,
    CASE WHEN TRIM(`Internet Service`) = 'No' THEN 'No internet service' ELSE TRIM(`Streaming TV`) END AS Streaming_TV,
    CASE WHEN TRIM(`Internet Service`) = 'No' THEN 'No internet service' ELSE TRIM(`Streaming Movies`) END AS Streaming_Movies,
    CASE WHEN TRIM(`Internet Service`) = 'No' THEN 'No internet service' ELSE TRIM(`Streaming Music`) END AS Streaming_Music,
    CASE WHEN TRIM(`Internet Service`) = 'No' THEN 'No internet service' ELSE TRIM(`Unlimited Data`) END AS Unlimited_Data,

    TRIM(`Contract`) AS Contract,
    TRIM(`Paperless Billing`) AS Paperless_Billing,
    TRIM(`Payment Method`) AS Payment_Method,

    CAST(`Monthly Charge` AS DECIMAL(10,2)) AS monthly_charges,
    CAST(`Total Charges` AS DECIMAL(10,2)) AS total_charges,

    CAST(`Total Refunds` AS DECIMAL(10,2)) AS Total_Refunds,
    CAST(`Total Extra Data Charges` AS DECIMAL(10,2)) AS Total_Extra_Data_Charges,
    CAST(`Total Long Distance Charges` AS DECIMAL(10,2)) AS Total_Long_Distance_Charges,
    CAST(`Total Revenue` AS DECIMAL(10,2)) AS Total_Revenue,

    CASE
        WHEN TRIM(`Customer Status`) IN ('Stayed', 'Joined') THEN 'No'
        ELSE 'Yes'
    END AS churn,

    CASE
        WHEN TRIM(`Customer Status`) IN ('Stayed', 'Joined') THEN 'No churn'
        ELSE COALESCE(NULLIF(TRIM(`Churn Category`), ''), 'Unknown')
    END AS Churn_Category,

    CASE
        WHEN TRIM(`Customer Status`) IN ('Stayed', 'Joined') THEN 'No churn'
        ELSE COALESCE(NULLIF(TRIM(`Churn Reason`), ''), 'Unknown')
    END AS Churn_Reason

FROM telecom_customer_churn_raw;

SELECT * FROM telecom_customer_churn;

-- ===================================================================================================
-- Step 5: Create Table Telecom Merged 
-- ===================================================================================================
CREATE TABLE telecom_merged AS
SELECT
    t.customer_id,
    t.gender,
    t.Age,
    t.Married,
    t.Number_of_Dependents,
    t.City,
    t.Zip_Code,
    t.Latitude,
    t.Longitude,
    t.Number_of_Referrals,
    t.tenure,
    t.Offer,
    t.Phone_Service,
    t.Avg_Monthly_Long_Distance_Charges,
    t.Multiple_Lines,
    t.Internet_Service,
    t.Internet_Type,
    t.Avg_Monthly_GB_Download,
    t.Online_Security,
    t.Online_Backup,
    t.Device_Protection,
    t.Premium_Tech_Support,
    t.Streaming_TV,
    t.Streaming_Movies,
    t.Streaming_Music,
    t.Unlimited_Data,
    t.Contract,
    t.Paperless_Billing,
    t.Payment_Method,
    c.monthly_charges,

    ROUND(c.monthly_charges * t.tenure, 2) AS total_charges,

    t.Total_Extra_Data_Charges,
    t.Total_Long_Distance_Charges,
    t.Total_Refunds,

    ROUND(
        (c.monthly_charges * t.tenure)
        + t.Total_Extra_Data_Charges
        + t.Total_Long_Distance_Charges
        - t.Total_Refunds,
    2) AS Total_Revenue,

    t.churn,
    t.Churn_Category,
    t.Churn_Reason,
    c.SeniorCitizen

FROM telecom_customer_churn t
LEFT JOIN Churn c
ON t.customer_id = c.customer_id;

SELECT * FROM telecom_merged;
