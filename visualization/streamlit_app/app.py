# =============================================================================
# File: visualization/streamlit_app/app.py
# Purpose: Main entry point for the multi-page Streamlit dashboard.
#          Renders a sidebar navigation menu and landing page with KPI cards.
# =============================================================================

from datetime import date

import streamlit as st

from utils.auth import require_login
from utils.db_connector import query_df

st.set_page_config(
    page_title="Personal Finance Dashboard",
    page_icon="💰",
    layout="wide",
)

require_login()

# ---------------------------------------------------------------------------
# Sidebar – date range filter stored in session_state for cross-page access
# ---------------------------------------------------------------------------
st.sidebar.title("💰 Finance Dashboard")
st.sidebar.markdown("---")
st.sidebar.markdown("**Date Range**")

today = date.today()
default_start = date(today.year - 1, today.month, 1)

date_start = st.sidebar.date_input("From", value=default_start, key="date_start")
date_end = st.sidebar.date_input("To", value=today, key="date_end")

st.sidebar.markdown("---")
st.sidebar.caption("Use the pages in the sidebar to explore your finances.")


# ---------------------------------------------------------------------------
# KPI data loaders
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300)
def load_latest_month_kpis():
    return query_df(
        """
        SELECT yr, mo, total_spend, transaction_count
        FROM mart_monthly_summary
        ORDER BY yr DESC, mo DESC
        LIMIT 1
        """
    )


@st.cache_data(ttl=300)
def load_top_category():
    return query_df(
        """
        SELECT category_name, total_spend
        FROM mart_category_breakdown
        ORDER BY yr DESC, mo DESC, total_spend DESC
        LIMIT 1
        """
    )


@st.cache_data(ttl=300)
def load_latest_ingestion_date():
    return query_df("SELECT MAX(last_seen) AS latest FROM mart_top_merchants")


# ---------------------------------------------------------------------------
# Landing page
# ---------------------------------------------------------------------------
st.title("Personal Finance Dashboard")
st.markdown("Overview of your latest financial data. Use the sidebar to explore details.")

st.subheader("📊 Key Performance Indicators")

try:
    kpi_df = load_latest_month_kpis()
    cat_df = load_top_category()
    date_df = load_latest_ingestion_date()

    total_spend = float(kpi_df["total_spend"].iloc[0]) if not kpi_df.empty else 0.0
    tx_count = int(kpi_df["transaction_count"].iloc[0]) if not kpi_df.empty else 0
    top_cat = cat_df["category_name"].iloc[0] if not cat_df.empty else "—"
    latest = date_df["latest"].iloc[0] if not date_df.empty else "—"
    if hasattr(latest, "strftime"):
        latest = latest.strftime("%Y-%m-%d")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Spend (Latest Mo)", f"₫{total_spend:,.0f}")
    with col2:
        st.metric("Transactions (Latest Mo)", f"{tx_count:,}")
    with col3:
        st.metric("Top Category", top_cat)
    with col4:
        st.metric("Latest Ingestion Date", str(latest))

except Exception as exc:
    st.warning(f"Could not load KPIs — check DB connection: {exc}")

st.markdown("---")
st.caption("Personal Finance Pipeline • Phase 4 – Visualisation")
