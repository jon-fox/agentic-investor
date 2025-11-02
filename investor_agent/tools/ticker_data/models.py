"""Pydantic models for the Ticker Data tool."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

from ..interfaces.tool import BaseToolInput


class TickerDataInput(BaseToolInput):
    """Input schema for Ticker Data tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "ticker": "AAPL",
                    "max_news": 5,
                    "max_recommendations": 5,
                    "max_upgrades": 5,
                }
            ]
        }
    )

    ticker: str = Field(description="Stock ticker symbol (e.g., AAPL, TSLA)")
    max_news: int = Field(
        default=5, description="Maximum number of news items to return", ge=1, le=50
    )
    max_recommendations: int = Field(
        default=5,
        description="Maximum number of recommendations to return",
        ge=1,
        le=50,
    )
    max_upgrades: int = Field(
        default=5,
        description="Maximum number of upgrade/downgrade entries to return",
        ge=1,
        le=50,
    )


class TickerDataOutput(BaseModel):
    """Output schema for Ticker Data tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "data": {
                        "basic_info": [{"metric": "symbol", "value": "AAPL"}],
                        "calendar": [{"event": "earnings_date", "value": "2024-11-01"}],
                        "news": [
                            {
                                "date": "2024-10-31",
                                "title": "Apple releases earnings",
                                "source": "Reuters",
                                "url": "https://...",
                            }
                        ],
                    }
                }
            ]
        }
    )

    data: Dict[str, Any] = Field(
        description="Comprehensive ticker data including basic info, calendar, news, recommendations, and upgrades/downgrades"
    )
