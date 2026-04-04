# =============================================================================
# File: visualization/streamlit_app/pages/02_categories.py
# Purpose: Category breakdown page showing spend distribution across categories.
#          Queries mart_category_breakdown to render pie and bar charts.
# =============================================================================

import streamlit as st

# TODO: from utils.db_connector import get_engine
# TODO: import pandas as pd
# TODO: import plotly.express as px

st.set_page_config(page_title="Categories", page_icon="🏷️", layout="wide")

st.title("🏷️ Category Breakdown")
st.markdown("Spending distribution by category.")

# TODO: Add a month/year selector widget (st.selectbox or st.date_input).
# TODO: Load data from mart_category_breakdown filtered to selected period.

st.subheader("Spend by Category")
# TODO: Render a Plotly pie chart: labels=category_name, values=total_spend.
st.info("TODO: Implement category pie chart")

st.subheader("Category Comparison")
# TODO: Render a Plotly horizontal bar chart: x=total_spend, y=category_name.
st.info("TODO: Implement category bar chart")
