"""Pydantic models for the Nasdaq Earnings Calendar tool."""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from agentic_investor.interfaces.tool import BaseToolInput


class NasdaqEarningsCalendarInput(BaseToolInput):
    """Input schema for Nasdaq Earnings Calendar tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"date": None, "limit": 100},
                {"date": "2024-11-01", "limit": 50},
            ]
        }
    )

    date: Optional[str] = Field(
        default=None,
        description="Date for earnings calendar in YYYY-MM-DD format. Defaults to today if not provided.",
    )
    limit: int = Field(
        default=100,
        description="Maximum number of earnings entries to return",
        ge=1,
        le=500,
    )


class NasdaqEarningsCalendarOutput(BaseModel):
    """Output schema for Nasdaq Earnings Calendar tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "earnings_data": "Date,Symbol,Company,EPS Estimate,EPS Actual,Surprise %\n2024-11-01,AAPL,Apple Inc.,1.50,1.55,+3.33%\n"
                }
            ]
        }
    )

    earnings_data: str = Field(
        description="CSV formatted earnings calendar data or error/info message"
    )
