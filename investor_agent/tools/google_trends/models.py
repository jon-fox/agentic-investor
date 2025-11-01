"""Pydantic models for the Google Trends tool."""

from typing import List
from pydantic import BaseModel, Field, ConfigDict

from ..interfaces.tool import BaseToolInput


class GoogleTrendsInput(BaseToolInput):
    """Input schema for Google Trends tool."""
    
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"keywords": ["bitcoin", "ethereum"], "period_days": 7}]}
    )
    
    keywords: List[str] = Field(description="List of keywords to search for", examples=[["bitcoin", "ethereum"]])
    period_days: int = Field(default=7, description="Number of days to look back", examples=[7, 30, 90])


class GoogleTrendsOutput(BaseModel):
    """Output schema for Google Trends tool."""
    
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"trends_data": "date,bitcoin,ethereum\n2024-01-01,50,45\n"}]}
    )
    
    trends_data: str = Field(description="CSV formatted trends data with dates and search interest values")
