"""
===============================================================================
SAMSUNG DATA ENGINEERING PROJECT
DDL Script: Create Bronze Tables
===============================================================================
Script Purpose:
    This script creates tables in the 'bronze' schema, dropping existing tables 
    if they already exist.
	Run this script to re-define the DDL structure of 'bronze' Tables

Author       : Harsh Belekar
Project      : Samsung Data Engineering 
Pipeline     : Raw → Bronze → Silver → Gold
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
LOG_FILE = "DDL_Bronze.log"

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
# TABLE CREATION QUERIES
# =====================================================================

# ----------------------------------
# Source: After-Sales Service (AS2)  
# ----------------------------------
CREATE_COMPLAINTS_TABLE = """
CREATE TABLE bronze.as2_complaints (
    complaint_id     TEXT,
    customer_id      TEXT,
    product_id       TEXT,
    center_id        TEXT,
    complaint_date   TEXT,
    issue_type       TEXT,
    priority         TEXT,
    status           TEXT,
    resolution_date  TEXT,
    resolution_days  TEXT,
    csat_score       TEXT,
    technician_id    TEXT
);
"""

CREATE_RETURNS_TABLE = """
CREATE TABLE bronze.as2_returns (
    return_id       TEXT,
    txn_id          TEXT,
    customer_id     TEXT,
    product_id      TEXT,
    return_date     TEXT,
    return_reason   TEXT,
    condition       TEXT,
    refund_amount   TEXT,
    refund_mode     TEXT,
    is_replacement  TEXT,
    processed_by    TEXT
);
"""

CREATE_SERVICE_CENTERS_TABLE = """
CREATE TABLE bronze.as2_service_centers (
    center_id         TEXT,   
    center_name       TEXT,  
    tier              TEXT,   
    city              TEXT,
    state             TEXT,  
    pincode           TEXT,   
    phone             TEXT, 
    email             TEXT,
    working_hours     TEXT, 
    capacity_per_day  TEXT, 
    is_active         TEXT
);
"""

# -------------------------------
# Source: Customers (CRM)   
# -------------------------------
CREATE_CUSTOMERS_TABLE = """
CREATE TABLE bronze.crm_customers (
    customer_id    TEXT,   
    full_name      TEXT,   
    email          TEXT,   
    phone          TEXT,   
    city           TEXT,
    state          TEXT,
    pincode        TEXT,  
    gender         TEXT,   
    dob            TEXT,   
    segment        TEXT,   
    registered_on  TEXT,   
    is_active      TEXT
);
"""

CREATE_PRODUCT_REVIEWS_TABLE = """
CREATE TABLE bronze.crm_product_reviews (
    review_id          TEXT,
    customer_id        TEXT,   
    product_id         TEXT,   
    rating             TEXT,   
    review_text        TEXT,   
    review_date        TEXT,   
    verified_purchase  TEXT,   
    helpful_votes      TEXT
);
"""

# ---------------------------------
# Source: Finance & Payments (FIP)  
# ---------------------------------
CREATE_FINANCIAL_TRANSACTIONS_TABLE = """
CREATE TABLE bronze.fip_financial_transactions (
    payment_id      TEXT,   
    txn_id          TEXT, 
    payment_date    TEXT,   
    payment_mode    TEXT,   
    amount_inr      TEXT,   
    gst_pct         TEXT,   
    bank_name       TEXT,   
    emi_months      TEXT,   
    upi_ref         TEXT,   
    invoice_no      TEXT,   
    payment_status  TEXT
);
"""

# -------------------------------
# Source: HR & Marketing (HRM)  
# -------------------------------
CREATE_CAMPAIGNS_TABLE = """
CREATE TABLE bronze.hrm_campaigns (
    campaign_id      TEXT, 
    campaign_name    TEXT,   
    type             TEXT,   
    start_date       TEXT,   
    end_date         TEXT,   
    budget_inr       TEXT,  
    discount_pct     TEXT,   
    target_region    TEXT,   
    target_segment   TEXT,   
    channel          TEXT,   
    status           TEXT
);
"""

CREATE_EMPLOYEES_TABLE = """
CREATE TABLE bronze.hrm_employees (
    employee_id  TEXT,
    full_name    TEXT,
    department   TEXT,   
    designation  TEXT,   
    location     TEXT,   
    join_date    TEXT,   
    salary_inr   TEXT,  
    manager_id   TEXT,   
    gender       TEXT,   
    pf_number    TEXT, 
    is_active    TEXT
);
"""

CREATE_PRODUCTS_TABLE = """
CREATE TABLE bronze.hrm_products (
    product_id        TEXT,   
    sku               TEXT,   
    product_name      TEXT,   
    category          TEXT,   
    subcategory       TEXT,   
    mrp_inr           TEXT,   
    launch_date_india TEXT,   
    ram_gb            TEXT,   
    storage_gb        TEXT,   
    display_inches    TEXT,   
    bis_certified     TEXT,   
    warranty_years    TEXT,   
    color_variants    TEXT
);
"""

# -------------------------------
# Supply Chain & Inventory (SCI) 
# -------------------------------
CREATE_INVENTORY_TABLE = """
CREATE TABLE bronze.sci_inventory (
    inventory_id    TEXT, 
    product_id      TEXT,   
    warehouse_id    TEXT,   
    qty_available   TEXT,   
    qty_reserved    TEXT,   
    reorder_level   TEXT,   
    last_restocked  TEXT,   
    snapshot_date   TEXT
);
"""

CREATE_SUPPLIERS_TABLE = """
CREATE TABLE bronze.sci_suppliers (
    supplier_id          TEXT, 
    supplier_name        TEXT,   
    country              TEXT,   
    city                 TEXT,
    gstin                TEXT,   
    contact_email        TEXT,
    payment_terms_days   TEXT,   
    category             TEXT,   
    rating               TEXT,   
    is_msme              TEXT,   
    contract_start       TEXT
);
"""

CREATE_WAREHOUSES_TABLE = """
CREATE TABLE bronze.sci_warehouses (
    warehouse_id    TEXT,   
    warehouse_name  TEXT,   
    city            TEXT,
    state           TEXT,   
    pincode         TEXT,   
    capacity_units  TEXT,   
    latitude        TEXT,   
    longitude       TEXT,
    type            TEXT
);
"""

# -------------------------------
# Sales & Distribution (SND) 
# -------------------------------
CREATE_DEALERS_TABLE = """
CREATE TABLE bronze.snd_dealers (
    dealer_id      TEXT,   
    dealer_name    TEXT,   
    store_type     TEXT,   
    chain          TEXT,   
    city           TEXT,
    state          TEXT,
    tier           TEXT,   
    contact_phone  TEXT,
    active_since   TEXT,   
    is_exclusive   TEXT
);
"""

CREATE_SALES_TRANSACTIONS_TABLE = """
CREATE TABLE bronze.snd_sales_transactions (
    txn_id        TEXT, 
    customer_id   TEXT,   
    product_id    TEXT,   
    dealer_id     TEXT,   
    txn_date      TEXT,   
    amount_inr    TEXT,   
    gst_amount    TEXT,   
    payment_mode  TEXT,   
    channel       TEXT,   
    city          TEXT,
    state         TEXT,
    status        TEXT
);
"""

Tables = [
    (CREATE_COMPLAINTS_TABLE, "as2_complaints"),
    (CREATE_RETURNS_TABLE, "as2_returns"),
    (CREATE_SERVICE_CENTERS_TABLE, "as2_service_centers"),
    (CREATE_CUSTOMERS_TABLE, "crm_customers"),
    (CREATE_PRODUCT_REVIEWS_TABLE, "crm_product_reviews"),
    (CREATE_FINANCIAL_TRANSACTIONS_TABLE, "fip_financial_transactions"),
    (CREATE_CAMPAIGNS_TABLE, "hrm_campaigns"),
    (CREATE_EMPLOYEES_TABLE, "hrm_employees"),
    (CREATE_PRODUCTS_TABLE, "hrm_products"),
    (CREATE_INVENTORY_TABLE, "sci_inventory"),
    (CREATE_SUPPLIERS_TABLE, "sci_suppliers"),
    (CREATE_WAREHOUSES_TABLE, "sci_warehouses"),
    (CREATE_DEALERS_TABLE, "snd_dealers"),
    (CREATE_SALES_TRANSACTIONS_TABLE, "snd_sales_transactions")
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
        logging.info(f"Executing: {query_name} Table Query")
        start_time = time.time()
        cursor.execute(query)
        end_time = time.time()
        duration = end_time - start_time
        logging.info(f"{query_name} Created Successfully in ({duration:.2f}s).")
    
    except Exception as e:
        logging.error(f"Failed to Execute {query_name} Query : {str(e)}")
        raise


# =============================
# Create Tables
# =============================
def create_all_tables(conn):
    logging.info("=" * 70)
    logging.info("Starting Bronze Layer Table Creation Process...")
    logging.info("=" * 70)
    cursor = conn.cursor()
    
    success_count = 0
    failed_count = 0
    
    for query, name in Tables:
        try:
            execute_query(cursor, query, name)
            success_count += 1
        except Exception as e:
            failed_count += 1
            logging.error(f"Skipping {name} Table due to error")
        
    cursor.close()
    logging.info("=" * 70)
    logging.info("TABLE CREATION SUMMARY")
    logging.info("=" * 70)
    logging.info(f"Total operations: {len(Tables)}")
    logging.info(f"Successful: {success_count}")
    logging.info(f"Failed: {failed_count}")
    logging.info("=" * 70 + "\n")
    
    if failed_count == 0:
        logging.info("All Tables created successfully!\n")
    else:
        logging.warning(f"{failed_count} operation(s) failed. Check logs above.\n")


# =============================
# Drop Tables
# =============================
def drop_all_tables(conn):
    logging.info("=" * 70)
    logging.info("DROPPING EXISTING TABLES")
    logging.info("=" * 70)
    cursor = conn.cursor()
    
    dropped_count = 0
    
    for query, name in Tables:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS bronze.{name} CASCADE;")
            logging.info(f"Dropped table: {name}")
            dropped_count += 1
        
        except Exception as e:
            logging.warning(f"Table {name} not found (probably doesn't exist yet)")
    
    cursor.close()

    logging.info("=" * 70)
    logging.info(f"Dropped {dropped_count}/{len(Tables)} tables")
    logging.info("=" * 70 + "\n")


# =============================
# Run Script
# =============================
if __name__ == "__main__":
    start_time = time.time()
    
    logging.info("=" * 70)
    logging.info("SAMSUNG WAREHOUSE SETUP - STARTING")
    logging.info("=" * 70)
    
    conn = None
    
    try:
        # Connect to database
        conn = create_connection()
        
        # Drop existing tables
        drop_all_tables(conn)
        
        # Create all tables and indexes
        create_all_tables(conn)
        
        # Success message
        end_time = time.time()
        duration = end_time - start_time
        
        logging.info("=" * 70)
        logging.info("BRONZE LAYER TABLES CREATION COMPLETED SUCCESSFULLY")
        logging.info(f"Total time: {duration:.2f} seconds")
        logging.info("=" * 70 + "\n")
        
        print("\n" + "=" * 70)
        print("All Tables Created Successfully!")
        print(f"Time taken: {duration:.2f} seconds")
        print(f"Check logs: {os.path.join(LOG_DIR, LOG_FILE)}")
        print("=" * 70 + "\n")
    
    except Exception as e:
        logging.error("=" * 70)
        logging.error("BRONZE LAYER TABLES CREATION FAILED")
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
