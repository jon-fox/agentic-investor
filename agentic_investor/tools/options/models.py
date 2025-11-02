"""Pydantic models for the Options tool."""

from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

from agentic_investor.interfaces.tool import BaseToolInput


class OptionsInput(BaseToolInput):
    """Input schema for Options tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"ticker_symbol": "AAPL", "num_options": 10, "option_type": "C"},
                {
                    "ticker_symbol": "TSLA",
                    "num_options": 20,
                    "start_date": "2024-11-01",
                    "end_date": "2024-12-31",
                },
            ]
        }
    )

    ticker_symbol: str = Field(description="Stock ticker symbol (e.g., AAPL, TSLA)")
    num_options: int = Field(
        default=10, description="Number of options to return", ge=1, le=1000
    )
    start_date: Optional[str] = Field(
        default=None,
        description="Filter options expiring on or after this date (YYYY-MM-DD)",
    )
    end_date: Optional[str] = Field(
        default=None,
        description="Filter options expiring on or before this date (YYYY-MM-DD)",
    )
    strike_lower: Optional[float] = Field(
        default=None, description="Minimum strike price to include"
    )
    strike_upper: Optional[float] = Field(
        default=None, description="Maximum strike price to include"
    )
    option_type: Optional[Literal["C", "P"]] = Field(
        default=None, description="Option type: C for calls, P for puts, None for both"
    )


class OptionsOutput(BaseModel):
    """Output schema for Options tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "options_data": "strike,lastPrice,bid,ask,volume,openInterest,impliedVolatility,expiryDate\n150.00,5.25,5.20,5.30,1000,5000,0.25,2024-12-20\n"
                }
            ]
        }
    )

    options_data: str = Field(description="CSV formatted options chain data")
