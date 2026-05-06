# =============================================================================
# Purpose: Provides helper functions for uploading files to gcs.
#          Credentials are read from environment variables.
# =============================================================================

from io import BytesIO
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]

def get_gspread_client(credentials_path: str):
    """Authenticate with Google Sheets API using service account credentials."""
    
    creds = Credentials.from_service_account_file(credentials_path, scopes = SCOPES)
    return gspread.authorize(creds)

def fetch_sheet_data(sheet_id: str, worksheet_name: str, credentials_path: str) -> pd.DataFrame:
    """Fetches data from a specified Google Sheets worksheet and returns it as a DataFrame."""
    
    client = get_gspread_client(credentials_path)
    worksheet = client.open_by_key(sheet_id).worksheet(worksheet_name)
    rows = worksheet.get_all_values()
    
    return pd.DataFrame(rows)

def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """
    Convert DataFrame into CSV bytes using memory buffer.

    Args:
        df: pandas DataFrame

    Returns:
        CSV file as raw bytes
    """
    
    if df is None or df.empty:
        raise ValueError("DataFrame is empty.")
    
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
    
    return csv_buffer.getvalue()
