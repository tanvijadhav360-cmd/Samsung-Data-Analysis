"""
===============================================================================
SAMSUNG DATA ENGINEERING PROJECT
DDL Script: Create Silver Tables
===============================================================================
Script Purpose:
    This script creates tables in the 'silver' schema, dropping existing tables 
    if they already exist.
	Run this script to re-define the DDL structure of 'bronze' Tables
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
LOG_FILE = "DDL_Silver.log"

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

CREATE_COMPLAINTS_TABLE = """
CREATE TABLE silver.as2_complaints (
    complaint_id     VARCHAR(50),
    customer_id      VARCHAR(50),
    product_id       VARCHAR(50),
    center_id        VARCHAR(50),
    complaint_date   DATE,
    issue_type       VARCHAR(50),
    priority         VARCHAR(50),
    status           VARCHAR(50),
    resolution_date  DATE,
    resolution_days  SMALLINT,
    csat_score       SMALLINT,
    technician_id    VARCHAR(50)
);
"""

CREATE_RETURNS_TABLE = """
CREATE TABLE silver.as2_returns (
    return_id       VARCHAR(50),
    txn_id          VARCHAR(50),
    customer_id     VARCHAR(50),
    product_id      VARCHAR(50),
    return_date     DATE,
    return_reason   TEXT,
    condition       VARCHAR(50),
    refund_amount   NUMERIC(10, 2),
    refund_mode     VARCHAR(50),
    is_replacement  BOOLEAN,
    processed_by    VARCHAR(50)
);
"""

CREATE_SERVICE_CENTERS_TABLE = """
CREATE TABLE silver.as2_service_centers (
    center_id         VARCHAR(50),   
    center_name       TEXT,  
    tier              VARCHAR(50),   
    city              VARCHAR(50),
    state             VARCHAR(50),  
    pincode           INT,   
    phone             BIGINT, 
    email             TEXT,
    working_hours     VARCHAR(50), 
    capacity_per_day  SMALLINT, 
    is_active         VARCHAR(50)
);
"""

CREATE_CUSTOMERS_TABLE = """
CREATE TABLE silver.crm_customers (
    customer_id    VARCHAR(50),   
    full_name      TEXT,   
    email          TEXT,   
    phone          BIGINT,   
    city           VARCHAR(50),
    state          VARCHAR(50),
    pincode        INT,  
    gender         VARCHAR(50),   
    dob            DATE,   
    segment        VARCHAR(50),   
    registered_on  DATE,   
    is_active      BOOLEAN
);
"""

CREATE_PRODUCT_REVIEWS_TABLE = """
CREATE TABLE silver.crm_product_reviews (
    review_id          VARCHAR(50),
    customer_id        VARCHAR(50),   
    product_id         VARCHAR(50),   
    rating             SMALLINT,   
    review_text        TEXT,   
    review_date        DATE,   
    verified_purchase  BOOLEAN,   
    helpful_votes      INT
);
"""

CREATE_FINANCIAL_TRANSACTIONS_TABLE = """
CREATE TABLE silver.fip_financial_transactions (
    payment_id      VARCHAR(50),   
    txn_id          VARCHAR(50), 
    payment_date    DATE,   
    payment_mode    VARCHAR(50),   
    amount_inr      NUMERIC(12, 2),   
    gst_pct         SMALLINT,   
    bank_name       VARCHAR(50),   
    emi_months      SMALLINT,   
    upi_ref         TEXT,   
    invoice_no      TEXT,   
    payment_status  VARCHAR(50)
);
"""

CREATE_CAMPAIGNS_TABLE = """
CREATE TABLE silver.hrm_campaigns (
    campaign_id      VARCHAR(50), 
    campaign_name    TEXT,   
    type             VARCHAR(50),   
    start_date       DATE,   
    end_date         DATE,   
    budget_inr       NUMERIC(12, 2),  
    discount_pct     NUMERIC(4, 1),   
    target_region    VARCHAR(50),   
    target_segment   VARCHAR(50),   
    channel          VARCHAR(50),   
    status           VARCHAR(50)
);
"""

CREATE_EMPLOYEES_TABLE = """
CREATE TABLE silver.hrm_employees (
    employee_id  VARCHAR(50),
    full_name    VARCHAR(50),
    department   VARCHAR(50),   
    designation  VARCHAR(50),   
    location     TEXT,   
    join_date    DATE,   
    salary_inr   NUMERIC(12, 2),  
    manager_id   VARCHAR(50),   
    gender       VARCHAR(50),   
    pf_number    TEXT, 
    is_active    BOOLEAN
);
"""

CREATE_PRODUCTS_TABLE = """
CREATE TABLE silver.hrm_products (
    product_id        VARCHAR(50),   
    sku               VARCHAR(50),   
    product_name      TEXT,   
    category          VARCHAR(50),   
    subcategory       TEXT,   
    mrp_inr           NUMERIC(10, 2),   
    launch_date_india DATE,   
    ram_gb            SMALLINT,   
    storage_gb        SMALLINT,   
    display_inches    NUMERIC(4, 1),   
    bis_certified     BOOLEAN,   
    warranty_years    SMALLINT,   
    color_variants    SMALLINT
);
"""

CREATE_INVENTORY_TABLE = """
CREATE TABLE silver.sci_inventory (
    inventory_id    VARCHAR(50), 
    product_id      VARCHAR(50),   
    warehouse_id    VARCHAR(50),   
    qty_available   INT,   
    qty_reserved    INT,   
    reorder_level   INT,   
    last_restocked  DATE,   
    snapshot_date   DATE
);
"""

CREATE_SUPPLIERS_TABLE = """
CREATE TABLE silver.sci_suppliers (
    supplier_id          VARCHAR(50), 
    supplier_name        TEXT,   
    country              VARCHAR(50),   
    city                 VARCHAR(50),
    gstin                TEXT,   
    contact_email        TEXT,
    payment_terms_days   SMALLINT,   
    category             VARCHAR(50),   
    rating               NUMERIC(3, 1),   
    is_msme              BOOLEAN,   
    contract_start       DATE
);
"""

CREATE_WAREHOUSES_TABLE = """
CREATE TABLE silver.sci_warehouses (
    warehouse_id    VARCHAR(50),   
    warehouse_name  TEXT,   
    city            VARCHAR(50),
    state           VARCHAR(50),   
    pincode         INT,   
    capacity_units  INT,   
    latitude        NUMERIC(9, 6),   
    longitude       NUMERIC(9, 6),
    type            VARCHAR(50)
);
"""

CREATE_DEALERS_TABLE = """
CREATE TABLE silver.snd_dealers (
    dealer_id      VARCHAR(50),   
    dealer_name    TEXT,   
    store_type     TEXT,   
    chain          VARCHAR(50),   
    city           VARCHAR(50),
    state          VARCHAR(50),
    tier           VARCHAR(50),   
    contact_phone  BIGINT,
    active_since   VARCHAR(50),   
    is_exclusive   BOOLEAN
);
"""

CREATE_SALES_TRANSACTIONS_TABLE = """
CREATE TABLE silver.snd_sales_transactions (
    txn_id        VARCHAR(50), 
    customer_id   VARCHAR(50),   
    product_id    VARCHAR(50),   
    dealer_id     VARCHAR(50),   
    txn_date      DATE,   
    amount_inr    NUMERIC(12, 2),   
    gst_amount    NUMERIC(12, 2),   
    payment_mode  VARCHAR(50),   
    channel       VARCHAR(50),   
    city          VARCHAR(50),
    state         VARCHAR(50),
    status        VARCHAR(50)
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
    logging.info("Starting Silver Layer Table Creation Process...")
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
            cursor.execute(f"DROP TABLE IF EXISTS silver.{name} CASCADE;")
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
        logging.info("SILVER LAYER TABLES CREATION COMPLETED SUCCESSFULLY")
        logging.info(f"Total time: {duration:.2f} seconds")
        logging.info("=" * 70 + "\n")
        
        print("\n" + "=" * 70)
        print("All Tables Created Successfully!")
        print(f"Time taken: {duration:.2f} seconds")
        print(f"Check logs: {os.path.join(LOG_DIR, LOG_FILE)}")
        print("=" * 70 + "\n")
    
    except Exception as e:
        logging.error("=" * 70)
        logging.error("SILVER LAYER TABLES CREATION FAILED")
        logging.error(f"Error: {str(e)}")
        logging.error("=" * 70 + "\n")
        
        print("\n" + "=" * 70)
        print("ERROR: WAREHOUSE setup failed!")
        print(f"Check logs for details: {os.path.join(LOG_DIR, LOG_FILE)}")
        print("=" * 70 + "\n")
    
    finally:
        # Always close connection
        if conn:
            conn.close()
            logging.info("Database connection closed.")
