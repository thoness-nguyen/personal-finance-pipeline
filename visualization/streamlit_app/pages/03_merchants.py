# =============================================================================
# File: visualization/streamlit_app/pages/03_merchants.py
# Purpose: Top merchants — bar chart, sortable data table, category filter.
#          Reads from mart_top_merchants (dbt mart table only).
# =============================================================================

from datetime import date

import plotly.express as px
import streamlit as st

from utils.auth import require_login
from utils.db_connector import query_df

st.set_page_config(page_title="Merchants", page_icon="🏪", layout="wide")

require_login()

# ---------------------------------------------------------------------------
# Sidebar – date range + controls
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

st.sidebar.markdown("---")
top_n = st.sidebar.slider("Top N merchants", min_value=5, max_value=30, value=10, step=5)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300)
def load_merchant_data(start_date: str, end_date: str):
    return query_df(
        f"""
        SELECT merchant, category_name, spending_type, visit_count,
               total_spend, first_seen, last_seen
        FROM mart_top_merchants
        WHERE last_seen BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY total_spend DESC
        """
    )


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------
st.title("🏪 Top Merchants")
st.markdown("Your most-visited and highest-spend merchants.")

try:
    df = load_merchant_data(str(date_start), str(date_end))

    if df.empty:
        st.info("No merchant data found for the selected date range.")
    else:
        # Category filter in sidebar
        all_categories = sorted(df["category_name"].dropna().unique().tolist())
        selected_cats = st.sidebar.multiselect(
            "Filter by Category",
            options=all_categories,
            default=all_categories,
        )

        filtered = df[df["category_name"].isin(selected_cats)].head(top_n)

        if filtered.empty:
            st.info("No data for the selected filters.")
        else:
            # Bar chart – top N merchants by spend
            st.subheader(f"Top {top_n} Merchants by Spend")
            fig = px.bar(
                filtered.sort_values("total_spend"),
                x="total_spend",
                y="merchant",
                orientation="h",
                color="category_name",
                labels={
                    "total_spend": "Total Spend (₫)",
                    "merchant": "Merchant",
                    "category_name": "Category",
                },
                title=f"Top {top_n} Merchants",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"}, legend_title="Category")
            st.plotly_chart(fig, use_container_width=True)

            # Sortable data table
            st.subheader("Merchant Details")
            table_df = filtered[
                ["merchant", "category_name", "spending_type", "visit_count",
                 "total_spend", "first_seen", "last_seen"]
            ].copy()
            table_df.columns = [
                "Merchant", "Category", "Type", "Visits",
                "Total Spend (₫)", "First Seen", "Last Seen",
            ]
            st.dataframe(
                table_df.style.format({"Total Spend (₫)": "{:,.0f}"}),
                use_container_width=True,
            )

except Exception as exc:
    st.error(f"Failed to load merchant data: {exc}")
