-- =============================================================================
-- File: models/marts/mart_monthly_summary.sql
-- Purpose: Monthly spend aggregation — total, fixed, and extra spend per month.
--          Used by the Streamlit overview page and BI tools for trend analysis.
-- =============================================================================
SELECT
    yr,
    mo,
    COUNT(id)                                                   AS transaction_count,
    SUM(amount)                                                 AS total_spend,
    SUM(CASE WHEN spending_type = 'fixed' THEN amount ELSE 0 END) AS fixed_spend,
    SUM(CASE WHEN spending_type = 'extra' THEN amount ELSE 0 END) AS extra_spend,
    SUM(CASE WHEN is_regretted = 1      THEN amount ELSE 0 END) AS regretted_spend,
    COUNT(DISTINCT category_id)                                 AS categories_used
FROM {{ ref('stg_expenses') }}
GROUP BY yr, mo
ORDER BY yr, mo