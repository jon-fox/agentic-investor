"""Tool for fetching comprehensive ticker data."""

import logging
import pandas as pd
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any

from ..interfaces.tool import Tool, ToolResponse
from .models import TickerDataInput, TickerDataOutput

logger = logging.getLogger(__name__)


def validate_ticker(ticker: str) -> str:
    """Validate and normalize ticker symbol."""
    ticker = ticker.upper().strip()
    if not ticker:
        raise ValueError("Ticker symbol cannot be empty")
    return ticker


def yf_call(ticker: str, method: str, *args, **kwargs):
    """Generic yfinance API call."""
    t = yf.Ticker(ticker)
    return getattr(t, method)(*args, **kwargs)


def format_date_string(date_str: str) -> str | None:
    """Parse and format date string to YYYY-MM-DD format."""
    import datetime
    try:
        return datetime.datetime.fromisoformat(date_str.replace("Z", "")).strftime("%Y-%m-%d")
    except Exception:
        return date_str[:10] if date_str else None


def to_clean_csv(df: pd.DataFrame) -> str:
    """Clean DataFrame by removing empty columns and convert to CSV string."""
    mask = (df.notna().any() & (df != '').any() &
            ((df != 0).any() | (df.dtypes == 'object')))
    return df.loc[:, mask].fillna('').to_csv(index=False)


class TickerDataTool(Tool):
    """Tool that fetches comprehensive ticker data including metrics, calendar, news, and recommendations."""
    
    name = "get_ticker_data"
    description = "Get comprehensive ticker data including basic metrics, earnings calendar, recent news, analyst recommendations, and upgrades/downgrades"
    input_model = TickerDataInput
    output_model = TickerDataOutput
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "input": self.input_model.model_json_schema(),
            "output": self.output_model.model_json_schema(),
        }
    
    async def execute(self, input_data: TickerDataInput) -> ToolResponse:
        """Execute the ticker data tool.
        
        Args:
            input_data: The validated input for the tool
            
        Returns:
            A response containing comprehensive ticker data
        """
        ticker = validate_ticker(input_data.ticker)

        # Get all basic data in parallel
        with ThreadPoolExecutor() as executor:
            info_future = executor.submit(yf_call, ticker, "get_info")
            calendar_future = executor.submit(yf_call, ticker, "get_calendar")
            news_future = executor.submit(yf_call, ticker, "get_news")

            info = info_future.result()
            if not info:
                raise ValueError(f"No information available for {ticker}")

            essential_fields = {
                'symbol', 'longName', 'currentPrice', 'marketCap', 'volume', 'trailingPE',
                'forwardPE', 'dividendYield', 'beta', 'eps', 'totalRevenue', 'totalDebt',
                'profitMargins', 'operatingMargins', 'returnOnEquity', 'returnOnAssets',
                'revenueGrowth', 'earningsGrowth', 'bookValue', 'priceToBook',
                'enterpriseValue', 'pegRatio', 'trailingEps', 'forwardEps'
            }

            # Basic info section - convert to structured format
            basic_info = [
                {"metric": key, "value": value.isoformat() if hasattr(value, 'isoformat') else value}
                for key, value in info.items() if key in essential_fields
            ]

            result: dict[str, Any] = {"basic_info": basic_info}

            # Process calendar
            calendar = calendar_future.result()
            if calendar:
                result["calendar"] = [
                    {"event": key, "value": value.isoformat() if hasattr(value, 'isoformat') else value}
                    for key, value in calendar.items()
                ]

            # Process news
            news_items = news_future.result()
            if news_items:
                news_items = news_items[:input_data.max_news]  # Apply limit
                news_data = []
                for item in news_items:
                    content = item.get("content", {})
                    raw_date = content.get("pubDate") or content.get("displayTime") or ""

                    news_data.append({
                        "date": format_date_string(raw_date),
                        "title": content.get("title") or "Untitled",
                        "source": content.get("provider", {}).get("displayName", "Unknown"),
                        "url": (content.get("canonicalUrl", {}).get("url") or
                                content.get("clickThroughUrl", {}).get("url") or "")
                    })

                result["news"] = news_data

        # Get recommendations and upgrades in parallel
        with ThreadPoolExecutor() as executor:
            recommendations_future = executor.submit(yf_call, ticker, "get_recommendations")
            upgrades_future = executor.submit(yf_call, ticker, "get_upgrades_downgrades")

            recommendations = recommendations_future.result()
            if isinstance(recommendations, pd.DataFrame) and not recommendations.empty:
                result["recommendations"] = to_clean_csv(recommendations.head(input_data.max_recommendations))

            upgrades = upgrades_future.result()
            if isinstance(upgrades, pd.DataFrame) and not upgrades.empty:
                upgrades = upgrades.sort_index(ascending=False) if hasattr(upgrades, 'sort_index') else upgrades
                result["upgrades_downgrades"] = to_clean_csv(upgrades.head(input_data.max_upgrades))

        output = TickerDataOutput(data=result)
        return ToolResponse.from_model(output)
