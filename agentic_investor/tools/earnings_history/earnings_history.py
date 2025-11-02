"""Tool for fetching earnings history."""

import logging
import pandas as pd
from typing import Dict, Any

from agentic_investor.utils import validate_ticker, yf_call, to_clean_csv
from agentic_investor.interfaces.tool import Tool, ToolResponse
from agentic_investor.utils.logger import get_debug_logger
from .models import EarningsHistoryInput, EarningsHistoryOutput

logger = get_debug_logger(__name__)


class EarningsHistoryTool(Tool):
    """Tool that fetches historical earnings data including estimates, actuals, and surprises."""

    name = "get_earnings_history"
    description = "Get historical quarterly earnings results including EPS estimates (analyst consensus), actual reported EPS, earnings surprise amounts and percentages, and earnings announcement dates. Returns up to 50 historical earnings reports. Use this when asked about earnings beats/misses, earnings surprise history, quarterly results trends, how often a company beats estimates, earnings consistency, EPS growth trajectory, or past earnings performance. Helps identify companies that consistently beat/miss expectations. Example: \"Has NVDA been beating earnings?\" or \"Show me TSLA's earnings surprise history\"."
    input_model = EarningsHistoryInput
    output_model = EarningsHistoryOutput

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "input": self.input_model.model_json_schema(),
            "output": self.output_model.model_json_schema(),
        }

    async def execute(self, input_data: EarningsHistoryInput) -> ToolResponse:
        """Execute the earnings history tool.

        Args:
            input_data: The validated input for the tool

        Returns:
            A response containing earnings history data as CSV
        """
        ticker = validate_ticker(input_data.ticker)
        logger.debug(f"Fetching earnings history for {ticker}, max_entries: {input_data.max_entries}")

        earnings_history = yf_call(ticker, "get_earnings_history")
        if earnings_history is None or (
            isinstance(earnings_history, pd.DataFrame) and earnings_history.empty
        ):
            raise ValueError(f"No earnings history data found for {ticker}")

        if isinstance(earnings_history, pd.DataFrame):
            earnings_history = earnings_history.head(input_data.max_entries)

        csv_data = to_clean_csv(earnings_history)

        output = EarningsHistoryOutput(earnings_data=csv_data)
        return ToolResponse.from_model(output)
