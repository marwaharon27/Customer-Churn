# Telecom Customer Churn SQL Project

## Project Description

This project analyzes telecom customer churn data using MySQL.  
It includes data cleaning, merging, dimensional modeling, fact table creation, churn analysis, revenue analysis, service analysis, demographic analysis, and statistical analysis.

## Database Name

final_project

## Main Tables

- customerchurn_raw
- telecom_customer_churn_raw
- Churn
- telecom_customer_churn
- telecom_merged
- Dim_City
- Dim_Contract
- Dim_Services
- Dim_Churn
- Dim_Customer
- Fact_Telecom_Company

## SQL Files

1. DATABASE CREATION.sql  
   Creates and selects the database.

2. DATA CLEANING.sql  
   Renames raw tables, cleans both datasets, and creates the merged telecom table.

3. DIM_TABLES.sql  
   Creates dimension tables for city, contract, services, churn, and customer.

4. FACT_TABLE.sql  
   Creates the main fact table and defines foreign key relationships.

5. Churn Analysis.sql  
   Contains churn-related analysis queries.

6. Company Overview.sql  
   Contains company-level KPIs and revenue analysis.

7. Demographics.sql  
   Contains customer demographic analysis.

8. Services Analysis.sql  
   Contains service-related analysis queries.

9. Statistical Analysis.sql  
   Contains descriptive statistics, correlations, chi-square preparation, t-test, and ANOVA queries.

## How to Run

Run the SQL files in this order:

1. DATABASE CREATION.sql
2. DATA CLEANING.sql
3. DIM_TABLES.sql
4. FACT_TABLE.sql
5. Analysis files as needed
