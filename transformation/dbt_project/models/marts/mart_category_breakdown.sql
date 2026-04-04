-- =============================================================================
-- File: models/marts/mart_category_breakdown.sql
-- Purpose: Mart model aggregating total spend per category per month.
--          Used by the Streamlit categories page and BI tools for category analysis.
-- =============================================================================

-- TODO: SELECT category_name from categories joined via stg_expenses.
-- TODO: SUM(amount) AS total_spend grouped by category and month/year.
-- TODO: ROUND percentage share of total monthly spend for each category.
-- TODO: ORDER BY year, month, total_spend DESC.

SELECT
    -- TODO: Implement category breakdown aggregation
    NULL AS placeholder
FROM {{ ref('stg_expenses') }}

-- TODO: Remove placeholder and implement full aggregation
