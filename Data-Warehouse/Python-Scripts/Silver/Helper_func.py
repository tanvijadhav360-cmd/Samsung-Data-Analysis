import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
import os 
import time

# ===============================
# Logging Configuration
# ===============================
LOG_DIR = "Logs"
LOG_FILE = "Helper_func.log"

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


# ============================================================
# SHARED HELPER FUNCTIONS
# ============================================================
SCHEMA = "CREATE SCHEMA IF NOT EXISTS cleaning;"

FN_TO_BOOLEAN = """
CREATE OR REPLACE FUNCTION cleaning.fn_to_boolean(raw_val TEXT)
        RETURNS BOOLEAN
        LANGUAGE SQL
        IMMUTABLE
        AS $$
            SELECT CASE
                WHEN TRIM(LOWER(raw_val)) IN ('yes','1','true','active','verified purchase') THEN TRUE
                WHEN TRIM(LOWER(raw_val)) IN ('no','0','false','inactive')                  THEN FALSE
                ELSE NULL
            END;
        $$;
"""

FN_CLEAN_PHONE = """
CREATE OR REPLACE FUNCTION cleaning.fn_clean_phone(raw_phone TEXT)
RETURNS CHAR(10)
LANGUAGE SQL
IMMUTABLE
AS $$
    SELECT CASE
        WHEN raw_phone IS NULL THEN NULL
        WHEN TRIM(raw_phone) ~ '^\+91[6-9][0-9]{9}$'  THEN SUBSTRING(TRIM(raw_phone), 4, 10)
        WHEN TRIM(raw_phone) ~ '^0[6-9][0-9]{9}$'     THEN SUBSTRING(TRIM(raw_phone), 2, 10)
        WHEN TRIM(raw_phone) ~ '^[6-9][0-9]{9}$'       THEN TRIM(raw_phone)
        ELSE NULL   -- Invalid format — set to NULL
    END;
$$;
"""

FN_PARSE_DATE = """
CREATE OR REPLACE FUNCTION cleaning.fn_parse_date(raw_date TEXT)
RETURNS DATE
LANGUAGE PLPGSQL
IMMUTABLE
AS $$
BEGIN
    IF raw_date IS NULL OR TRIM(raw_date) = '' THEN RETURN NULL; END IF;
    BEGIN RETURN TO_DATE(TRIM(raw_date), 'YYYY-MM-DD'); EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN RETURN TO_DATE(TRIM(raw_date), 'DD/MM/YYYY'); EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN RETURN TO_DATE(TRIM(raw_date), 'DD-MM-YYYY'); EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN RETURN TO_DATE(TRIM(raw_date), 'MM/DD/YYYY'); EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN RETURN TO_DATE(TRIM(raw_date), 'YYYY/MM/DD'); EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN RETURN TO_DATE(TRIM(raw_date), 'DD Mon YYYY'); EXCEPTION WHEN OTHERS THEN NULL; END;
    RETURN NULL;
END;
$$;
"""

FN_PARSE_EPOCH_OR_DATE = """
CREATE OR REPLACE FUNCTION cleaning.fn_parse_epoch_or_date(raw_val TEXT)
RETURNS DATE
LANGUAGE PLPGSQL
IMMUTABLE
AS $$
BEGIN
    IF raw_val IS NULL THEN RETURN NULL; END IF;
    -- If it looks like an epoch (all digits, 10 chars)
    IF raw_val ~ '^[0-9]{9,11}$' THEN
        RETURN TO_TIMESTAMP(raw_val::BIGINT)::DATE;
    END IF;
    RETURN cleaning.fn_parse_date(raw_val);
END;
$$;
"""

FN_PARSE_GST_PCT = """
CREATE OR REPLACE FUNCTION cleaning.fn_parse_gst_pct(raw_gst TEXT)
RETURNS NUMERIC(4,1)
LANGUAGE PLPGSQL
IMMUTABLE
AS $$
DECLARE
    cleaned TEXT;
    result  NUMERIC;
BEGIN
    IF raw_gst IS NULL THEN RETURN NULL; END IF;
    cleaned := TRIM(UPPER(raw_gst));
    -- Handle "GST@18" format
    IF cleaned LIKE 'GST@%' THEN cleaned := REPLACE(cleaned, 'GST@', ''); END IF;
    cleaned := REPLACE(cleaned, '%', '');
    BEGIN
        result := cleaned::NUMERIC;
        -- Only accept valid Indian GST rates
        IF result IN (5, 12, 18, 28) THEN RETURN result;
        ELSE RETURN NULL;
        END IF;
    EXCEPTION WHEN OTHERS THEN RETURN NULL;
    END;
END;
$$;
"""

