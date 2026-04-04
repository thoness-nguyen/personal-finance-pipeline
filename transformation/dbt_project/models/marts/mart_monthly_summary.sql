-- =============================================================================
-- File: models/marts/mart_monthly_summary.sql
-- Purpose: Mart model aggregating total spend per month and year.
--          Used by the Streamlit overview page and BI tools for trend analysis.
-- =============================================================================

-- TODO: SELECT year, month, month_name from time_dim joined to stg_expenses.
-- TODO: SUM(amount) AS total_spend grouped by year, month.
-- TODO: COUNT(id) AS transaction_count grouped by year, month.
-- TODO: ORDER BY year, month.

SELECT
    -- TODO: Implement monthly aggregation
    NULL AS placeholder
FROM {{ ref('stg_expenses') }}

-- TODO: Remove placeholder and implement full aggregation
