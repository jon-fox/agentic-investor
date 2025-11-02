"""Tool for fetching 15-minute intraday data using Alpaca API."""

import logging
from typing import Dict, Any

from ..interfaces.tool import Tool, ToolResponse
from .models import IntradayDataInput, IntradayDataOutput

logger = logging.getLogger(__name__)


class IntradayDataTool(Tool):
    """Tool that fetches 15-minute historical stock bars using Alpaca API."""

    name = "fetch_intraday_data"
    description = "Fetch 15-minute historical stock bars using Alpaca API. Returns timestamp and close price data in EST timezone."
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
