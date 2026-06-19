"""
===============================================================================
SAMSUNG INDIA — DATA ENGINEERING PROJECT
Insertion Script: Load Silver Layer (Bronze -> Silver)
===============================================================================
Script Purpose:
    This stored procedure performs the ETL (Extract, Transform, Load) process to 
    populate the 'silver' schema tables from the 'bronze' schema.
	Actions Performed:
		- Truncates Silver tables.
		- Inserts transformed and cleansed data from Bronze into Silver tables.

Database:
    PostgreSQL

Parameters:
    None. 
		This Script does not accept any parameters or return any values.
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
LOG_FILE = "Load_Silver.log"

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
# Cleaning & Insertion QUERIES
# =====================================================================

COMPLAINTS_TABLE = """
INSERT INTO silver.as2_complaints
	(
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
	)
    SELECT
        TRIM(complaint_id) AS complaint_id,
        TRIM(customer_id) AS customer_id,
        TRIM(product_id) AS product_id,
        TRIM(center_id) AS center_id,
        cleaning.fn_parse_date(complaint_date) AS complaint_date,
        TRIM(issue_type) AS issue_type,
        CASE
            WHEN TRIM(LOWER(priority)) IN ('urgent', 'p1') THEN 'Urgent'
            WHEN TRIM(LOWER(priority)) IN ('high')         THEN 'High'
            WHEN TRIM(LOWER(priority)) IN ('medium', 'p2') THEN 'Medium'
            WHEN TRIM(LOWER(priority)) IN ('low', 'p3')    THEN 'Low'
            ELSE NULL
        END AS priority,
        TRIM(status) AS status,
        cleaning.fn_parse_date(resolution_date) AS resolution_date,
        CASE
            WHEN TRIM(resolution_days) ~ '^[0-9]+$' AND TRIM(resolution_days)::INTEGER >= 0
                THEN TRIM(resolution_days)::SMALLINT
            ELSE NULL
        END AS resolution_days,
        CASE
            WHEN TRIM(csat_score) ~ '^[1-5]$'
                THEN TRIM(csat_score)::SMALLINT
            ELSE NULL
        END AS csat_score,
        TRIM(technician_id) AS technician_id
    FROM bronze.as2_complaints
    WHERE TRIM(complaint_id) IS NOT NULL
    ORDER BY complaint_id ASC;"""

RETURNS_TABLE = """
INSERT INTO silver.as2_returns
	(
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
	)
    SELECT
        TRIM(return_id) AS return_id,
        TRIM(txn_id) AS txn_id,
        TRIM(customer_id) AS customer_id,
        TRIM(product_id) AS product_id,
        cleaning.fn_parse_date(return_date) AS return_date,
        CASE
            WHEN TRIM(LOWER(return_reason)) IN ('n/a', '?', 'other', '')
                OR return_reason IS NULL
            THEN NULL
            ELSE TRIM(return_reason)
        END AS return_reason,
        CASE
            WHEN TRIM(LOWER(condition)) = 'good'    THEN 'Good'
            WHEN TRIM(LOWER(condition)) = 'fair'    THEN 'Fair'
            WHEN TRIM(LOWER(condition)) = 'damaged' THEN 'Damaged'
            WHEN TRIM(LOWER(condition)) = 'opened'  THEN 'Opened'
            WHEN TRIM(LOWER(condition)) = 'sealed'  THEN 'Sealed'
            ELSE NULL
        END AS condition,
        CASE
            WHEN TRIM(refund_amount) ~ '^[0-9]+(\.[0-9]+)?$'
            AND TRIM(refund_amount)::NUMERIC >= 0
            THEN TRIM(refund_amount)::NUMERIC(10,2)
            ELSE NULL
        END AS refund_amount,
        CASE
            WHEN TRIM(LOWER(refund_mode)) = 'bank transfer'         THEN 'Bank Transfer'
            WHEN TRIM(LOWER(refund_mode)) = 'neft'                  THEN 'Bank Transfer'
            WHEN TRIM(LOWER(refund_mode)) = 'wallet credit'         THEN 'Wallet Credit'
            WHEN TRIM(LOWER(refund_mode)) = 'gift card'             THEN 'Gift Card'
            WHEN TRIM(LOWER(refund_mode)) = 'upi'                   THEN 'UPI'
            WHEN TRIM(LOWER(refund_mode)) = 'original payment mode' THEN 'Original Payment Mode'
            ELSE TRIM(refund_mode)
        END AS refund_mode,
        cleaning.fn_to_boolean(is_replacement) AS is_replacement,
        TRIM(processed_by) AS processed_by
    FROM bronze.as2_returns
    WHERE TRIM(return_id) IS NOT NULL
    ORDER BY return_id ASC;"""

SERVICE_CENTERS_TABLE = """
INSERT INTO silver.as2_service_centers
	(
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
	)
    SELECT
        TRIM(center_id) AS center_id,
        TRIM(center_name) AS center_name,
        CASE
            WHEN TRIM(LOWER(tier)) IN ('premium')    THEN 'Premium'
            WHEN TRIM(LOWER(tier)) IN ('standard')   THEN 'Standard'
            WHEN TRIM(LOWER(tier)) IN ('brand shop') THEN 'Brand Shop'
            ELSE NULL
        END AS tier,
        INITCAP(LOWER(TRIM(city))) AS city,
        INITCAP(LOWER(TRIM(state))) AS state,
        CASE
            WHEN TRIM(pincode) ~ '^[0-9]{6}$' THEN TRIM(pincode)
            ELSE NULL
        END ::INTEGER AS pincode,
        cleaning.fn_clean_phone(phone) ::BIGINT AS phone,
        CASE
            WHEN TRIM(email) LIKE '%@%.%' THEN LOWER(TRIM(email))
            ELSE NULL
        END AS email,
        CASE
            WHEN TRIM(working_hours) = '10:00-18:00'          THEN '10:00 AM - 6:00 PM'
            WHEN TRIM(working_hours) = '9AM-7PM'              THEN '9:00 AM - 7:00 PM'
            WHEN TRIM(working_hours) = '9:00 AM - 6:00 PM'    THEN '9:00 AM - 6:00 PM'
            WHEN TRIM(working_hours) = 'Monday-Saturday 10-7' THEN '10:00 AM - 7:00 PM'
            ELSE NULL
        END AS working_hours,
        CASE
            WHEN TRIM(capacity_per_day) ~ '^[0-9]+$'
            AND TRIM(capacity_per_day)::INTEGER > 0
            THEN TRIM(capacity_per_day)::SMALLINT
            ELSE NULL
        END AS capacity_per_day,
        cleaning.fn_to_boolean(is_active) AS is_active
    FROM bronze.as2_service_centers
    WHERE TRIM(center_id) IS NOT NULL
    ORDER BY center_id ASC;"""

CUSTOMERS_TABLE = """
INSERT INTO silver.crm_customers
	(
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
	)
    WITH deduped_emails AS (
        SELECT
            customer_id,
            email,
            ROW_NUMBER() OVER (
                PARTITION BY LOWER(TRIM(email))
                ORDER BY registered_on
            ) AS email_rank
        FROM bronze.crm_customers
        WHERE email IS NOT NULL
    )
    SELECT
        TRIM(c.customer_id) AS customer_id,
        INITCAP(LOWER(TRIM(c.full_name))) AS full_name,
        CASE
            WHEN de.email_rank = 1 THEN LOWER(TRIM(c.email))
            ELSE NULL 
        END AS email,
        cleaning.fn_clean_phone(c.phone) ::BIGINT AS phone,
        INITCAP(LOWER(TRIM(c.city))) AS city,
        INITCAP(LOWER(TRIM(c.state))) AS state,
        CASE
            WHEN TRIM(c.pincode) ~ '^[0-9]{6}$' THEN TRIM(c.pincode)
            ELSE NULL
        END ::INTEGER AS pincode,
        CASE
            WHEN TRIM(LOWER(c.gender)) IN ('male',   'm')  THEN 'Male'
            WHEN TRIM(LOWER(c.gender)) IN ('female', 'f')  THEN 'Female'
            WHEN TRIM(LOWER(c.gender)) = 'other'           THEN 'Other'
            ELSE NULL
        END AS gender,
        cleaning.fn_parse_date(c.dob) AS dob,
        INITCAP(LOWER(TRIM(c.segment))) AS segment,
        cleaning.fn_parse_date(c.registered_on) AS registered_on,
        COALESCE(cleaning.fn_to_boolean(c.is_active), TRUE) AS is_active
    FROM bronze.crm_customers c
    LEFT JOIN deduped_emails de
        ON LOWER(TRIM(c.email)) = LOWER(TRIM(de.email))
    AND c.customer_id = de.customer_id
    WHERE TRIM(c.customer_id) IS NOT NULL
    AND TRIM(c.customer_id) != ''
    ORDER BY c.customer_id ASC;"""

PRODUCT_REVIEWS_TABLE = """
INSERT INTO silver.crm_product_reviews
	(
		review_id,
        customer_id,
        product_id,
        rating,
        review_text,
		review_date,
        verified_purchase,
        helpful_votes
	)
    SELECT
        TRIM(review_id) AS review_id,
        TRIM(customer_id) AS customer_id,
        TRIM(product_id) AS product_id,
        CASE
            WHEN TRIM(rating) ~ '^[1-5]$'
            THEN TRIM(rating)::SMALLINT
            ELSE NULL
        END AS rating,
        TRIM(review_text) AS review_text,
        cleaning.fn_parse_date(review_date) AS review_date,
        cleaning.fn_to_boolean(verified_purchase) AS verified_purchase,
        CASE
            WHEN TRIM(helpful_votes) ~ '^[0-9]+$'
            THEN TRIM(helpful_votes)::SMALLINT
            ELSE 0
        END AS helpful_votes
    FROM bronze.crm_product_reviews
    WHERE TRIM(review_id) IS NOT NULL
    AND TRIM(review_id) != ''
    ORDER BY review_id ASC;"""

FINANCIAL_TRANSACTIONS_TABLE = """
INSERT INTO silver.fip_financial_transactions
	(
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
	)
    SELECT
        TRIM(payment_id) AS payment_id,
        TRIM(txn_id) AS txn_id,
        cleaning.fn_parse_date(payment_date) AS payment_date,
        CASE
            WHEN TRIM(LOWER(payment_mode)) = 'upi'                        THEN 'UPI'
            WHEN TRIM(LOWER(payment_mode)) IN ('credit card', 'credit')   THEN 'Credit Card'
            WHEN TRIM(LOWER(payment_mode)) IN ('debit card',  'debit')    THEN 'Debit Card'
            WHEN TRIM(LOWER(payment_mode)) = 'net banking'                THEN 'Net Banking'
            WHEN TRIM(LOWER(payment_mode)) = 'emi'                        THEN 'EMI'
            WHEN TRIM(LOWER(payment_mode)) IN ('cash on delivery', 'cod') THEN 'Cash on Delivery'
            WHEN TRIM(LOWER(payment_mode)) = 'wallet'                     THEN 'Wallet'
            ELSE NULL
        END AS payment_mode,
        CASE
            WHEN TRIM(amount_inr) ~ '^[0-9]+(\.[0-9]+)?$'
            AND TRIM(amount_inr)::NUMERIC > 0
            THEN TRIM(amount_inr)::NUMERIC(12,2)
            ELSE NULL
        END AS amount_inr,
        cleaning.fn_parse_gst_pct(gst_pct):: SMALLINT AS gst_pct,
        TRIM(bank_name) AS bank_name,
        CASE
            WHEN TRIM(LOWER(payment_mode)) = 'emi'
            AND TRIM(emi_months) ~ '^[0-9]+$'
            THEN TRIM(emi_months)::SMALLINT
            ELSE NULL
        END AS emi_months,
        CASE
            WHEN TRIM(LOWER(payment_mode)) = 'upi'
            AND TRIM(upi_ref) IS NOT NULL
            AND TRIM(upi_ref) != ''
            THEN TRIM(upi_ref)
            ELSE NULL
        END AS upi_ref,
        TRIM(invoice_no) AS invoice_no,
        CASE
            WHEN TRIM(LOWER(payment_status)) = 'success'   THEN 'Success'
            WHEN TRIM(LOWER(payment_status)) = 'failed'    THEN 'Failed'
            WHEN TRIM(LOWER(payment_status)) = 'pending'   THEN 'Pending'
            WHEN TRIM(LOWER(payment_status)) = 'refunded'  THEN 'Refunded'
            WHEN TRIM(LOWER(payment_status)) = 'disputed'  THEN 'Disputed'
            ELSE NULL
        END AS payment_status
    FROM bronze.fip_financial_transactions
    ORDER BY payment_id ASC;"""

CAMPAIGNS_TABLE = """
INSERT INTO silver.hrm_campaigns
	(
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
	)
    SELECT
        TRIM(campaign_id) AS campaign_id,
        TRIM(campaign_name) AS campaign_name,
        INITCAP(LOWER(TRIM(type))) AS type,
        cleaning.fn_parse_date(start_date) AS start_date,
        cleaning.fn_parse_date(end_date) AS end_date,
        CASE
            WHEN TRIM(budget_inr) ~ '^[0-9]+(\.[0-9]+)?$'
            AND TRIM(budget_inr)::NUMERIC > 0
            THEN TRIM(budget_inr)::NUMERIC(12,2)
            ELSE NULL
        END AS budget_inr,
        CASE
            WHEN REGEXP_REPLACE(discount_pct, '[^0-9.]', '', 'g') ~ '^[0-9]+(\.[0-9]+)?$'
            THEN REGEXP_REPLACE(discount_pct, '[^0-9.]', '', 'g')::NUMERIC(4,1)
            ELSE NULL
        END AS discount_pct,
        TRIM(target_region) AS target_region,
        INITCAP(LOWER(TRIM(target_segment))) AS target_segment,
        TRIM(channel) AS channel,
        CASE
            WHEN TRIM(LOWER(status)) = 'active'     THEN 'Active'
            WHEN TRIM(LOWER(status)) = 'completed'  THEN 'Completed'
            WHEN TRIM(LOWER(status)) = 'paused'     THEN 'Paused'
            WHEN TRIM(LOWER(status)) = 'draft'      THEN 'Draft'
            WHEN TRIM(LOWER(status)) = 'cancelled'  THEN 'Cancelled'
            ELSE NULL
        END AS status
    FROM bronze.hrm_campaigns
    WHERE TRIM(campaign_id) IS NOT NULL
    ORDER BY campaign_id ASC;"""

EMPLOYEES_TABLE = """
INSERT INTO silver.hrm_employees
	(
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
	)
    SELECT
        TRIM(employee_id) AS employee_id,
        INITCAP(LOWER(TRIM(full_name))) AS full_name,
        INITCAP(LOWER(TRIM(department))) AS department,
        TRIM(designation) AS designation,
        TRIM(location) AS location,
        cleaning.fn_parse_date(join_date) AS join_date,
        cleaning.fn_salary_to_annual(salary_inr) :: NUMERIC(12, 2) AS annual_salary_inr,
        CASE
            WHEN TRIM(manager_id) IS NOT NULL
            AND TRIM(manager_id) != TRIM(employee_id)
            THEN TRIM(manager_id)
            ELSE NULL
        END AS manager_id,
        CASE
            WHEN TRIM(LOWER(gender)) IN ('male',   'm') THEN 'Male'
            WHEN TRIM(LOWER(gender)) IN ('female', 'f') THEN 'Female'
            WHEN TRIM(LOWER(gender)) = 'other'          THEN 'Other'
            ELSE NULL
        END AS gender,
        CASE
            WHEN TRIM(pf_number) ~ '^[A-Z]{2}/[0-9]{5}/[0-9]{3}$'
            THEN TRIM(pf_number)
            ELSE NULL
        END AS pf_number,
        CASE
            WHEN TRIM(LOWER(is_active)) IN ('active',   '1', 'yes', 'true')  THEN TRUE
            WHEN TRIM(LOWER(is_active)) IN ('inactive', '0', 'no',  'false') THEN FALSE
            ELSE TRUE  
        END AS is_active
    FROM bronze.hrm_employees
    WHERE TRIM(employee_id) IS NOT NULL
    ORDER BY employee_id ASC;"""

PRODUCTS_TABLE = """
INSERT INTO silver.hrm_products
	(
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
    )    
    SELECT
        TRIM(product_id) AS product_id,
        TRIM(sku) AS sku,
        TRIM(product_name) AS product_name,
        INITCAP(LOWER(TRIM(category))) AS category,
        TRIM(subcategory) AS subcategory,
        CASE
            WHEN mrp_inr ~ '^[0-9]+(\.[0-9]+)?$'
            AND mrp_inr::NUMERIC > 0  THEN mrp_inr::NUMERIC(10,2)
            ELSE NULL
        END AS mrp_inr,
        cleaning.fn_parse_date(launch_date_india) AS launch_date_india,
        CASE
            WHEN REGEXP_REPLACE(ram_gb, '[^0-9]', '', 'g') ~ '^[0-9]+$'
            THEN REGEXP_REPLACE(ram_gb, '[^0-9]', '', 'g')::SMALLINT
            ELSE NULL
        END AS ram_gb,
        CASE
            WHEN REGEXP_REPLACE(storage_gb, '[^0-9]', '', 'g') ~ '^[0-9]+$'
            THEN REGEXP_REPLACE(storage_gb, '[^0-9]', '', 'g')::SMALLINT
            ELSE NULL
        END AS storage_gb,
        CASE
            WHEN display_inches ~ '^[0-9]+(\.[0-9]+)?$' THEN display_inches::NUMERIC(4,1)
            ELSE NULL
        END AS display_inches,
        cleaning.fn_to_boolean(bis_certified) AS bis_certified,
        CASE
            WHEN warranty_years ~ '^[12]$' THEN warranty_years::SMALLINT
            ELSE NULL
        END AS warranty_years,
        CASE
            WHEN color_variants ~ '^[0-9]+$' THEN color_variants::SMALLINT
            ELSE NULL
        END AS color_variants
    FROM bronze.hrm_products
    WHERE TRIM(product_id) IS NOT NULL
    AND TRIM(product_id) != ''
    ORDER BY product_id ASC;"""

INVENTORY_TABLE = """
INSERT INTO silver.sci_inventory
	(
		inventory_id,
        product_id,
        warehouse_id,
        qty_available,  
        qty_reserved,
        reorder_level,
        last_restocked,
        snapshot_date
	)
    SELECT
        TRIM(inventory_id) AS inventory_id,
        TRIM(product_id) AS product_id,
        TRIM(warehouse_id) AS warehouse_id,
        CASE 
            WHEN TRIM(qty_available) ~ '^-?[0-9]+(\.[0-9]+)?$' 
                THEN GREATEST(TRIM(qty_available)::DECIMAL, 0)
            ELSE 0 
        END :: INTEGER AS qty_available,
        CASE
            WHEN TRIM(qty_reserved) ~ '^[0-9]+$'
            THEN TRIM(qty_reserved)::INTEGER
            ELSE 0
        END AS qty_reserved,
        CASE
            WHEN TRIM(reorder_level) ~ '^[0-9]+$'
            AND TRIM(reorder_level)::INTEGER > 0
            THEN TRIM(reorder_level)::INTEGER
            ELSE NULL
        END AS reorder_level,
        cleaning.fn_parse_date(last_restocked) AS last_restocked,
        cleaning.fn_parse_epoch_or_date(snapshot_date) AS snapshot_date
    FROM bronze.sci_inventory
    WHERE TRIM(inventory_id) IS NOT NULL
    ORDER BY inventory_id ASC;"""

SUPPLIERS_TABLE = """
INSERT INTO silver.sci_suppliers
	(
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
	)
    SELECT
        TRIM(supplier_id) AS supplier_id,
        TRIM(supplier_name) AS supplier_name,
        INITCAP(LOWER(TRIM(country))) AS country,
        INITCAP(LOWER(TRIM(city))) AS city,
        CASE
            WHEN TRIM(gstin) ~ '^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][0-9][A-Z][0-9]$'
            THEN UPPER(TRIM(gstin))
            ELSE NULL
        END AS gstin,
        LOWER(TRIM(contact_email)) AS contact_email,
        CASE
            WHEN TRIM(LOWER(payment_terms_days)) IN ('30', 'net 30', '30 days')  THEN 30
            WHEN TRIM(LOWER(payment_terms_days)) IN ('45', 'net 45', '45 days')  THEN 45
            WHEN TRIM(LOWER(payment_terms_days)) IN ('60', 'net 60', '60 days')  THEN 60
            ELSE NULL
        END :: SMALLINT AS payment_terms_days,
        TRIM(category) AS category,
        CASE
            WHEN rating ~ '^[0-9]+(\.[0-9]+)?$'
            AND rating::NUMERIC BETWEEN 1.0 AND 5.0
            THEN rating::NUMERIC(3,1)
            ELSE NULL
        END AS rating,
        cleaning.fn_to_boolean(is_msme) AS is_msme,
        cleaning.fn_parse_date(contract_start) AS contract_start
    FROM bronze.sci_suppliers
    WHERE TRIM(supplier_id) IS NOT NULL
    ORDER BY supplier_id ASC;"""

WAREHOUSES_TABLE = """
INSERT INTO silver.sci_warehouses
	(
		warehouse_id,   
        warehouse_name,   
        city,
        state,   
        pincode,   
        capacity_units,   
        latitude,   
        longitude,
        type
	)
    SELECT
        TRIM(warehouse_id) AS warehouse_id,
        TRIM(warehouse_name) AS warehouse_name,
        INITCAP(LOWER(TRIM(city))) AS city,
        INITCAP(LOWER(TRIM(state))) AS state,
        CASE
            WHEN TRIM(pincode) ~ '^[0-9]{6}$' THEN TRIM(pincode)
            ELSE NULL
        END :: INTEGER AS pincode,
        CASE
            WHEN TRIM(capacity_units) ~ '^[0-9]+$' THEN TRIM(capacity_units)::INTEGER
            ELSE NULL
        END AS capacity_units,
        CASE
            WHEN TRIM(latitude) IS NOT NULL
            THEN REPLACE(TRIM(latitude), ',', '.')::NUMERIC(9,6)
            ELSE NULL
        END AS latitude,
        CASE
            WHEN TRIM(longitude) ~ '^-?[0-9]+\.[0-9]+$'
            THEN TRIM(longitude)::NUMERIC(9,6)
            ELSE NULL
        END AS longitude,
        INITCAP(LOWER(TRIM(type))) AS type
    FROM bronze.sci_warehouses
    WHERE TRIM(warehouse_id) IS NOT NULL
    ORDER BY warehouse_id ASC;"""

DEALERS_TABLE = """
INSERT INTO silver.snd_dealers
	(
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
	)
    SELECT
        TRIM(dealer_id) AS dealer_id,
        TRIM(dealer_name) AS dealer_name,
        TRIM(store_type) AS store_type,
        TRIM(chain) AS chain,
        INITCAP(LOWER(TRIM(city))) AS city,
        INITCAP(LOWER(TRIM(state))) AS state,
        CASE
            WHEN TRIM(UPPER(REPLACE(tier, ' ', ''))) IN ('TIER1', 'T1') THEN 'Tier 1'
            WHEN TRIM(UPPER(REPLACE(tier, ' ', ''))) IN ('TIER2', 'T2') THEN 'Tier 2'
            WHEN TRIM(UPPER(REPLACE(tier, ' ', ''))) IN ('TIER3', 'T3') THEN 'Tier 3'
            WHEN TRIM(tier) = 'Tier 1'                                  THEN 'Tier 1'
            WHEN TRIM(tier) = 'Tier 2'                                  THEN 'Tier 2'
            WHEN TRIM(tier) = 'Tier 3'                                  THEN 'Tier 3'
            ELSE NULL
        END AS tier,
        cleaning.fn_clean_phone(contact_phone) :: BIGINT AS contact_phone,
        cleaning.fn_parse_date(active_since) AS active_since,
        cleaning.fn_to_boolean(is_exclusive) AS is_exclusive
    FROM bronze.snd_dealers
    WHERE TRIM(dealer_id) IS NOT NULL
    ORDER BY dealer_id ASC;"""

SALES_TRANSACTIONS_TABLE = """
INSERT INTO silver.snd_sales_transactions
	(
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
	)
    WITH cleaned_data AS (
        SELECT
            TRIM(st.txn_id) AS txn_id,
            TRIM(st.customer_id) AS customer_id,
            TRIM(st.product_id) AS product_id,
            TRIM(st.dealer_id) AS dealer_id,
            cleaning.fn_parse_date(st.txn_date) AS txn_date,
            CASE
                WHEN TRIM(UPPER(st.amount_inr)) LIKE 'USD %'
                THEN REGEXP_REPLACE(st.amount_inr, '[^0-9.]', '', 'g')::NUMERIC(12,2)
                WHEN TRIM(st.amount_inr) ~ '^[0-9]+(\.[0-9]+)?$'
                    AND TRIM(st.amount_inr)::NUMERIC > 0
                THEN TRIM(st.amount_inr)::NUMERIC(12,2)
                ELSE 0
            END AS amount_inr,
            CASE
                WHEN TRIM(LOWER(st.payment_mode)) IN ('upi')                          THEN 'UPI'
                WHEN TRIM(LOWER(st.payment_mode)) IN ('credit card', 'credit')        THEN 'Credit Card'
                WHEN TRIM(LOWER(st.payment_mode)) IN ('debit card', 'debit')          THEN 'Debit Card'
                WHEN TRIM(LOWER(st.payment_mode)) IN ('net banking')                  THEN 'Net Banking'
                WHEN TRIM(LOWER(st.payment_mode)) IN ('emi')                          THEN 'EMI'
                WHEN TRIM(LOWER(st.payment_mode)) IN ('cash on delivery', 'cod')      THEN 'Cash on Delivery'
                WHEN TRIM(LOWER(st.payment_mode)) IN ('wallet')                       THEN 'Wallet'
                ELSE 'Other'
            END AS payment_mode,
            TRIM(st.channel) AS channel,
            INITCAP(LOWER(TRIM(st.city))) AS city,
            INITCAP(LOWER(TRIM(st.state))) AS state,
            CASE
                WHEN TRIM(LOWER(st.status)) = 'completed'  THEN 'Completed'
                WHEN TRIM(LOWER(st.status)) = 'pending'    THEN 'Pending'
                WHEN TRIM(LOWER(st.status)) = 'failed'     THEN 'Failed'
                WHEN TRIM(LOWER(st.status)) = 'returned'   THEN 'Returned'
                WHEN TRIM(LOWER(st.status)) = 'cancelled'  THEN 'Cancelled'
                ELSE 'Unknown'
            END AS status
        FROM bronze.snd_sales_transactions st
    ),
    deduplicated_tax AS (
        SELECT 
            TRIM(txn_id) AS txn_id, 
            MAX(gst_pct) AS gst_pct
        FROM silver.fip_financial_transactions
        GROUP BY TRIM(txn_id)
    )
    SELECT 
        cd.txn_id,
        cd.customer_id,
        cd.product_id,
        cd.dealer_id,
        cd.txn_date,
        cd.amount_inr,
        (cd.amount_inr * COALESCE(ft.gst_pct, 18) / 100.0)::NUMERIC(12,2) AS gst_amount,
        cd.payment_mode,
        cd.channel,
        cd.city,
        cd.state,
        cd.status
    FROM cleaned_data cd
    LEFT JOIN deduplicated_tax ft ON cd.txn_id = ft.txn_id
    WHERE cd.txn_id IS NOT NULL
    ORDER BY cd.txn_id ASC;"""

QUERIES = [
    (COMPLAINTS_TABLE, "silver.as2_complaints"),
    (RETURNS_TABLE, "silver.as2_returns"),
    (SERVICE_CENTERS_TABLE, "silver.as2_service_centers"),
    (CUSTOMERS_TABLE, "silver.crm_customers"),
    (PRODUCT_REVIEWS_TABLE, "silver.crm_product_reviews"),
    (FINANCIAL_TRANSACTIONS_TABLE, "silver.fip_financial_transactions"),
    (CAMPAIGNS_TABLE, "silver.hrm_campaigns"),
    (EMPLOYEES_TABLE, "silver.hrm_employees"),
    (PRODUCTS_TABLE, "silver.hrm_products"),
    (INVENTORY_TABLE, "silver.sci_inventory"),
    (SUPPLIERS_TABLE, "silver.sci_suppliers"),
    (WAREHOUSES_TABLE, "silver.sci_warehouses"),
    (DEALERS_TABLE, "silver.snd_dealers"),
    (SALES_TRANSACTIONS_TABLE, "silver.snd_sales_transactions")
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
        logging.info(f"Executing: {query_name} Insertion Query")
        start_time = time.time()
        cursor.execute(query)
        end_time = time.time()
        duration = end_time - start_time
        logging.info(f"{query_name} Table Data Inserted Successfully in ({duration:.2f}s).")
    
    except Exception as e:
        logging.error(f"Failed to Execute {query_name} Query : {str(e)}")
        raise


# =============================
# Truncate Tables
# =============================
def truncate_tables(conn):
    try:
        cursor = conn.cursor()
        
        logging.info("=" * 70)
        logging.info("TRUNCATING TABLES")
        logging.info("=" * 70)

        for query,table_name in QUERIES:
            # Get row count before truncate
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            before_count = cursor.fetchone()[0]
            
            # Truncate Table
            cursor.execute(f"TRUNCATE TABLE {table_name}")
            
            # Verify truncate
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            after_count = cursor.fetchone()[0]
            
            logging.info(
                f"Truncated {table_name}: "
                f"{before_count:,} rows deleted, {after_count} remaining"
            )

        cursor.close()
        logging.info("=" * 70)
        logging.info("All tables truncated successfully")
        logging.info("=" * 70 + "\n")

    except Exception as e:
        logging.error(f"Error during table truncation: {e}\n")
        raise


# ======================================================
# Insert Bronze Layer Data into Silver Layer Tables
# ======================================================
def insert_data(conn):
    logging.info("=" * 70)
    logging.info("Starting Silver Layer Data Insertion Process...")
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
            logging.error(f"Skipping {name} Table due to error")
        
    cursor.close()
    logging.info("=" * 70)
    logging.info("DATA INSERTION SUMMARY")
    logging.info("=" * 70)
    logging.info(f"Total operations: {len(QUERIES)}")
    logging.info(f"Successful: {success_count}")
    logging.info(f"Failed: {failed_count}")
    logging.info("=" * 70 + "\n")
    
    if failed_count == 0:
        logging.info("All Data Inserted successfully!\n")
    else:
        logging.warning(f"{failed_count} operation(s) failed. Check logs above.\n")


# =============================
# Run Script
# =============================
if __name__ == "__main__":
    start_time = time.time()
    
    logging.info("=" * 70)
    logging.info("SILVER LAYER DATA INSERTION - STARTING")
    logging.info("=" * 70)
    
    conn = None
    
    try:
        # Connect to database
        conn = create_connection()
        
        # Truncate existing tables
        truncate_tables(conn)
        
        # Insert Bronze Layer Data into Silver Layer Tables
        insert_data(conn)
        
        # Success message
        end_time = time.time()
        duration = end_time - start_time
        
        logging.info("=" * 70)
        logging.info("SILVER LAYER DATA INSERTION COMPLETED SUCCESSFULLY")
        logging.info(f"Total time: {duration:.2f} seconds")
        logging.info("=" * 70 + "\n")
        
        print("\n" + "=" * 70)
        print("All Data Inserted Successfully!")
        print(f"Time taken: {duration:.2f} seconds")
        print(f"Check logs: {os.path.join(LOG_DIR, LOG_FILE)}")
        print("=" * 70 + "\n")
    
    except Exception as e:
        logging.error("=" * 70)
        logging.error("SILVER LAYER DATA INSERTION FAILED")
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
