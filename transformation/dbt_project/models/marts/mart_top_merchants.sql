-- =============================================================================
-- File: models/marts/mart_top_merchants.sql
-- Purpose: Spend grouped by subcategory (used as merchant proxy) ranked by
--          total spend. Used by the Streamlit merchants page and BI tools.
--          Note: transactions don't have a merchant field — subcategory_name
--          is the closest proxy (e.g. "Coffee/Drinks", "Daily meals").
-- =============================================================================
SELECT
    COALESCE(subcategory_name, category_name)   AS merchant,
    category_name,
    spending_type,
    COUNT(id)                                   AS visit_count,
    SUM(amount)                                 AS total_spend,
    MIN(expense_date)                           AS first_seen,
    MAX(expense_date)                           AS last_seen,
    RANK() OVER (ORDER BY SUM(amount) DESC)     AS spend_rank
FROM {{ ref('stg_expenses') }}
GROUP BY
    COALESCE(subcategory_name, category_name),
    category_name,
    spending_type
ORDER BY total_spend DESC