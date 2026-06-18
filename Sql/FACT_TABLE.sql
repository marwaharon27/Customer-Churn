-- Step 11: Create Table Fact_Telecom_Company
-- =====================================================================================================
CREATE TABLE Fact_Telecom_Company(
    customer_id VARCHAR(50),
    City_Key INT,
    Contract_Key INT,
    Services_Key INT,
    churn_key INT,
    tenure INT,
    Tenure_Group VARCHAR(50),
    monthly_charges DECIMAL(10,2),
    total_charges DECIMAL(10,2),
    Total_Revenue DECIMAL(10,2),
  Avg_Monthly_Long_Distance_Charges DECIMAL(10,2),
  Avg_Monthly_GB_Download DECIMAL(10,2),
  Total_Extra_Data_Charges DECIMAL(10,2),
  Total_Long_Distance_Charges DECIMAL(10,2),
   Total_Refunds DECIMAL(10,2),
    Number_of_Referrals INT,
    Churn VARCHAR(50)
);
-- =====================================================================================================
ALTER TABLE telecom_merged
ADD COLUMN Tenure_Group VARCHAR(20);

SET SQL_SAFE_UPDATES = 0;
UPDATE telecom_merged
SET Tenure_Group = 
CASE
    WHEN tenure BETWEEN 0 AND 12 THEN '0-12 months'
    WHEN tenure BETWEEN 13 AND 24 THEN '13-24 months'
    WHEN tenure BETWEEN 25 AND 48 THEN '25-48 months'
    WHEN tenure BETWEEN 49 AND 72 THEN '49-72 months'
    ELSE 'Unknown'
END;
-- =====================================================================================================

INSERT INTO Fact_Telecom_Company
SELECT 
m.customer_id,
c.City_Key,
ct.Contract_Key,
s.Services_Key,
ch.churn_key,
m.tenure,
m.Tenure_Group,
m.monthly_charges, 
m.total_charges ,
m.Total_Revenue,
m.Avg_Monthly_Long_Distance_Charges,
m.Avg_Monthly_GB_Download,
m.Total_Extra_Data_Charges,
m.Total_Long_Distance_Charges,
m.Total_Refunds,
m.Number_of_Referrals,
m.Churn
FROM telecom_merged m

LEFT JOIN Dim_City c
ON m.City = c.City 
AND m.Zip_Code = c.Zip_Code
AND m. Latitude = c. Latitude
AND m. Longitude = c. Longitude	

-- Contract
LEFT JOIN Dim_Contract ct
ON m.Contract = ct.Contract
AND m.Payment_Method = ct.Payment_Method
AND m.Paperless_Billing = ct.Paperless_Billing
AND m.Offer = ct.Offer

-- Services 
LEFT JOIN Dim_Services s
ON m.Phone_Service = s.Phone_Service
AND m.Internet_Service = s.Internet_Service
AND m.Multiple_Lines = s.Multiple_Lines
AND m.Internet_Type = s.Internet_Type
AND m.Online_Security = s.Online_Security
AND m.Online_Backup = s.Online_Backup
AND m.Device_Protection = s.Device_Protection
AND m.Premium_Tech_Support = s.Premium_Tech_Support
AND m.Streaming_TV = s.Streaming_TV
AND m.Streaming_Movies = s.Streaming_Movies
AND m.Streaming_Music = s.Streaming_Music
AND m.Unlimited_Data = s.Unlimited_Data

-- Churn
LEFT JOIN Dim_Churn ch
ON m.Churn_Category = ch.Churn_Category
AND m.Churn_Reason = ch.Churn_Reason;

-- FOREIGN KEYS

ALTER TABLE Fact_Telecom_Company
ADD FOREIGN KEY (City_Key) REFERENCES Dim_City(City_Key);

ALTER TABLE Fact_Telecom_Company
ADD FOREIGN KEY (Contract_Key) REFERENCES Dim_Contract(Contract_Key);

ALTER TABLE Fact_Telecom_Company
ADD FOREIGN KEY (Services_Key) REFERENCES Dim_Services(Services_Key);

ALTER TABLE Fact_Telecom_Company
ADD FOREIGN KEY (churn_key) REFERENCES Dim_Churn(churn_key);

ALTER TABLE Fact_Telecom_Company
ADD FOREIGN KEY (customer_id) REFERENCES Dim_Customer(customer_id);

SELECT * FROM fact_telecom_company;