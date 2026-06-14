-- =============================================================================
-- File: models/marts/mart_category_breakdown.sql
-- Purpose: Spend per category per month with % share of that month's total.
--          Used by the Streamlit categories page and BI tools.
-- =============================================================================
SELECT
    yr,
    mo,
    category_id,
    category_name,
    subcategory_name,
    spending_type,
    COUNT(id)       AS tx_count,
    SUM(amount)     AS total_spend,
    ROUND(
        100.0 * SUM(amount) / SUM(SUM(amount)) OVER (
            PARTITION BY yr, mo
        ),
        2
    )               AS pct_of_month
FROM {{ ref('stg_expenses') }}
GROUP BY yr, mo, category_id, category_name, subcategory_name, spending_type
ORDER BY yr, mo, total_spend DESC