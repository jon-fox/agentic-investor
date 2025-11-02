"""Tool for fetching insider trading data."""

import logging
import pandas as pd
import yfinance as yf
from typing import Dict, Any

from ..interfaces.tool import Tool, ToolResponse
from .models import InsiderTradesInput, InsiderTradesOutput

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


class InsiderTradesTool(Tool):
    """Tool that fetches insider trading transactions."""
    
    name = "get_insider_trades"
    description = "Get insider trading transactions including buys, sells, and other transactions by company insiders"
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

        trades = yf_call(ticker, "get_insider_transactions")
        if trades is None or (isinstance(trades, pd.DataFrame) and trades.empty):
            raise ValueError(f"No insider trading data found for {ticker}")

        if isinstance(trades, pd.DataFrame):
            trades = trades.head(input_data.max_trades)

        csv_data = to_clean_csv(trades)
        
        output = InsiderTradesOutput(trades_data=csv_data)
        return ToolResponse.from_model(output)
