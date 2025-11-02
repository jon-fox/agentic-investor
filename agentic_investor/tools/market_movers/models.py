"""Pydantic models for the Market Movers tool."""

from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

from agentic_investor.interfaces.tool import BaseToolInput


class MarketMoversInput(BaseToolInput):
    """Input schema for Market Movers tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"category": "most-active", "count": 25, "market_session": "regular"},
                {"category": "gainers", "count": 10, "market_session": "regular"},
            ]
        }
    )

    category: Literal["gainers", "losers", "most-active"] = Field(
        default="most-active", description="Category of market movers to fetch"
    )
    count: int = Field(
        default=25, description="Number of stocks to return (1-100)", ge=1, le=100
    )
    market_session: Literal["regular", "pre-market", "after-hours"] = Field(
        default="regular",
        description="Market session (only applies to 'most-active' category)",
    )


class MarketMoversOutput(BaseModel):
    """Output schema for Market Movers tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "movers_data": "Symbol,Name,Price,Change,%Change\nAAPL,Apple Inc.,150.00,+2.50,+1.69%\n"
                }
            ]
        }
    )

    movers_data: str = Field(description="CSV formatted market movers data")
