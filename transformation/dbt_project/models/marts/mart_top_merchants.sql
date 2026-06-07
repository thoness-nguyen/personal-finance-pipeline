-- =============================================================================
-- File: models/marts/mart_top_merchants.sql
-- Purpose: Mart model aggregating total spend per merchant, ranked by spend.
--          Used by the Streamlit merchants page and BI tools.
-- =============================================================================
-- TODO: SELECT merchant_name from merchants joined via stg_expenses.
-- TODO: SUM(amount) AS total_spend grouped by merchant.
-- TODO: COUNT(id) AS visit_count grouped by merchant.
-- TODO: RANK() OVER (ORDER BY total_spend DESC) AS spend_rank.
-- TODO: Optionally filter to a configurable time window (e.g. last 12 months).
SELECT COALESCE(description, '(no description)') AS merchant,
    category_name,
    COUNT(id) AS visit_count,
    SUM(amount) AS total_spend,
    RANK() OVER (
        ORDER BY SUM(amount) DESC
    ) AS spend_rank
FROM { { ref('stg_expenses') } }
WHERE expense_date IS NOT NULL
GROUP BY 1,
    2
ORDER BY total_spend DESC