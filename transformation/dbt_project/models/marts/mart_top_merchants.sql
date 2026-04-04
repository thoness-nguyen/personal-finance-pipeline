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

SELECT
    -- TODO: Implement top merchants aggregation
    NULL AS placeholder
FROM {{ ref('stg_expenses') }}

-- TODO: Remove placeholder and implement full aggregation
