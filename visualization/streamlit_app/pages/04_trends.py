# =============================================================================
# File: visualization/streamlit_app/pages/04_trends.py
# Purpose: Trends & Forecast — year-over-year comparison, rolling 3-month
#          average, monthly heatmap, and Phase 5 ML placeholder.
#          Reads from mart_monthly_summary (dbt mart table only).
# =============================================================================

from datetime import date

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.auth import require_login
from utils.db_connector import query_df

st.set_page_config(page_title="Trends & Forecast", page_icon="📈", layout="wide")

require_login()

# ---------------------------------------------------------------------------
# Sidebar – date range (defaults to 2 years for meaningful YoY comparison)
# ---------------------------------------------------------------------------
st.sidebar.title("💰 Finance Dashboard")
st.sidebar.markdown("---")
st.sidebar.markdown("**Date Range**")

today = date.today()
default_start = date(today.year - 2, today.month, 1)
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
def load_trend_data(
    start_yr: int, start_mo: int, end_yr: int, end_mo: int
):
    import pandas as pd

    df = query_df(
        f"""
        SELECT yr, mo, total_spend, transaction_count
        FROM mart_monthly_summary
        WHERE (yr > {start_yr} OR (yr = {start_yr} AND mo >= {start_mo}))
          AND (yr < {end_yr}   OR (yr = {end_yr}   AND mo <= {end_mo}))
        ORDER BY yr, mo
        """
    )
    if df.empty:
        return df
    df["month_date"] = pd.to_datetime(
        df.apply(lambda r: f"{int(r['yr'])}-{int(r['mo']):02d}-01", axis=1)
    )
    df["month_label"] = df["month_date"].dt.strftime("%b %Y")
    df["rolling_3mo"] = df["total_spend"].rolling(window=3, min_periods=1).mean()
    df["yr_str"] = df["yr"].astype(str)
    return df


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------
st.title("📈 Trends & Forecast")
st.markdown("Historical spend trends and future forecasts (Phase 5).")

try:
    df = load_trend_data(
        date_start.year, date_start.month,
        date_end.year, date_end.month,
    )

    if df.empty:
        st.info("No data found for the selected date range.")
    else:
        month_names = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
        ]

        # ── Year-over-Year Comparison ──────────────────────────────────────
        st.subheader("📆 Year-over-Year Spend Comparison")
        fig_yoy = px.line(
            df,
            x="mo",
            y="total_spend",
            color="yr_str",
            markers=True,
            labels={"mo": "Month", "total_spend": "Spend (₫)", "yr_str": "Year"},
            title="Year-over-Year Monthly Spend",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_yoy.update_xaxes(
            tickmode="array",
            tickvals=list(range(1, 13)),
            ticktext=month_names,
        )
        fig_yoy.update_layout(legend_title="Year")
        st.plotly_chart(fig_yoy, use_container_width=True)

        # ── Rolling 3-Month Average ────────────────────────────────────────
        st.subheader("📉 Rolling 3-Month Average Spend")
        fig_roll = go.Figure()
        fig_roll.add_trace(
            go.Bar(
                x=df["month_label"],
                y=df["total_spend"],
                name="Monthly Spend",
                marker_color="lightsteelblue",
            )
        )
        fig_roll.add_trace(
            go.Scatter(
                x=df["month_label"],
                y=df["rolling_3mo"],
                name="3-Mo Rolling Avg",
                line={"color": "#d62728", "width": 2},
                mode="lines+markers",
            )
        )
        fig_roll.update_layout(
            xaxis_title="Month",
            yaxis_title="Spend (₫)",
            xaxis_tickangle=-45,
            legend_title="Series",
            title="Monthly Spend with 3-Month Rolling Average",
        )
        st.plotly_chart(fig_roll, use_container_width=True)

        # ── Monthly Heatmap ────────────────────────────────────────────────
        st.subheader("🔥 Monthly Spend Heatmap")
        heatmap_pivot = df.pivot_table(
            index="yr", columns="mo", values="total_spend", aggfunc="sum"
        )
        mo_name_map = {i + 1: m for i, m in enumerate(month_names)}
        heatmap_pivot.columns = [mo_name_map[c] for c in heatmap_pivot.columns]
        heatmap_pivot.index = heatmap_pivot.index.astype(str)
        fig_heat = px.imshow(
            heatmap_pivot,
            color_continuous_scale="Blues",
            labels={"x": "Month", "y": "Year", "color": "Spend (₫)"},
            title="Spend Heatmap by Year × Month",
            aspect="auto",
            text_auto=".0f",
        )
        fig_heat.update_xaxes(side="top")
        st.plotly_chart(fig_heat, use_container_width=True)

except Exception as exc:
    st.error(f"Failed to load trend data: {exc}")

# ---------------------------------------------------------------------------
# Phase 5 ML placeholders (always visible)
# ---------------------------------------------------------------------------
st.markdown("---")
st.subheader("🤖 Spend Forecast (Phase 5)")
st.info(
    "ℹ️ **Coming in Phase 5 — Forecasting:** "
    "A Prophet/ARIMA model trained in "
    "`data_science/notebooks/02_forecasting.ipynb` will render a 3-month "
    "forward forecast with confidence bands here. The model output will be "
    "loaded from the `data_science/models/` directory and overlaid on the "
    "historical spend chart above."
)

st.subheader("🔍 Anomaly Detection (Phase 5)")
st.info(
    "ℹ️ **Coming in Phase 5 — Anomaly Detection:** "
    "Unusual transactions and spending spikes identified by the model in "
    "`data_science/notebooks/03_anomaly_detection.ipynb` will be highlighted "
    "in a flagged transaction table here."
)
