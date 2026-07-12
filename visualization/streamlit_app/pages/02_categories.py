# =============================================================================
# File: visualization/streamlit_app/pages/02_categories.py
# Purpose: Category breakdown — pie chart and month-over-month stacked bar.
#          Reads from mart_category_breakdown (dbt mart table only).
# =============================================================================

from datetime import date

import plotly.express as px
import streamlit as st

from utils.auth import require_login
from utils.db_connector import query_df

st.set_page_config(page_title="Categories", page_icon="🏷️", layout="wide")

require_login()

# ---------------------------------------------------------------------------
# Sidebar – date range
# ---------------------------------------------------------------------------
st.sidebar.title("💰 Finance Dashboard")
st.sidebar.markdown("---")
st.sidebar.markdown("**Date Range**")

today = date.today()
default_start = date(today.year - 1, today.month, 1)
date_start = st.sidebar.date_input(
    "From", value=st.session_state.get("date_start", default_start), key="date_start"
)
date_end = st.sidebar.date_input(
    "To", value=st.session_state.get("date_end", today), key="date_end"
)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300)
def load_category_data(
    start_yr: int, start_mo: int, end_yr: int, end_mo: int
):
    df = query_df(
        f"""
        SELECT yr, mo, category_name, spending_type, tx_count, total_spend, pct_of_month
        FROM mart_category_breakdown
        WHERE (yr > {start_yr} OR (yr = {start_yr} AND mo >= {start_mo}))
          AND (yr < {end_yr}   OR (yr = {end_yr}   AND mo <= {end_mo}))
        ORDER BY yr, mo, total_spend DESC
        """
    )
    if df.empty:
        return df
    df["month_label"] = df.apply(
        lambda r: date(int(r["yr"]), int(r["mo"]), 1).strftime("%b %Y"), axis=1
    )
    return df


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------
st.title("🏷️ Category Breakdown")
st.markdown("Spending distribution across categories.")

try:
    df = load_category_data(
        date_start.year, date_start.month,
        date_end.year, date_end.month,
    )

    if df.empty:
        st.info("No data found for the selected date range.")
    else:
        # Aggregate totals over the range for the pie + ranked bar
        agg = df.groupby("category_name", as_index=False)["total_spend"].sum()
        agg = agg.sort_values("total_spend", ascending=False)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Spend by Category")
            fig_pie = px.pie(
                agg,
                names="category_name",
                values="total_spend",
                title="Category Share of Total Spend",
                hole=0.3,
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            st.subheader("Category Totals (Ranked)")
            fig_hbar = px.bar(
                agg,
                x="total_spend",
                y="category_name",
                orientation="h",
                labels={"total_spend": "Total Spend (₫)", "category_name": "Category"},
                title="Spend by Category",
                color="total_spend",
                color_continuous_scale="Blues",
            )
            fig_hbar.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_hbar, use_container_width=True)

        # Month-over-month stacked bar chart
        st.subheader("Month-over-Month by Category")
        mom = df.groupby(["month_label", "yr", "mo", "category_name"], as_index=False)[
            "total_spend"
        ].sum()
        month_order = (
            df[["yr", "mo", "month_label"]]
            .drop_duplicates()
            .sort_values(["yr", "mo"])["month_label"]
            .tolist()
        )
        fig_mom = px.bar(
            mom,
            x="month_label",
            y="total_spend",
            color="category_name",
            barmode="stack",
            category_orders={"month_label": month_order},
            labels={
                "month_label": "Month",
                "total_spend": "Spend (₫)",
                "category_name": "Category",
            },
            title="Monthly Spend by Category",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_mom.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_mom, use_container_width=True)

except Exception as exc:
    st.error(f"Failed to load category data: {exc}")
