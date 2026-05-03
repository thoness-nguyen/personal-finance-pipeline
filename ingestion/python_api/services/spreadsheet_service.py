# =============================================================================
# File: services/spreadsheet_service.py
# Purpose: Provides helper functions for uploading files to gcs.
#          Credentials are read from environment variables.
# =============================================================================

import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]

def get_gspread_client(credentials_path: str):
    creds = Credentials.from_service_account_file(credentials_path, scopes = SCOPES)
    return gspread.authorize(creds)

def fetch_sheet_data(sheet_id: str, worksheet_name: str, credentials_path: str) -> pd.DataFrame:
    client = get_gspread_client(credentials_path)
    worksheet = client.open_by_key(sheet_id).worksheet(worksheet_name)
    rows = worksheet.get_all_values()
    
    return pd.DataFrame(rows)

def save_to_csv(df: pd.DataFrame, output_path: str):
    df.to_csv(output_path, index=False, encoding="utf-8-sig")