"""Pydantic models for the CNN Fear & Greed Index tool."""

from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from ..interfaces.tool import BaseToolInput


class CNNFearGreedInput(BaseToolInput):
    """Input schema for CNN Fear & Greed Index tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"indicators": None},
                {"indicators": ["fear_and_greed", "market_volatility_vix"]},
            ]
        }
    )

    indicators: Optional[
        List[
            Literal[
                "fear_and_greed",
                "fear_and_greed_historical",
                "put_call_options",
                "market_volatility_vix",
                "market_volatility_vix_50",
                "junk_bond_demand",
                "safe_haven_demand",
            ]
        ]
    ] = Field(
        default=None,
        description="List of specific indicators to return. If None, returns all indicators.",
    )


class CNNFearGreedOutput(BaseModel):
    """Output schema for CNN Fear & Greed Index tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "data": {
                        "fear_and_greed": {"score": 50, "rating": "Neutral"},
                        "market_volatility_vix": {"score": 30, "rating": "Greed"},
                    }
                }
            ]
        }
    )

    data: Dict[str, Any] = Field(
        description="Fear & Greed index data for requested indicators"
    )
