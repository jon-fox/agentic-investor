"""Pydantic models for the Intraday Data tool."""

from pydantic import BaseModel, Field, ConfigDict

from ..interfaces.tool import BaseToolInput


class IntradayDataInput(BaseToolInput):
    """Input schema for Intraday Data tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"stock": "AAPL", "window": 200},
                {"stock": "TSLA", "window": 100},
            ]
        }
    )

    stock: str = Field(description="Stock ticker symbol (e.g., AAPL, TSLA)")
    window: int = Field(
        default=200, description="Number of 15-minute bars to fetch", ge=1, le=1000
    )


class IntradayDataOutput(BaseModel):
    """Output schema for Intraday Data tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "intraday_data": "timestamp,AAPL\n2024-10-31 09:30:00 EST,150.25\n2024-10-31 09:45:00 EST,150.50\n"
                }
            ]
        }
    )

    intraday_data: str = Field(
        description="CSV formatted 15-minute intraday price data in EST timezone or error message"
    )
