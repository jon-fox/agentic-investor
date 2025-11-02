"""Pydantic models for the Earnings History tool."""

from pydantic import BaseModel, Field, ConfigDict

from ..interfaces.tool import BaseToolInput


class EarningsHistoryInput(BaseToolInput):
    """Input schema for Earnings History tool."""
    
    model_config = ConfigDict(
        json_schema_extra={"examples": [
            {"ticker": "AAPL", "max_entries": 8},
            {"ticker": "TSLA", "max_entries": 12}
        ]}
    )
    
    ticker: str = Field(description="Stock ticker symbol (e.g., AAPL, TSLA)")
    max_entries: int = Field(default=8, description="Maximum number of earnings entries to return", ge=1, le=50)


class EarningsHistoryOutput(BaseModel):
    """Output schema for Earnings History tool."""
    
    model_config = ConfigDict(
        json_schema_extra={"examples": [{
            "earnings_data": "Date,EPS Estimate,EPS Actual,Surprise\n2024-10-31,1.50,1.55,+3.33%\n"
        }]}
    )
    
    earnings_data: str = Field(description="CSV formatted earnings history data")
