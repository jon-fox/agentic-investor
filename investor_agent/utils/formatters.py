"""Data formatting utility functions."""

import datetime
import pandas as pd


def to_clean_csv(df: pd.DataFrame) -> str:
    """Clean DataFrame by removing empty columns and convert to CSV string.
    
    Removes columns that are:
    - All NaN values
    - All empty strings
    - All zeros (except for object/string columns)
    
    Args:
        df: DataFrame to clean and convert
        
    Returns:
        CSV string representation of the cleaned DataFrame
    """
    # Chain operations more efficiently
    mask = (df.notna().any() & (df != '').any() &
            ((df != 0).any() | (df.dtypes == 'object')))
    return df.loc[:, mask].fillna('').to_csv(index=False)


def format_date_string(date_str: str) -> str | None:
    """Parse and format date string to YYYY-MM-DD format.
    
    Handles ISO format dates with timezone info.
    
    Args:
        date_str: Date string to format
        
    Returns:
        Formatted date string in YYYY-MM-DD format, or None if parsing fails
    """
    try:
        return datetime.datetime.fromisoformat(date_str.replace("Z", "")).strftime("%Y-%m-%d")
    except Exception:
        return date_str[:10] if date_str else None
