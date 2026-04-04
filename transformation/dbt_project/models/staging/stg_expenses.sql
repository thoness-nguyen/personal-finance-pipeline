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

SELECT
    -- TODO: Implement column selection and transformations
    NULL AS placeholder
FROM {{ source('finance_db', 'expenses') }}

-- TODO: Remove placeholder and implement full SELECT
