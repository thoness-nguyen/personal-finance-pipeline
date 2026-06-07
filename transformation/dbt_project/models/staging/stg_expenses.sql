-- =============================================================================
-- File: models/staging/stg_expenses.sql
-- Purpose: Staging model that selects from the raw expenses source table,
--          renames/casts columns to consistent names, and joins category
--          and merchant names for downstream use.
-- =============================================================================
-- TODO: SELECT and rename columns from source('finance_db', 'expenses').
-- TODO: Cast expense_date to DATE type.
-- TODO: Cast amount to DECIMAL/FLOAT.
-- TODO: Join categories table to include category_name.
-- TODO: Join merchants table to include merchant_name.
-- TODO: Filter out rows where needs_cleaning = TRUE.
SELECT t.transaction_id AS id,
    t.transaction_date AS expense_date,
    t.amount,
    a.currency,
    t.note AS description,
    t.category_id,
    c.category_name,
    t.subcategory_id,
    s.subcategory_name,
    t.payment_method,
    t.spending_type,
    t.is_regretted,
    t.source_data AS source
FROM { { source('finance_db', 'transactions') } } t
    LEFT JOIN { { source('finance_db', 'categories') } } c ON t.category_id = c.category_id
    LEFT JOIN { { source('finance_db', 'subcategories') } } s ON t.subcategory_id = s.subcategory_id
    LEFT JOIN { { source('finance_db', 'accounts') } } a ON t.account_id = a.account_id
WHERE t.transaction_type IN ('expense', 'credit_purchase')