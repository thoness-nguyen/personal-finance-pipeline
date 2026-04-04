# =============================================================================
# File: services/cleaner.py
# Purpose: Provides data-cleaning utilities for expense DataFrames.
#          Normalises column names, handles missing values, parses dates,
#          and flags rows that need manual review.
# =============================================================================

# TODO: import pandas as pd


def clean_expenses(df):
    """
    Clean and normalise an expense DataFrame.

    Args:
        df: Raw pandas DataFrame loaded from a CSV/Excel upload.

    Returns:
        Cleaned pandas DataFrame ready for GCS upload and DB insertion.

    TODO: Standardise column names to snake_case.
    TODO: Parse and validate the expense_date column.
    TODO: Strip whitespace from string columns.
    TODO: Coerce amount to numeric; flag non-numeric rows with needs_cleaning=True.
    TODO: Fill missing description/notes with empty string.
    TODO: Drop fully duplicate rows.
    TODO: Add source column defaulting to 'python-api'.
    TODO: Return the cleaned DataFrame.
    """
    # TODO: Implement cleaning logic
    raise NotImplementedError("clean_expenses is not yet implemented")
