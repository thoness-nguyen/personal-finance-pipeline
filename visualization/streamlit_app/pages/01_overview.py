# =============================================================================
# File: visualization/streamlit_app/pages/01_overview.py
# Purpose: Overview page showing total monthly spend trends.
#          Queries mart_monthly_summary to render a bar chart and line chart.
# =============================================================================

import streamlit as st

# TODO: from utils.db_connector import get_engine
# TODO: import pandas as pd
# TODO: import plotly.express as px

st.set_page_config(page_title="Overview", page_icon="📅", layout="wide")

st.title("📅 Monthly Overview")
st.markdown("Total spend and transaction trends by month.")

# TODO: Load data from mart_monthly_summary using SQLAlchemy engine.
# TODO: df = pd.read_sql("SELECT * FROM mart_monthly_summary ORDER BY year, month", engine)

st.subheader("Total Spend by Month")
# TODO: Render a Plotly bar chart: x=month_name, y=total_spend, color=year.
st.info("TODO: Implement monthly bar chart")

st.subheader("Spend Trend Over Time")
# TODO: Render a Plotly line chart: x=date, y=cumulative_spend.
st.info("TODO: Implement spend trend line chart")
