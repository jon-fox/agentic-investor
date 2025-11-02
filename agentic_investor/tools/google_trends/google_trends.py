"""Tool for fetching Google Trends data."""

import logging
import pandas as pd
from typing import Dict, Any

from agentic_investor.utils import to_clean_csv
from agentic_investor.interfaces.tool import Tool, ToolResponse
from agentic_investor.utils.logger import get_debug_logger
from .models import GoogleTrendsInput, GoogleTrendsOutput

logger = get_debug_logger(__name__)

# Google Trends timeframe mapping
TREND_TIMEFRAMES = {
    1: "now 1-d",
    7: "now 7-d",
    30: "today 1-m",
    90: "today 3-m",
    365: "today 12-m",
}


def get_trends_timeframe(days: int) -> str:
    """Get appropriate Google Trends timeframe for given days."""
    for max_days, timeframe in TREND_TIMEFRAMES.items():
        if days <= max_days:
            return timeframe
    return "today 5-y"


class GoogleTrendsTool(Tool):
    """Tool that fetches Google Trends relative search interest data."""

    name = "get_google_trends"
    description = "Get relative search interest data from Google Trends for specified keywords over customizable time periods (7, 30, 90+ days). Returns normalized interest scores (0-100) showing search popularity trends. Use this when asked about public interest trends, search volume comparisons, trending topics, brand awareness over time, seasonal patterns, or correlation between search interest and stock movements. Example keywords: \"bitcoin\", \"Tesla earnings\", \"inflation\", \"recession\"."
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

        logger.debug(f"Fetching Google Trends for keywords: {input_data.keywords}, period: {input_data.period_days} days")

        timeframe = get_trends_timeframe(input_data.period_days)
        logger.debug(f"Using Google Trends timeframe: {timeframe}")
        pytrends = TrendReq(hl="en-US", tz=360)
        pytrends.build_payload(input_data.keywords, timeframe=timeframe)

        df = pytrends.interest_over_time()
        if df.empty:
            raise ValueError("No data returned from Google Trends")

        # Clean and format data
        if "isPartial" in df.columns:
            df = df[~df["isPartial"]].drop("isPartial", axis=1)

        df_reset = df.reset_index()
        csv_data = to_clean_csv(df_reset)

        output = GoogleTrendsOutput(trends_data=csv_data)
        return ToolResponse.from_model(output)
