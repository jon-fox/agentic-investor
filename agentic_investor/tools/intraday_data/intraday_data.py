"""Tool for fetching 15-minute intraday data using Alpaca API."""

import logging
from typing import Dict, Any

from agentic_investor.interfaces.tool import Tool, ToolResponse
from agentic_investor.utils.logger import get_debug_logger
from .models import IntradayDataInput, IntradayDataOutput

logger = get_debug_logger(__name__)


class IntradayDataTool(Tool):
    """Tool that fetches 15-minute historical stock bars using Alpaca API."""

    name = "fetch_intraday_data"
    description = "Fetch high-resolution 15-minute interval stock price data (bars) using Alpaca market data API. Returns timestamp and close price for each 15-minute period in EST timezone. Supports up to 1000 bars (roughly 10 trading days of intraday data). Use this when asked about intraday price action, today's trading pattern, minute-by-minute movement, recent price fluctuations, current session behavior, or short-term price trends. Perfect for day trading analysis, identifying intraday support/resistance, or examining recent volatility. Example: \"Show me TSLA's price movement today\" or \"What's the intraday chart for AAPL?\"."
    input_model = IntradayDataInput
    output_model = IntradayDataOutput

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "input": self.input_model.model_json_schema(),
            "output": self.output_model.model_json_schema(),
        }

    async def execute(self, input_data: IntradayDataInput) -> ToolResponse:
        """Execute the intraday data tool.

        Args:
            input_data: The validated input for the tool

        Returns:
            A response containing intraday data as CSV or error message
        """
        logger.debug(f"Fetching intraday data for {input_data.stock}, window: {input_data.window}")
        
        # Check if Alpaca is available
        try:
            from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
            from alpaca.data.historical import StockHistoricalDataClient
            from alpaca.data.requests import StockBarsRequest
        except ImportError:
            error_msg = "Alpaca API is not available. Please install alpaca-py package to use this tool: pip install alpaca-py"
            output = IntradayDataOutput(intraday_data=error_msg)
            return ToolResponse.from_model(output)

        import os

        try:
            api_key = os.getenv("ALPACA_API_KEY")
            api_secret = os.getenv("ALPACA_API_SECRET")

            if not api_key or not api_secret:
                raise ValueError(
                    "ALPACA_API_KEY and ALPACA_API_SECRET environment variables must be set"
                )

            timeframe = TimeFrame(15, TimeFrameUnit.Minute)
            client = StockHistoricalDataClient(api_key, api_secret)
            request = StockBarsRequest(
                symbol_or_symbols=input_data.stock,
                timeframe=timeframe,
                limit=input_data.window,
            )

            df_raw = client.get_stock_bars(request).df

            if df_raw.empty or "close" not in df_raw.columns:
                raise ValueError(
                    f"'close' column missing or data empty for {input_data.stock}"
                )

            df = df_raw["close"]
            df.index = df_raw.index.get_level_values("timestamp").tz_convert(
                "America/New_York"
            )
            df = df.to_frame(name=f"{input_data.stock}")

            # Convert to CSV string
            df_reset = df.reset_index()
            df_reset["timestamp"] = df_reset["timestamp"].dt.strftime(
                "%Y-%m-%d %H:%M:%S %Z"
            )
            csv_data = df_reset.to_csv(index=False)

            output = IntradayDataOutput(intraday_data=csv_data)
            return ToolResponse.from_model(output)

        except Exception as e:
            error_msg = f"Error fetching data for {input_data.stock}: {e}"
            output = IntradayDataOutput(intraday_data=error_msg)
            return ToolResponse.from_model(output)
