-- =============================================================================
-- File: models/marts/mart_monthly_summary.sql
-- Purpose: Mart model aggregating total spend per month and year.
--          Used by the Streamlit overview page and BI tools for trend analysis.
-- =============================================================================
-- TODO: SELECT year, month, month_name from time_dim joined to stg_expenses.
-- TODO: SUM(amount) AS total_spend grouped by year, month.
-- TODO: COUNT(id) AS transaction_count grouped by year, month.
-- TODO: ORDER BY year, month.
SELECT YEAR(expense_date) AS yr,
    MONTH(expense_date) AS mo,
    COUNT(id) AS transaction_count,
    SUM(amount) AS total_spend,
    SUM(
        CASE
            WHEN spending_type = 'fixed' THEN amount
            ELSE 0
        END
    ) AS fixed_spend,
    SUM(
        CASE
            WHEN spending_type = 'extra' THEN amount
            ELSE 0
        END
    ) AS extra_spend
FROM {{ref('stg_expenses')}}
WHERE expense_date IS NOT NULL
GROUP BY 1,
    2
ORDER BY yr,
    mo