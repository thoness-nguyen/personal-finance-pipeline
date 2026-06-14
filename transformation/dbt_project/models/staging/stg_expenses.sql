-- =============================================================================
-- File: models/staging/stg_expenses.sql
-- Purpose: Staging model — selects expense & credit_purchase rows from the
--          transactions fact table, enriches with account/category/subcategory
--          names, and casts columns to consistent types for downstream marts.
-- =============================================================================
SELECT
    t.transaction_id                        AS id,
    CAST(t.transaction_date AS DATE)        AS expense_date,
    YEAR(t.transaction_date)                AS yr,
    MONTH(t.transaction_date)               AS mo,
    CAST(t.amount AS DECIMAL(15,0))         AS amount,
    a.account_name,
    a.account_type,
    a.currency,
    t.transaction_type,
    t.spending_type,
    t.category_id,
    c.category_name,
    t.subcategory_id,
    s.subcategory_name,
    t.payment_method,
    t.note                                  AS description,
    t.is_regretted,
    t.source_data                           AS source
FROM {{ source('finance_db', 'transactions') }} t
LEFT JOIN {{ source('finance_db', 'accounts') }}     a ON t.account_id     = a.account_id
LEFT JOIN {{ source('finance_db', 'categories') }}   c ON t.category_id    = c.category_id
LEFT JOIN {{ source('finance_db', 'subcategories') }} s ON t.subcategory_id = s.subcategory_id
WHERE t.transaction_type IN ('expense', 'credit_purchase')
  AND t.transaction_date IS NOT NULL