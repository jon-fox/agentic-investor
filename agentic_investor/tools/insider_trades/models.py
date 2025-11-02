"""Pydantic models for the Insider Trades tool."""

from pydantic import BaseModel, Field, ConfigDict

from agentic_investor.interfaces.tool import BaseToolInput


class InsiderTradesInput(BaseToolInput):
    """Input schema for Insider Trades tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"ticker": "AAPL", "max_trades": 20},
                {"ticker": "TSLA", "max_trades": 50},
            ]
        }
    )

    ticker: str = Field(description="Stock ticker symbol (e.g., AAPL, TSLA)")
    max_trades: int = Field(
        default=20,
        description="Maximum number of insider trades to return",
        ge=1,
        le=100,
    )


class InsiderTradesOutput(BaseModel):
    """Output schema for Insider Trades tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "trades_data": "Date,Insider,Transaction,Shares,Value\n2024-10-31,John Smith,Sale,10000,$1500000\n"
                }
            ]
        }
    )

    trades_data: str = Field(description="CSV formatted insider trading data")
