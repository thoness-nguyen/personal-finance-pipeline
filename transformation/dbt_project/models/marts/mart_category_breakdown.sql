-- =============================================================================
-- File: models/marts/mart_category_breakdown.sql
-- Purpose: Mart model aggregating total spend per category per month.
--          Used by the Streamlit categories page and BI tools for category analysis.
-- =============================================================================
-- TODO: SELECT category_name from categories joined via stg_expenses.
-- TODO: SUM(amount) AS total_spend grouped by category and month/year.
-- TODO: ROUND percentage share of total monthly spend for each category.
-- TODO: ORDER BY year, month, total_spend DESC.
SELECT YEAR(expense_date) AS yr,
    MONTH(expense_date) AS mo,
    category_name,
    spending_type,
    COUNT(id) AS tx_count,
    SUM(amount) AS total_spend,
    ROUND(
        100.0 * SUM(amount) / SUM(SUM(amount)) OVER (
            PARTITION BY YEAR(expense_date),
            MONTH(expense_date)
        ),
        2
    ) AS pct_of_month
FROM { { ref('stg_expenses') } }
WHERE expense_date IS NOT NULL
GROUP BY 1,
    2,
    3,
    4
ORDER BY yr,
    mo,
    total_spend DESC