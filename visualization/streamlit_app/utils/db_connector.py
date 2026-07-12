# =============================================================================
# File: visualization/streamlit_app/utils/db_connector.py
# Purpose: Provides a SQLAlchemy engine factory for connecting to the MySQL
#          finance_db database. Connection parameters are read from environment
#          variables so that no credentials are hard-coded.
# =============================================================================

import os

import pandas as pd
from dotenv import find_dotenv, load_dotenv
from sqlalchemy import create_engine, text

# Search up the directory tree for the nearest .env file
load_dotenv(find_dotenv(usecwd=True))


def get_engine():
    """
    Create and return a SQLAlchemy engine connected to finance_db.

    Required env vars: MYSQL_USER, MYSQL_PASSWORD
    Optional env vars (with defaults): MYSQL_HOST (localhost), MYSQL_PORT (3307),
                                       MYSQL_DATABASE (finance_db)
    Optional TLS env vars (for connecting over the public internet, e.g. from
    Streamlit Community Cloud to a home-hosted MySQL exposed via port-forward):
      MYSQL_REQUIRE_SSL=true   — encrypt the connection (best-effort, no CA check)
      MYSQL_SSL_CA=/path/to/ca.pem — encrypt AND verify against a trusted CA

    When running locally (outside Docker) set MYSQL_HOST=localhost.
    Inside Docker the service name 'mysql' is used automatically.
    """
    user = os.environ["MYSQL_USER"]
    password = os.environ["MYSQL_PASSWORD"]
    host = os.environ.get("MYSQL_HOST", "localhost")
    port = os.environ.get("MYSQL_PORT", "3307")
    database = os.environ.get("MYSQL_DATABASE", "finance_db")

    # MYSQL_PORT in .env is the HOST-mapped port (for connecting from outside
    # Docker). When talking to the 'mysql' service over the Docker network,
    # the container's actual listening port (3306) must be used instead.
    if host == "mysql":
        port = "3306"

    ssl_ca = os.environ.get("MYSQL_SSL_CA")
    require_ssl = os.environ.get("MYSQL_REQUIRE_SSL", "false").lower() in ("1", "true", "yes")
    connect_args = {}
    if ssl_ca:
        connect_args["ssl"] = {"ca": ssl_ca}
    elif require_ssl:
        connect_args["ssl"] = {}

    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    return create_engine(url, pool_pre_ping=True, connect_args=connect_args)


def query_df(sql: str) -> pd.DataFrame:
    """
    Execute a read-only SQL query and return the results as a DataFrame.

    Only query mart_ views — never raw tables.

    Args:
        sql: SQL string to execute.

    Returns:
        pd.DataFrame containing the query results.
    """
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)
