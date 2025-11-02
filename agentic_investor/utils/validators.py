"""Validation utility functions."""

import datetime


def validate_ticker(ticker: str) -> str:
    """Validate and normalize ticker symbol.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Normalized ticker in uppercase

    Raises:
        ValueError: If ticker is empty
    """
    ticker = ticker.upper().strip()
    if not ticker:
        raise ValueError("Ticker symbol cannot be empty")
    return ticker


def validate_date(date_str: str) -> datetime.date:
    """Validate and parse a date string in YYYY-MM-DD format.

    Args:
        date_str: Date string in YYYY-MM-DD format

    Returns:
        Parsed date object

    Raises:
        ValueError: If date format is invalid
    """
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")


def validate_date_range(start_str: str | None, end_str: str | None) -> None:
    """Validate a date range.

    Args:
        start_str: Start date string in YYYY-MM-DD format (optional)
        end_str: End date string in YYYY-MM-DD format (optional)

    Raises:
        ValueError: If start date is after end date
    """
    start_date = None
    end_date = None

    if start_str:
        start_date = validate_date(start_str)
    if end_str:
        end_date = validate_date(end_str)

    if start_date and end_date and start_date > end_date:
        raise ValueError("start_date must be before or equal to end_date")
