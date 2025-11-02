"""Pydantic models for the Technical Indicators tool."""

from typing import Literal, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from agentic_investor.interfaces.tool import BaseToolInput


class TechnicalIndicatorsInput(BaseToolInput):
    """Input schema for Technical Indicators tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "ticker": "AAPL",
                    "indicator": "SMA",
                    "period": "1y",
                    "timeperiod": 14,
                },
                {
                    "ticker": "TSLA",
                    "indicator": "RSI",
                    "period": "6mo",
                    "timeperiod": 14,
                },
            ]
        }
    )

    ticker: str = Field(description="Stock ticker symbol (e.g., AAPL, TSLA)")
    indicator: Literal["SMA", "EMA", "RSI", "MACD", "BBANDS"] = Field(
        description="Technical indicator to calculate"
    )
    period: Literal["1mo", "3mo", "6mo", "1y", "2y", "5y"] = Field(
        default="1y", description="Time period for historical data"
    )
    timeperiod: int = Field(
        default=14, description="Time period for SMA, EMA, RSI, BBANDS", ge=1, le=200
    )
    fastperiod: int = Field(
        default=12, description="Fast EMA period for MACD", ge=1, le=200
    )
    slowperiod: int = Field(
        default=26, description="Slow EMA period for MACD", ge=1, le=200
    )
    signalperiod: int = Field(
        default=9, description="Signal line period for MACD", ge=1, le=200
    )
    nbdev: int = Field(
        default=2, description="Number of standard deviations for BBANDS", ge=1, le=10
    )
    matype: int = Field(
        default=0,
        description="MA type: 0=SMA, 1=EMA, 2=WMA, 3=DEMA, 4=TEMA, 5=TRIMA, 6=KAMA, 7=MAMA, 8=T3",
        ge=0,
        le=8,
    )
    num_results: int = Field(
        default=100, description="Number of recent results to return", ge=1, le=1000
    )


class TechnicalIndicatorsOutput(BaseModel):
    """Output schema for Technical Indicators tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "data": {
                        "price_data": "Date,Open,High,Low,Close,Volume\n2024-10-31,150.00,152.00,149.00,151.50,50000000\n",
                        "indicator_data": "Date,sma\n2024-10-31,150.25\n",
                    }
                }
            ]
        }
    )

    data: Dict[str, Any] = Field(
        description="Dictionary containing price_data and indicator_data as CSV strings, or error message"
    )
