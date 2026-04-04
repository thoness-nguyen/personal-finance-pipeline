# =============================================================================
# File: visualization/streamlit_app/pages/04_trends.py
# Purpose: Trends and forecasting page. Displays historical spend trends and
#          serves as the placeholder for Phase 5 ML-based predictions
#          (Prophet/ARIMA forecasting, anomaly detection).
# =============================================================================

import streamlit as st

# TODO: from utils.db_connector import get_engine
# TODO: import pandas as pd
# TODO: import plotly.express as px

st.set_page_config(page_title="Trends & Forecast", page_icon="📈", layout="wide")

st.title("📈 Trends & Forecast")
st.markdown("Historical spend trends and future forecasts (Phase 5).")

# TODO: Load monthly spend data from mart_monthly_summary.

st.subheader("Historical Spend Trend")
# TODO: Render a Plotly line chart with a rolling average overlay.
st.info("TODO: Implement historical trend line chart")

st.subheader("📊 Spend Forecast (Phase 5)")
st.warning(
    "🚧 Forecasting will be implemented in Phase 5 using Prophet/ARIMA models "
    "trained in data_science/notebooks/02_forecasting.ipynb."
)
# TODO: Call Phase 5 ML model to generate forecast data.
# TODO: Render a Plotly line chart with historical + forecast bands.

st.subheader("🔍 Anomaly Detection (Phase 5)")
st.warning(
    "🚧 Anomaly detection will be implemented in Phase 5. "
    "See data_science/notebooks/03_anomaly_detection.ipynb."
)
# TODO: Highlight anomalous transactions in a table view.
