# =============================================================================
# File: visualization/streamlit_app/app.py
# Purpose: Main entry point for the multi-page Streamlit dashboard.
#          Renders a sidebar navigation menu, displays a health-check status
#          banner, and provides a landing page with high-level KPI cards.
# =============================================================================

import streamlit as st

# TODO: from utils.db_connector import get_engine
# TODO: import pandas as pd

st.set_page_config(
    page_title="Personal Finance Dashboard",
    page_icon="💰",
    layout="wide",
)

# Sidebar navigation
st.sidebar.title("💰 Finance Dashboard")
st.sidebar.markdown("---")
st.sidebar.markdown("**Navigation**")
st.sidebar.markdown("Use the pages below to explore your finances:")

# TODO: Add sidebar links or use st.Page() navigation (Streamlit 1.28+)

st.title("Personal Finance Pipeline – Dashboard")
st.markdown("Welcome to your personal finance dashboard.")

# TODO: Display a health-check status badge by querying the API /health endpoint.

st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Spend (MTD)", value="$0.00")
    # TODO: Query mart_monthly_summary for current month total spend.

with col2:
    st.metric(label="Transactions (MTD)", value="0")
    # TODO: Query mart_monthly_summary for current month transaction count.

with col3:
    st.metric(label="Top Category", value="—")
    # TODO: Query mart_category_breakdown for highest spend category this month.

with col4:
    st.metric(label="Top Merchant", value="—")
    # TODO: Query mart_top_merchants for highest spend merchant this month.

st.markdown("---")
st.caption("Personal Finance Pipeline • Phase 1–4 scaffold")
