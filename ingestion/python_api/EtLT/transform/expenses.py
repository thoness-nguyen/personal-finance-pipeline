# =============================================================================
# File: cleaners/expenses.py
# Source: expenses (Transactions sheet)
# Contract: expose  clean(df: pd.DataFrame) -> pd.DataFrame
# =============================================================================

import pandas as pd


def clean(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        raise ValueError("Input DataFrame is empty or None.")

    # Promote first row to header if columns look like integer indices
    if all(
        isinstance(col, (int, float)) or str(col).replace(".", "", 1).isdigit()
        for col in df.columns
    ):
        df.columns = df.iloc[0]
        df = df[1:].reset_index(drop=True)

    # Normalize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
    )

    # Drop columns with a non-string name (e.g. NaN)
    df = df.loc[:, df.columns.notna()]

    print(f"[cleaner:expenses] columns after normalization: {df.columns.tolist()}")

    # Parse date; flag unparseable rows
    df["needs_cleaning"] = False
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df.loc[df["date"].isna(), "needs_cleaning"] = True

    # Coerce numeric columns; flag non-numeric rows
    for col in ("amount", "balance"):
        if col in df.columns:
            cleaned_col = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.replace(r"\((.*?)\)", r"-\1", regex=True)
            )
            df[col] = pd.to_numeric(cleaned_col, errors="coerce")
            df.loc[df[col].isna(), "needs_cleaning"] = True

    # Strip whitespace from string columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].apply(lambda v: v.strip() if isinstance(v, str) else v)

    # Fill missing description/note with empty string
    for col in ("description", "note"):
        if col in df.columns:
            df[col] = df[col].fillna("")

    # Tag source
    df["source_data"] = "python-api"

    # Drop columns that are internal spreadsheet artifacts
    df = df.drop(
        [
            "input", "output", "amount_balance",
            "total_expense_monthly", "total_extra_using", "total_renting_expense",
        ],
        axis=1,
        errors="ignore",
    )

    # Drop rows with no parseable date
    df = df.dropna(subset=["date"])

    return df
