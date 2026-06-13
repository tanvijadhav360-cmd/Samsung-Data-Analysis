# **📒 Naming Conventions**

This document outlines the Naming Conventions used for schemas, tables, views, columns, and other objects in the Data Warehouse for **Samsung Data Engineering** Project.

---

## Table of Contents

1. [General Principles](#-general-principles)
2. [Table Naming Conventions](#️-table-naming-conventions)
   - [Bronze Rules](#-bronze-rules)
   - [Silver Rules](#-silver-rules)
   - [Gold Rules](#-gold-rules)
3. [Column Naming Conventions](#️-column-naming-conventions)
   - [Surrogate Keys](#️⃣-surrogate-keys)
   - [Technical Columns](#️-technical-columns)
4. [Stored Procedure](#-stored-procedure)

---

## 📜 General Principles

- **Naming Conventions**: Use snake_case, with lowercase letters and underscores (`_`) to separate words.
- **Language**: Use English for all names.
- **Avoid Reserved Words**: Do not use SQL reserved words as object names.

---

## 🏗️ Table Naming Conventions

### 🥉 Bronze Rules

- All names must start with the source system name, and table names must match their original names without renaming.

- **`<sourcesystem>_<entity>`**  
  - `<sourcesystem>`: Name of the source system (e.g., `as2`, `crm`, `hrm` etc.).  
  - `<entity>`: Exact table name from the source system.  
  - *Example:* `crm_customers` → Customer information from the CRM system.

---

### 🥈 Silver Rules

- All names must start with the source system name, and table names must match their original names without renaming.

- **`<sourcesystem>_<entity>`**  
  - `<sourcesystem>`: Name of the source system (`as2`, `crm`, `hrm` etc.).  
  - `<entity>`: Exact table name from the source system.  
  - *Example:* `crm_customers` → Customer information from the CRM system.

---

### 🥇 Gold Rules

- All names must use meaningful, business-aligned names for tables, starting with the category prefix.

- **`<category>_<entity>`**  
  - `<category>`: Describes the role of the table, such as `dim` (dimension) or `fact` (fact table).  
  - `<entity>`: Descriptive name of the table, aligned with the business domain (e.g., `customers`, `products`, `sales_transactions`).  
  - *Example:*
    - `dim_customers` → Dimension table for customer data.  
    - `fact_sales_transactions` → Fact table containing sales transactions.  

### 🧩 Glossary of Category Patterns

| Pattern     | Meaning                           | Example(s)                              |
|-------------|-----------------------------------|-----------------------------------------|
| `dim_`      | Dimension table                  | `dim_customer`, `dim_product`           |
| `fact_`     | Fact table                       | `fact_sales_transactions`                        |
| `agg_`   | Aggregated table                     | `agg_orders`, `agg_order_items`   |

---

## 🏷️ Column Naming Conventions

### #️⃣ Surrogate Keys 

- All primary keys in dimension tables must use the suffix `_id`.

- **`<table_name>_id`**  
  - `<table_name>`: Refers to the name of the table or entity the key belongs to.  
  - `_key`: A suffix indicating that this column is a surrogate key.  
  - *Example:* `customer_id` → Surrogate key in the `dim_customers` table.

### 🖥️ Technical Columns

- All technical columns must start with the prefix `dwh_`, followed by a descriptive name indicating the column's purpose.

- **`dwh_<column_name>`**  
  - `dwh`: Prefix exclusively for system-generated metadata.  
  - `<column_name>`: Descriptive name indicating the column's purpose.  
  - *Example:* `dwh_load_date` → System-generated column used to store the date when the record was loaded.

---

## 💾 Stored Procedure

- All stored procedures used for loading data must follow the naming pattern:

- **`load_<layer>`**.
  - `<layer>`: Represents the layer being loaded, such as `bronze`, `silver`, or `gold`.
  - *Example:*
    - `load_bronze` → Stored procedure for loading data into the Bronze layer.
    - `load_silver` → Stored procedure for loading data into the Silver layer.

---

## 🧑‍💻 Author

**👤 Harsh Belekar**  
📍 Data Analyst | Python Developer | SQL | Power BI | Excel | Data Visualization  
📬[LinkedIn](https://www.linkedin.com/in/harshbelekar) | 🔗[GitHub](https://github.com/Harsh-Belekar)

📧 [harshbelekar74@gmail.com](mailto:harshbelekar74@gmail.com)
