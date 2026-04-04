# =============================================================================
# File: visualization/streamlit_app/utils/db_connector.py
# Purpose: Provides a SQLAlchemy engine factory for connecting to the MySQL
#          finance_db database. Connection parameters are read from environment
#          variables so that no credentials are hard-coded.
# =============================================================================

import os

# TODO: from sqlalchemy import create_engine
# TODO: from dotenv import load_dotenv


def get_engine():
    """
    Create and return a SQLAlchemy engine connected to finance_db.

    Returns:
        sqlalchemy.engine.Engine configured for the MySQL database.

    TODO: load_dotenv() to populate environment variables.
    TODO: Read MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE
          from environment.
    TODO: Build connection string:
          mysql+pymysql://{user}:{password}@{host}:{port}/{database}
    TODO: Return create_engine(connection_string, pool_pre_ping=True).
    """
    # TODO: Implement database connection
    raise NotImplementedError("get_engine is not yet implemented")
