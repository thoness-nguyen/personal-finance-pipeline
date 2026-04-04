# =============================================================================
# File: visualization/streamlit_app/pages/03_merchants.py
# Purpose: Top merchants page showing spend and visit counts by merchant.
#          Queries mart_top_merchants to render a ranked table and bar chart.
# =============================================================================

import streamlit as st

# TODO: from utils.db_connector import get_engine
# TODO: import pandas as pd
# TODO: import plotly.express as px

st.set_page_config(page_title="Merchants", page_icon="🏪", layout="wide")

st.title("🏪 Top Merchants")
st.markdown("Your most-visited and highest-spend merchants.")

# TODO: Add a Top-N slider widget (st.slider, default 10).
# TODO: Load data from mart_top_merchants limited to Top-N.

st.subheader("Merchant Spend Ranking")
# TODO: Render an interactive st.dataframe with merchant_name, total_spend, visit_count, spend_rank.
st.info("TODO: Implement top merchants table")

st.subheader("Top Merchant Spend Chart")
# TODO: Render a Plotly horizontal bar chart: x=total_spend, y=merchant_name (top N).
st.info("TODO: Implement top merchants bar chart")
