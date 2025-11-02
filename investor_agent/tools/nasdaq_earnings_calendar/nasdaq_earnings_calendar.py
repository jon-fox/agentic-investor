"""Tool for fetching Nasdaq earnings calendar."""

import logging
import pandas as pd
import datetime
from typing import Dict, Any

from ..interfaces.tool import Tool, ToolResponse
from .models import NasdaqEarningsCalendarInput, NasdaqEarningsCalendarOutput

logger = logging.getLogger(__name__)


def validate_date(date_str: str) -> datetime.date:
    """Validate and parse a date string in YYYY-MM-DD format."""
    try:
        return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")


async def fetch_json(url: str, headers: dict | None = None) -> dict:
    """Generic JSON fetcher with retry logic."""
    from hishel.httpx import AsyncCacheClient
    
    async_client = AsyncCacheClient(
        timeout=30.0,
        follow_redirects=True,
        headers=headers,
    )
    async with async_client as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


def to_clean_csv(df: pd.DataFrame) -> str:
    """Clean DataFrame by removing empty columns and convert to CSV string."""
    mask = (df.notna().any() & (df != '').any() &
            ((df != 0).any() | (df.dtypes == 'object')))
    return df.loc[:, mask].fillna('').to_csv(index=False)


class NasdaqEarningsCalendarTool(Tool):
    """Tool that fetches earnings calendar for a specific date from Nasdaq API."""
    
    name = "get_nasdaq_earnings_calendar"
    description = "Get earnings calendar for a specific date using Nasdaq API. Returns company earnings dates, EPS estimates, and surprises."
    input_model = NasdaqEarningsCalendarInput
    output_model = NasdaqEarningsCalendarOutput
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "input": self.input_model.model_json_schema(),
            "output": self.output_model.model_json_schema(),
        }
    
    async def execute(self, input_data: NasdaqEarningsCalendarInput) -> ToolResponse:
        """Execute the nasdaq earnings calendar tool.
        
        Args:
            input_data: The validated input for the tool
            
        Returns:
            A response containing earnings calendar data as CSV or info message
        """
        # Constants
        NASDAQ_EARNINGS_URL = "https://api.nasdaq.com/api/calendar/earnings"
        BROWSER_HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        NASDAQ_HEADERS = {
            **BROWSER_HEADERS,
            'Referer': 'https://www.nasdaq.com/'
        }

        # Set default date if not provided or validate provided date
        today = datetime.date.today()
        target_date = validate_date(input_data.date) if input_data.date else today

        date_str = target_date.strftime('%Y-%m-%d')
        url = f"{NASDAQ_EARNINGS_URL}?date={date_str}"

        try:
            logger.info(f"Fetching earnings for {date_str}")

            data = await fetch_json(url, NASDAQ_HEADERS)

            if 'data' in data and data['data']:
                earnings_data = data['data']

                if earnings_data.get('headers') and earnings_data.get('rows'):
                    headers = earnings_data['headers']
                    rows = earnings_data['rows']

                    # Extract column names from headers dict
                    if isinstance(headers, dict):
                        column_names = list(headers.values())
                        column_keys = list(headers.keys())
                    else:
                        column_names = [h.get('label', h) if isinstance(h, dict) else str(h) for h in headers]
                        column_keys = column_names

                    # Convert rows to DataFrame
                    processed_rows = []
                    for row in rows:
                        if isinstance(row, dict):
                            processed_row = [row.get(key, '') for key in column_keys]
                            processed_rows.append(processed_row)

                    if processed_rows:
                        df = pd.DataFrame(processed_rows, columns=column_names)
                        # Add date column at the beginning
                        df.insert(0, 'Date', date_str)

                        # Apply limit
                        if len(df) > input_data.limit:
                            df = df.head(input_data.limit)

                        logger.info(f"Retrieved {len(df)} earnings entries for {date_str}")
                        csv_data = to_clean_csv(df)
                        
                        output = NasdaqEarningsCalendarOutput(earnings_data=csv_data)
                        return ToolResponse.from_model(output)

            # No earnings data found
            result_str = f"No earnings announcements found for {date_str}. This could be due to weekends, holidays, or no scheduled earnings on this date."
            output = NasdaqEarningsCalendarOutput(earnings_data=result_str)
            return ToolResponse.from_model(output)

        except Exception as e:
            logger.error(f"Error fetching earnings for {date_str}: {e}")
            error_str = f"Error retrieving earnings data for {date_str}: {str(e)}"
            output = NasdaqEarningsCalendarOutput(earnings_data=error_str)
            return ToolResponse.from_model(output)
