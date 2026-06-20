"""
===============================================================================
SAMSUNG INDIA — DATA ENGINEERING PROJECT
DDL Script: Create Gold Views
===============================================================================
Script Purpose:
    This script creates views for the Gold layer in the Samsung data warehouse. 
    The Gold layer represents the final dimension and fact tables (Snowflake Schema)

    Each view performs transformations and combines data from the Silver layer 
    to produce a clean, enriched, and business-ready dataset.

Usage:
    - These views can be queried directly for analytics and reporting.
===============================================================================
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
import os 
import time

# ===============================
# Logging Configuration
# ===============================
LOG_DIR = "Logs"
LOG_FILE = "DDL_Gold.log"

# Creates Logs/ folder if it doesn’t exist
os.makedirs(LOG_DIR, exist_ok=True) 

logging.basicConfig(
    filename=os.path.join(LOG_DIR, LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# =============================
# Database Configuration
# =============================
DB_NAME = "Samsung_Data_Warehouse"
DB_USER = "postgres"
DB_PASSWORD = "password" # Replace this with Your Password 
DB_HOST = "localhost"
DB_PORT = "5432"


# =====================================================================
# VIEW CREATION QUERIES
# =====================================================================

PRODUCTS_VIEW = """
SELECT 
    product_id,           
    sku,                 
    product_name,      
    category,           
    subcategory,       
    mrp_inr,           
    launch_date_india, 
    ram_gb,            
    storage_gb,        
    display_inches,    
    bis_certified,     
    warranty_years,    
    color_variants
FROM silver.hrm_products;"""

WAREHOUSES_VIEW = """
CREATE VIEW gold.dim_warehouses AS
SELECT 
    warehouse_id,   
    warehouse_name,   
    city,
    state,   
    pincode,   
    capacity_units,   
    latitude,   
    longitude,
    type
FROM silver.sci_warehouses;"""

SERVICE_CENTERS_VIEW = """
CREATE VIEW gold.dim_service_centers AS
SELECT 
    center_id,
    center_name,
    tier,              
    city,             
    state,
    pincode,
    phone,
    email,             
    working_hours,     
    capacity_per_day, 
    is_active
FROM silver.as2_service_centers;"""

CUSTOMERS_VIEW = """
CREATE VIEW gold.dim_customers AS
SELECT 
    customer_id,
    full_name,
    email,
    phone,
    city,
    state,
    pincode,
    gender,
    dob,
    segment,
    registered_on,
    is_active
FROM silver.crm_customers;"""

DEALERS_VIEW = """
CREATE VIEW gold.dim_dealers AS
SELECT 
    dealer_id,
    dealer_name,
    store_type,
    chain,
    city,
    state,
    tier,
    contact_phone,
    active_since,
    is_exclusive
FROM silver.snd_dealers;"""

SUPPLIERS_VIEW = """
CREATE VIEW gold.dim_suppliers AS
SELECT 
    supplier_id,
    supplier_name,
    country,
    city,
    gstin,
    contact_email,
    payment_terms_days,
    category,
    rating,
    is_msme,
    contract_start
FROM silver.sci_suppliers;"""

CAMPAIGNS_VIEW = """
CREATE VIEW gold.dim_campaigns AS
SELECT 
    campaign_id,
    campaign_name,
    type,
    start_date,
    end_date,
    budget_inr,
    discount_pct,
    target_region,
    target_segment,
    channel,
    status
FROM silver.hrm_campaigns;"""

EMPLOYEES_VIEW = """
CREATE VIEW gold.dim_employees AS
SELECT 
    employee_id,
    full_name,
    department,
    designation,
    location,
    join_date,
    salary_inr,
    manager_id,
    gender,
    pf_number,
    is_active
FROM silver.hrm_employees;"""

INVENTORY_VIEW = """
CREATE VIEW gold.fact_inventory AS
SELECT 
    inventory_id,
    product_id,
    warehouse_id,
    qty_available,  
    qty_reserved,
    reorder_level,
    last_restocked,
    snapshot_date
FROM silver.sci_inventory;"""

SALES_TRANSACTIONS_VIEW = """
CREATE VIEW gold.fact_sales_transactions AS
SELECT 
    txn_id,
    customer_id,
    product_id,
    dealer_id,
    txn_date,
    amount_inr,
    gst_amount,
    payment_mode,
    channel,
    city,
    state,
    status
FROM silver.snd_sales_transactions;"""

COMPLAINTS_VIEW = """
CREATE VIEW gold.fact_complaints AS
SELECT 
    complaint_id,
    customer_id,
    product_id,
    center_id,
    complaint_date,
    issue_type,
    priority,
    status,
    resolution_date,
    resolution_days,
    csat_score,
    technician_id
FROM silver.as2_complaints;"""

RETURNS_VIEW = """
CREATE VIEW gold.fact_returns AS
SELECT 
    return_id,
    txn_id,
    customer_id,
    product_id,
    return_date,
    return_reason,
    condition,
    refund_amount,
    refund_mode,
    is_replacement,
    processed_by
FROM silver.as2_returns;"""

FINANCIAL_TRANSACTIONS_VIEW = """
CREATE VIEW gold.fact_financial_transactions AS
SELECT 
    payment_id,
    txn_id,
    payment_date,
    payment_mode,  
    amount_inr,
    gst_pct,
    bank_name,
    emi_months,
    upi_ref, 
    invoice_no,
    payment_status
