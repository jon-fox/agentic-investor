"""Pydantic models for the Crypto Fear & Greed Index tool."""

from pydantic import BaseModel, Field, ConfigDict

from ..interfaces.tool import BaseToolInput


class CryptoFearGreedInput(BaseToolInput):
    """Input schema for Crypto Fear & Greed Index tool."""
    pass  # No inputs required


class CryptoFearGreedOutput(BaseModel):
    """Output schema for Crypto Fear & Greed Index tool."""
    
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"value": "50", "classification": "Neutral", "timestamp": "1698710400"}]}
    )
    
    value: str = Field(description="The fear & greed index value (0-100)")
    classification: str = Field(description="Classification of the index (e.g., Fear, Greed, Neutral)")
    timestamp: str = Field(description="Unix timestamp of the data")
