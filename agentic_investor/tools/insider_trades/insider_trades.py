"""Tool for fetching insider trading data."""

import logging
import pandas as pd
from typing import Dict, Any

from agentic_investor.utils import validate_ticker, yf_call, to_clean_csv
from agentic_investor.interfaces.tool import Tool, ToolResponse
from agentic_investor.utils.logger import get_debug_logger
from .models import InsiderTradesInput, InsiderTradesOutput

logger = get_debug_logger(__name__)


class InsiderTradesTool(Tool):
    """Tool that fetches insider trading transactions."""

    name = "get_insider_trades"
    description = "Get recent insider trading activity including executive and director transactions: stock purchases, sales, option exercises, and other reportable transactions. Returns up to 100 recent trades with insider name, title, transaction type, share count, price per share, total value, and filing date. Use this when asked about insider buying/selling, whether executives are confident, if insiders are dumping stock, insider sentiment, Form 4 filings, C-suite transactions, or director activity. Heavy insider buying can signal confidence while selling may indicate concerns. Example: \"Are AAPL insiders buying?\" or \"Show me recent insider sales at TSLA\"."
    input_model = InsiderTradesInput
    output_model = InsiderTradesOutput

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "input": self.input_model.model_json_schema(),
            "output": self.output_model.model_json_schema(),
        }

    async def execute(self, input_data: InsiderTradesInput) -> ToolResponse:
        """Execute the insider trades tool.

        Args:
            input_data: The validated input for the tool

        Returns:
            A response containing insider trading data as CSV
        """
        ticker = validate_ticker(input_data.ticker)
        logger.debug(f"Fetching insider trades for {ticker}, max_trades: {input_data.max_trades}")

        trades = yf_call(ticker, "get_insider_transactions")
        if trades is None or (isinstance(trades, pd.DataFrame) and trades.empty):
            raise ValueError(f"No insider trading data found for {ticker}")

        if isinstance(trades, pd.DataFrame):
            trades = trades.head(input_data.max_trades)

        csv_data = to_clean_csv(trades)

        output = InsiderTradesOutput(trades_data=csv_data)
        return ToolResponse.from_model(output)