FROM silver.fip_financial_transactions;"""

PRODUCT_REVIEWS_VIEW = """
CREATE VIEW gold.fact_product_reviews AS
SELECT 
    review_id,
    customer_id,
    product_id,
    rating,
    review_text,
    review_date,
    verified_purchase,
    helpful_votes
FROM silver.crm_product_reviews;"""

QUERIES = [
    (PRODUCTS_VIEW, "gold.dim_products"),
    (WAREHOUSES_VIEW, "gold.dim_warehouses"),
    (SERVICE_CENTERS_VIEW, "gold.dim_service_centers"),
    (CUSTOMERS_VIEW, "gold.dim_customers"),
    (DEALERS_VIEW, "gold.dim_dealers"),
    (SUPPLIERS_VIEW, "gold.dim_suppliers"),
    (CAMPAIGNS_VIEW, "gold.dim_campaigns"),
    (EMPLOYEES_VIEW, "gold.dim_employees"),
    
    (INVENTORY_VIEW, "gold.fact_inventory"),
    (SALES_TRANSACTIONS_VIEW, "gold.fact_sales_transactions"),
    (COMPLAINTS_VIEW, "gold.fact_complaints"),
    (RETURNS_VIEW, "gold.fact_returns"),
    (FINANCIAL_TRANSACTIONS_VIEW, "gold.fact_financial_transactions"),
    (PRODUCT_REVIEWS_VIEW, "gold.fact_product_reviews"),
]


# =============================
# # Connect to PostgreSQL
# =============================
def create_connection():
    try:
        logging.info("Connecting to PostgreSQL Database...")
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        logging.info("Database connection Established Successfully.\n")
        return conn
    
    except Exception as e:
        # Show Logs error details & Stops execution if DB fails
        logging.error(f"Database Connection Failed: {e}\n") 
        raise


# =============================
# Execute Query
# =============================    
def execute_query(cursor,query, query_name):
    try:
        logging.info(f"Executing: {query_name} View Query")
        start_time = time.time()
        cursor.execute(query)
        end_time = time.time()
        duration = end_time - start_time
        logging.info(f"{query_name} View Created Successfully in ({duration:.2f}s).")
    
    except Exception as e:
        logging.error(f"Failed to Execute {query_name} Query : {str(e)}")
        raise


# =============================
# Drop Views
# =============================
def drop_viwes(conn):
    logging.info("=" * 70)
    logging.info("DROPPING EXISTING VIEWS")
    logging.info("=" * 70)
    cursor = conn.cursor()
    
    dropped_count = 0
    
    for query, name in QUERIES:
        try:
            cursor.execute(f"DROP VIEW IF EXISTS {name} CASCADE;")
            logging.info(f"Dropped View: {name}")
            dropped_count += 1
        
        except Exception as e:
            logging.warning(f"View {name} not found (probably doesn't exist yet)")
    
    cursor.close()

    logging.info("=" * 70)
    logging.info(f"Dropped {dropped_count}/{len(QUERIES)} Views")
    logging.info("=" * 70 + "\n")


# ======================================================
# Create Views
# ======================================================
def create_views(conn):
    logging.info("=" * 70)
    logging.info("Starting Gold Layer Views Creation Process...")
    logging.info("=" * 70)
    cursor = conn.cursor()
    
    success_count = 0
    failed_count = 0
    
    for query, name in QUERIES:
        try:
            execute_query(cursor, query, name)
            success_count += 1
        except Exception as e:
            failed_count += 1
            logging.error(f"Skipping {name} View due to error")
        
    cursor.close()
    logging.info("=" * 70)
    logging.info("VIEWS CREATION SUMMARY")
    logging.info("=" * 70)
    logging.info(f"Total operations: {len(QUERIES)}")
    logging.info(f"Successful: {success_count}")
    logging.info(f"Failed: {failed_count}")
    logging.info("=" * 70 + "\n")
    
    if failed_count == 0:
        logging.info("All Views Created successfully!\n")
    else:
        logging.warning(f"{failed_count} operation(s) failed. Check logs above.\n")


# =============================
# Run Script
# =============================
if __name__ == "__main__":
    start_time = time.time()
    
    logging.info("=" * 70)
    logging.info("GOLD LAYER VIEWS CREATION - STARTING")
    logging.info("=" * 70)
    
    conn = None
    
    try:
        # Connect to database
        conn = create_connection()
        
        # Truncate existing tables
        drop_viwes(conn)
        
        # Insert Bronze Layer Data into Silver Layer Tables
        create_views(conn)
        
        # Success message
        end_time = time.time()
        duration = end_time - start_time
        
        logging.info("=" * 70)
        logging.info("GOLD LAYER VIEWS CREATION COMPLETED SUCCESSFULLY")
        logging.info(f"Total time: {duration:.2f} seconds")
        logging.info("=" * 70 + "\n")
        
        print("\n" + "=" * 70)
        print("All Views Created Successfully!")
        print(f"Time taken: {duration:.2f} seconds")
        print(f"Check logs: {os.path.join(LOG_DIR, LOG_FILE)}")
        print("=" * 70 + "\n")
    
    except Exception as e:
        logging.error("=" * 70)
        logging.error("GOLD LAYER VIEWS CREATION FAILED")
        logging.error(f"Error: {str(e)}")
        logging.error("=" * 70 + "\n")
        
        print("\n" + "=" * 70)
        print("ERROR: Database setup failed!")
        print(f"Check logs for details: {os.path.join(LOG_DIR, LOG_FILE)}")
        print("=" * 70 + "\n")
    
    finally:
        # Always close connection
        if conn:
            conn.close()
            logging.info("Database connection closed.")
