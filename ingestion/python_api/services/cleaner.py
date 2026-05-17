# =============================================================================
# Purpose: Provides data-cleaning utilities for expense DataFrames.
#          Normalises column names, handles missing values, parses dates,
#          and flags rows that need manual review.
# =============================================================================

import pandas as pd
import numpy as np

def clean_expenses(df: pd.DataFrame):
    if df is None or df.empty:
        raise ValueError("Input DataFrame is empty or None.")
    
    # Set headers:
    if all(isinstance(col, (int, float)) or str(col).replace('.', '', 1).isdigit() for col in df.columns):
        df.columns = df.iloc[0]
        df = df[1:]
        df = df.reset_index(drop=True)
    
    # Vectorized string operations to clean up headers
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
    )
    
    # Drop any column whose name is not a string
    df = df.loc[:, df.columns.notna()]
    
    print(f"[cleaner] columns after normalization: {df.columns.tolist()}")
    
    # Parse and validate date
    df["needs_cleaning"] = False
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df.loc[df["date"].isna(), "needs_cleaning"] = True
    
    # Coerce amount to numeric; flag non-numeric rows with needs_cleaning=True.
    for col in ("amount", "balance"):
        if col in df.columns:
            cleaned = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.replace(r"\((.*?)\)", r"-\1", regex=True)
            )
            df[col] = pd.to_numeric(cleaned, errors="coerce")
            df.loc[df[col].isna(), "needs_cleaning"] = True
    
    # Strip whitespace from string columns only (exclude numeric/datetime/bool)
    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        df[col] = df[col].apply(lambda v: v.strip() if isinstance(v, str) else v)

    # Fill missing description/notes with empty string
    for col in ("description", "note"):
        if col in df.columns:
            df[col] = df[col].fillna("")

    # Add source api
    df["source_data"] = "python-api"

    # Drop unused columns
    df = df.drop(
        ["input", "output", "amount_balance", "note",
        "total_expense_monthly", "total_extra_using", "total_renting_expense"],
        axis=1,
        errors="ignore",
    )

    df = df.dropna(subset=["date"])

    return df
