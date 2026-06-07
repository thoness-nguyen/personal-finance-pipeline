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

def fetch_sheet_data(sheet_id: str, worksheet_name: str, credentials_path: str, as_type: str = "dataframe"):
    """Fetches data from a specified Google Sheets worksheet and returns it as a DataFrame."""
    
    client = get_gspread_client(credentials_path)
    worksheet = client.open_by_key(sheet_id).worksheet(worksheet_name)
    rows = worksheet.get_all_values()

    if not rows:
        if as_type == "dataframe":
            return pd.DataFrame()
        elif as_type == "list":
            return []
        else:
            return rows

    # Use first row as column headers (matches Node.js behaviour)
    header, *data = rows
    
    data = [row for row in data if any(cell.strip() for cell in row)]
    
    if as_type == "dataframe":
        df = pd.DataFrame(data, columns=header)
        return df
    elif as_type == "list":
        return [dict(zip(header, row)) for row in data]
    else:
        return rows

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
