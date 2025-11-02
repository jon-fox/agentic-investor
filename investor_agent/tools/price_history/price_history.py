"""Tool for fetching historical price data."""

import logging
import pandas as pd
import yfinance as yf
from typing import Dict, Any

from ..interfaces.tool import Tool, ToolResponse
from .models import PriceHistoryInput, PriceHistoryOutput

logger = logging.getLogger(__name__)


def validate_ticker(ticker: str) -> str:
    """Validate and normalize ticker symbol."""
    ticker = ticker.upper().strip()
    if not ticker:
        raise ValueError("Ticker symbol cannot be empty")
    return ticker


def yf_call(ticker: str, method: str, *args, **kwargs):
    """Generic yfinance API call."""
    t = yf.Ticker(ticker)
    return getattr(t, method)(*args, **kwargs)


def to_clean_csv(df: pd.DataFrame) -> str:
    """Clean DataFrame by removing empty columns and convert to CSV string."""
    mask = (df.notna().any() & (df != '').any() &
            ((df != 0).any() | (df.dtypes == 'object')))
    return df.loc[:, mask].fillna('').to_csv(index=False)


class PriceHistoryTool(Tool):
    """Tool that fetches historical OHLCV price data for stocks."""
    
    name = "get_price_history"
    description = "Get historical OHLCV (Open, High, Low, Close, Volume) price data for a stock with smart interval selection"
    input_model = PriceHistoryInput
    output_model = PriceHistoryOutput
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "input": self.input_model.model_json_schema(),
            "output": self.output_model.model_json_schema(),
        }
    
    async def execute(self, input_data: PriceHistoryInput) -> ToolResponse:
        """Execute the price history tool.
        
        Args:
            input_data: The validated input for the tool
            
        Returns:
            A response containing historical price data as CSV
        """
        ticker = validate_ticker(input_data.ticker)

        interval = "1mo" if input_data.period in ["2y", "5y", "10y", "max"] else "1d"
        history = yf_call(ticker, "history", period=input_data.period, interval=interval)
        if history is None or history.empty:
            raise ValueError(f"No historical data found for {ticker}")

        # Reset index to include dates as a column
        history_with_dates = history.reset_index()
        history_with_dates['Date'] = pd.to_datetime(history_with_dates['Date']).dt.strftime('%Y-%m-%d')

        csv_data = to_clean_csv(history_with_dates)
        
        output = PriceHistoryOutput(price_data=csv_data)
        return ToolResponse.from_model(output)
