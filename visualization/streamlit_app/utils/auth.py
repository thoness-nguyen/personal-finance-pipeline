# =============================================================================
# File: visualization/streamlit_app/utils/auth.py
# Purpose: Google OIDC login gate for the Streamlit dashboard. Restricts
#          access to a fixed allowlist of Google account email(s), since this
#          dashboard shows personal financial data.
#
#          Requires streamlit>=1.42 and an [auth] section in secrets.toml
#          (see .streamlit/secrets.toml.example).
# =============================================================================

import os

import streamlit as st


def _allowed_emails() -> set[str]:
    """Read the allowed Google account email(s) from env (comma-separated)."""
    raw = os.environ.get("ALLOWED_EMAILS", "")
    return {e.strip().lower() for e in raw.split(",") if e.strip()}


def require_login() -> None:
    """
    Gate the current page behind Google login.

    Must be called immediately after st.set_page_config(). Stops script
    execution until the user is authenticated with an allowlisted Google
    account.
    """
    if not st.user.is_logged_in:
        st.title("💰 Personal Finance Dashboard")
        st.info("This dashboard is private. Please log in with your Google account to continue.")
        st.button("Log in with Google", on_click=st.login)
        st.stop()

    allowed = _allowed_emails()
    if allowed and st.user.email.lower() not in allowed:
        st.error(f"Access denied for {st.user.email}. This dashboard is restricted to its owner.")
        st.button("Log out", on_click=st.logout)
        st.stop()

    st.sidebar.success(f"👤 {st.user.email}")
    st.sidebar.button("Log out", on_click=st.logout, key="logout_btn")
