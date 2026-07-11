-- Step 6: Create Table Dim_City
-- =====================================================================================================
CREATE TABLE Dim_City (
    City_Key INT AUTO_INCREMENT PRIMARY KEY,
    City VARCHAR(100),
    Zip_Code VARCHAR(20),
    Latitude DECIMAL(10,6),
    Longitude DECIMAL(10,6)
);
INSERT INTO Dim_City (City, Zip_Code, Latitude, Longitude)
SELECT DISTINCT
    City, Zip_Code, Latitude, Longitude
FROM telecom_merged;

SELECT * FROM Dim_City;

-- =====================================================================================================
-- Step 7: Create Table Dim_Contract
-- =====================================================================================================
CREATE TABLE Dim_Contract (
    Contract_Key INT AUTO_INCREMENT PRIMARY KEY,
    Contract VARCHAR(50),
    Payment_Method VARCHAR(50),
    Paperless_Billing VARCHAR(10),
    Offer VARCHAR(50)
);
INSERT INTO Dim_Contract (Contract, Payment_Method, Paperless_Billing, Offer)
SELECT DISTINCT
    Contract, Payment_Method, Paperless_Billing, Offer
FROM telecom_merged;

SELECT * FROM Dim_Contract;
-- =====================================================================================================
-- Step 8: Create Table Dim_Services
-- =====================================================================================================
CREATE TABLE Dim_Services (
Services_Key INT AUTO_INCREMENT PRIMARY KEY,
Phone_Service VARCHAR(20),
Internet_Service VARCHAR(20),
Multiple_Lines VARCHAR(50),
Internet_Type VARCHAR(50),
Online_Security VARCHAR(20),
Online_Backup VARCHAR(20),
Device_Protection VARCHAR(20),
Premium_Tech_Support VARCHAR(20),
Streaming_TV VARCHAR(20),
Streaming_Movies VARCHAR(20),
Streaming_Music VARCHAR(20),
Unlimited_Data VARCHAR(20)
);
INSERT INTO Dim_Services ( Phone_Service,
Internet_Service,
Multiple_Lines,
Internet_Type,
Online_Security,
Online_Backup,
Device_Protection,
Premium_Tech_Support,
Streaming_TV,
Streaming_Movies,
Streaming_Music,
Unlimited_Data
)

SELECT DISTINCT
Phone_Service,
Internet_Service,
Multiple_Lines,
Internet_Type,
Online_Security,
Online_Backup,
Device_Protection,
Premium_Tech_Support,
Streaming_TV,
Streaming_Movies,
Streaming_Music,
Unlimited_Data
FROM telecom_merged;

SELECT * FROM Dim_Services;

-- =====================================================================================================
-- Step 9: Create Table Dim_Churn
-- =====================================================================================================
CREATE TABLE Dim_Churn (
    churn_key INT AUTO_INCREMENT PRIMARY KEY,
    Churn_Category VARCHAR(50),
    Churn_Reason TEXT
);
INSERT INTO Dim_Churn (Churn_Category, Churn_Reason)
SELECT DISTINCT
    Churn_Category, Churn_Reason
FROM telecom_merged;

SELECT * FROM Dim_Churn;

-- =====================================================================================================
-- Step 10: Create Table Dim_Customer
-- =====================================================================================================
CREATE TABLE Dim_Customer (
    customer_id VARCHAR(50) PRIMARY KEY,
    gender VARCHAR(10),
    SeniorCitizen INT,
    Age INT,
    Married VARCHAR(10),
    Number_of_Dependents INT
);
INSERT INTO Dim_Customer
SELECT DISTINCT
    customer_id,
    gender,
    SeniorCitizen,
    Age,
    Married,
    Number_of_Dependents
FROM telecom_merged;

SELECT * FROM Dim_Customer;