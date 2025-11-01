"""Tool for fetching Google Trends data."""

import logging
import pandas as pd
from typing import Dict, Any

from ..interfaces.tool import Tool, ToolResponse
from .models import GoogleTrendsInput, GoogleTrendsOutput

logger = logging.getLogger(__name__)


def to_clean_csv(df: pd.DataFrame) -> str:
    """Convert DataFrame to clean CSV string."""
    return df.to_csv(index=False)


def get_trends_timeframe(days: int) -> str:
    """Convert days to Google Trends timeframe string."""
    if days <= 1:
        return 'now 1-d'
    elif days <= 7:
        return 'now 7-d'
    elif days <= 30:
        return 'today 1-m'
    elif days <= 90:
        return 'today 3-m'
    else:
        # Find the best match among discrete options
        for threshold, timeframe in [(365 * 5, 'today 5-y'), (365, 'today 12-m')]:
            if days <= threshold:
                return timeframe
    return 'today 5-y'


class GoogleTrendsTool(Tool):
    """Tool that fetches Google Trends relative search interest data."""
    
    name = "get_google_trends"
    description = "Get Google Trends relative search interest for specified keywords"
    input_model = GoogleTrendsInput
    output_model = GoogleTrendsOutput
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "input": self.input_model.model_json_schema(),
            "output": self.output_model.model_json_schema(),
        }
    
    async def execute(self, input_data: GoogleTrendsInput) -> ToolResponse:
        """Execute the Google Trends tool.
        
        Args:
            input_data: The validated input for the tool
            
        Returns:
            A response containing the trends data as CSV
        """
        from pytrends.request import TrendReq

        logger.info(f"Fetching Google Trends data for {input_data.period_days} days")

        timeframe = get_trends_timeframe(input_data.period_days)
        pytrends = TrendReq(hl='en-US', tz=360)
        pytrends.build_payload(input_data.keywords, timeframe=timeframe)

        df = pytrends.interest_over_time()
        if df.empty:
            raise ValueError("No data returned from Google Trends")

        # Clean and format data
        if 'isPartial' in df.columns:
            df = df[~df['isPartial']].drop('isPartial', axis=1)

        df_reset = df.reset_index()
        csv_data = to_clean_csv(df_reset)
        
        output = GoogleTrendsOutput(trends_data=csv_data)
        return ToolResponse.from_model(output)
