"""Pydantic models for the Price History tool."""

from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

from agentic_investor.interfaces.tool import BaseToolInput


class PriceHistoryInput(BaseToolInput):
    """Input schema for Price History tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"ticker": "AAPL", "period": "1mo"},
                {"ticker": "TSLA", "period": "1y"},
            ]
        }
    )

    ticker: str = Field(description="Stock ticker symbol (e.g., AAPL, TSLA)")
    period: Literal[
        "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
    ] = Field(default="1mo", description="Time period for historical data")


class PriceHistoryOutput(BaseModel):
    """Output schema for Price History tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "price_data": "Date,Open,High,Low,Close,Volume\n2024-10-01,150.00,152.00,149.00,151.50,50000000\n"
                }
            ]
        }
    )

    price_data: str = Field(
        description="CSV formatted historical OHLCV (Open, High, Low, Close, Volume) data"
    )
