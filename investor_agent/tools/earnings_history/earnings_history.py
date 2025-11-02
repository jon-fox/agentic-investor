"""Tool for fetching earnings history."""

import logging
import pandas as pd
import yfinance as yf
from typing import Dict, Any

from ..interfaces.tool import Tool, ToolResponse
from .models import EarningsHistoryInput, EarningsHistoryOutput

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


class EarningsHistoryTool(Tool):
    """Tool that fetches historical earnings data including estimates, actuals, and surprises."""
    
    name = "get_earnings_history"
    description = "Get historical earnings data including EPS estimates, actual results, and surprise percentages"
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

        earnings_history = yf_call(ticker, "get_earnings_history")
        if earnings_history is None or (isinstance(earnings_history, pd.DataFrame) and earnings_history.empty):
            raise ValueError(f"No earnings history data found for {ticker}")

        if isinstance(earnings_history, pd.DataFrame):
            earnings_history = earnings_history.head(input_data.max_entries)

        csv_data = to_clean_csv(earnings_history)
        
        output = EarningsHistoryOutput(earnings_data=csv_data)
        return ToolResponse.from_model(output)