FN_SALARY_TO_ANNUAL = """
CREATE OR REPLACE FUNCTION cleaning.fn_salary_to_annual(raw_salary TEXT)
RETURNS NUMERIC(12,2)
LANGUAGE PLPGSQL
IMMUTABLE
AS $$
DECLARE
    cleaned TEXT;
    num     NUMERIC;
BEGIN
    IF raw_salary IS NULL OR TRIM(raw_salary) = '' THEN RETURN NULL; END IF;
    cleaned := TRIM(UPPER(raw_salary));

    -- Format: "18 LPA" or "18LPA"
    IF cleaned LIKE '%LPA%' THEN
        num := REGEXP_REPLACE(cleaned, '[^0-9.]', '', 'g')::NUMERIC;
        RETURN ROUND(num * 100000, 2);   -- Convert Lakhs to rupees
    END IF;

    -- Format: "18L" (shorthand Lakhs)
    IF cleaned LIKE '%L' AND cleaned NOT LIKE '%LPA%' THEN
        num := REGEXP_REPLACE(cleaned, '[^0-9.]', '', 'g')::NUMERIC;
        RETURN ROUND(num * 100000, 2);
    END IF;

    -- Format: plain number → assume monthly salary × 12
    IF cleaned ~ '^[0-9]+(\.[0-9]+)?$' THEN
        num := cleaned::NUMERIC;
        -- Heuristic: if > 200000 it is likely already annual, else monthly
        IF num > 200000 THEN RETURN ROUND(num, 2);
        ELSE RETURN ROUND(num * 12, 2);
        END IF;
    END IF;

    RETURN NULL;
END;
$$;
"""

Helper_Func = [
    (SCHEMA, "cleaning Schema"),
    (FN_TO_BOOLEAN, "fn_to_boolean Function"),
    (FN_CLEAN_PHONE, "fn_clean_phone Function"),
    (FN_PARSE_DATE, "fn_parse_date Function"),
    (FN_PARSE_EPOCH_OR_DATE, "fn_parse_epoch_or_date Function"),
    (FN_PARSE_GST_PCT, "fn_parse_gst_pct Function"),
    (FN_SALARY_TO_ANNUAL, "fn_salary_to_annual Function")
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
        logging.info(f"Executing: {query_name} Query")
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
def create_helper_func(conn):
    logging.info("=" * 70)
    logging.info("Starting Helper Function Creation Process...")
    logging.info("=" * 70)
    cursor = conn.cursor()
    
    success_count = 0
    failed_count = 0
    
    for query, name in Helper_Func:
        try:
            execute_query(cursor, query, name)
            success_count += 1
        except Exception as e:
            failed_count += 1
            logging.error(f"Skipping {name} due to error")
        
    cursor.close()
    logging.info("=" * 70)
    logging.info("HELPER FUNCTION SUMMARY")
    logging.info("=" * 70)
    logging.info(f"Total operations: {len(Helper_Func)}")
    logging.info(f"Successful: {success_count}")
    logging.info(f"Failed: {failed_count}")
    logging.info("=" * 70 + "\n")
    
    if failed_count == 0:
        logging.info("All Helper Function created successfully!\n")
    else:
        logging.warning(f"{failed_count} operation(s) failed. Check logs above.\n")


# =============================
# Run Script
# =============================
if __name__ == "__main__":
    start_time = time.time()
    
    logging.info("=" * 70)
    logging.info("HELPER FUNCTION SETUP - STARTING")
    logging.info("=" * 70)
    
    conn = None
    
    try:
        # Connect to database
        conn = create_connection()
        
        # Create all Helper Function
        create_helper_func(conn)
        
        # Success message
        end_time = time.time()
        duration = end_time - start_time
        
        logging.info("=" * 70)
        logging.info("HELPER FUNCTION CREATION COMPLETED SUCCESSFULLY")
        logging.info(f"Total time: {duration:.2f} seconds")
        logging.info("=" * 70 + "\n")
        
        print("\n" + "=" * 70)
        print("All Helper Functions Created Successfully!")
        print(f"Time taken: {duration:.2f} seconds")
        print(f"Check logs: {os.path.join(LOG_DIR, LOG_FILE)}")
        print("=" * 70 + "\n")
    
    except Exception as e:
        logging.error("=" * 70)
        logging.error("HELPER FUNCTION CREATION FAILED")
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
