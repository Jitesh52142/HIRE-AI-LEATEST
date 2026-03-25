import pandas as pd
from io import StringIO

def fetch_google_sheet_data(sheet_url: str) -> pd.DataFrame:
    """
    Fetches data from a public Google Sheet URL and returns a pandas DataFrame.
    The URL must be in the format: https://docs.google.com/spreadsheets/d/SHEET_ID/edit?gid=GID
    """
    try:
        # Construct the CSV export URL
        csv_export_url = sheet_url.replace('/edit?gid=', '/export?format=csv&gid=')
        
        # Read the CSV data directly into a pandas DataFrame
        df = pd.read_csv(csv_export_url)
        
        # Replace NaN values with empty strings for better template rendering
        df.fillna('', inplace=True)
        
        return df
        
    except Exception as e:
        print(f"Error fetching Google Sheet data: {e}")
        # Return an empty DataFrame on error
        return pd.DataFrame()