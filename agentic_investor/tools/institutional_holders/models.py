"""Pydantic models for the Institutional Holders tool."""

from typing import Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from agentic_investor.interfaces.tool import BaseToolInput


class InstitutionalHoldersInput(BaseToolInput):
    """Input schema for Institutional Holders tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"ticker": "AAPL", "top_n": 20},
                {"ticker": "TSLA", "top_n": 10},
            ]
        }
    )

    ticker: str = Field(description="Stock ticker symbol (e.g., AAPL, TSLA)")
    top_n: int = Field(
        default=20, description="Number of top holders to return", ge=1, le=100
    )


class InstitutionalHoldersOutput(BaseModel):
    """Output schema for Institutional Holders tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "data": {
                        "ticker": "AAPL",
                        "top_n": 20,
                        "institutional_holders": "Holder,Shares,Value\nVanguard,100000000,$15000000000\n",
                        "mutual_fund_holders": "Holder,Shares,Value\nFidelity,50000000,$7500000000\n",
                    }
                }
            ]
        }
    )

    data: Dict[str, Any] = Field(
        description="Dictionary containing ticker, top_n, and holder data as CSV"
    )
