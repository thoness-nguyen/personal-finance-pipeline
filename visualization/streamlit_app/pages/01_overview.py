# =============================================================================
# File: visualization/streamlit_app/pages/01_overview.py
# Purpose: Monthly spend overview — bar chart and cumulative spend line chart.
#          Reads from mart_monthly_summary (dbt mart table only).
# =============================================================================

from datetime import date

import plotly.express as px
import streamlit as st

from utils.auth import require_login
from utils.db_connector import query_df

st.set_page_config(page_title="Overview", page_icon="📅", layout="wide")

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
def load_monthly_summary(
    start_yr: int, start_mo: int, end_yr: int, end_mo: int
):
    df = query_df(
        f"""
        SELECT yr, mo, total_spend, fixed_spend, extra_spend, transaction_count
        FROM mart_monthly_summary
        WHERE (yr > {start_yr} OR (yr = {start_yr} AND mo >= {start_mo}))
          AND (yr < {end_yr}   OR (yr = {end_yr}   AND mo <= {end_mo}))
        ORDER BY yr, mo
        """
    )
    if df.empty:
        return df
    df["month_label"] = df.apply(
        lambda r: date(int(r["yr"]), int(r["mo"]), 1).strftime("%b %Y"), axis=1
    )
    df["month_date"] = df.apply(
        lambda r: date(int(r["yr"]), int(r["mo"]), 1), axis=1
    )
    df["cumulative_spend"] = df["total_spend"].cumsum()
    return df


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------
st.title("📅 Monthly Overview")
st.markdown("Total spend and transaction trends by month.")

try:
    df = load_monthly_summary(
        date_start.year, date_start.month,
        date_end.year, date_end.month,
    )

    if df.empty:
        st.info("No data found for the selected date range.")
    else:
        # Bar chart – monthly spend grouped by year
        st.subheader("Total Spend by Month")
        fig_bar = px.bar(
            df,
            x="month_label",
            y="total_spend",
            color=df["yr"].astype(str),
            barmode="group",
            labels={
                "month_label": "Month",
                "total_spend": "Total Spend (₫)",
                "color": "Year",
            },
            title="Monthly Total Spend",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_bar.update_layout(xaxis_tickangle=-45, legend_title="Year")
        st.plotly_chart(fig_bar, use_container_width=True)

        # Line chart – cumulative spend
        st.subheader("Cumulative Spend Over Time")
        fig_line = px.line(
            df,
            x="month_date",
            y="cumulative_spend",
            markers=True,
            labels={"month_date": "Month", "cumulative_spend": "Cumulative Spend (₫)"},
            title="Cumulative Spend",
        )
        fig_line.update_traces(line_color="#1f77b4", line_width=2)
        st.plotly_chart(fig_line, use_container_width=True)

        # Summary table
        st.subheader("Monthly Summary Table")
        display_df = df[
            ["month_label", "total_spend", "fixed_spend", "extra_spend", "transaction_count"]
        ].copy()
        display_df.columns = ["Month", "Total (₫)", "Fixed (₫)", "Extra (₫)", "Transactions"]
        st.dataframe(
            display_df.style.format(
                {"Total (₫)": "{:,.0f}", "Fixed (₫)": "{:,.0f}", "Extra (₫)": "{:,.0f}"}
            ),
            use_container_width=True,
        )

except Exception as exc:
    st.error(f"Failed to load overview data: {exc}")
