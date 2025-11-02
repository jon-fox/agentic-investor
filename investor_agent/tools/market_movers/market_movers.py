"""Tool for fetching market movers data."""

import logging
import pandas as pd
from io import StringIO
from typing import Dict, Any

from ..interfaces.tool import Tool, ToolResponse
from .models import MarketMoversInput, MarketMoversOutput

logger = logging.getLogger(__name__)


async def fetch_text(url: str, headers: dict | None = None) -> str:
    """Generic text fetcher with retry logic."""
    from hishel.httpx import AsyncCacheClient
    
    async_client = AsyncCacheClient(
        timeout=30.0,
        follow_redirects=True,
        headers=headers,
    )
    async with async_client as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text


def to_clean_csv(df: pd.DataFrame) -> str:
    """Clean DataFrame by removing empty columns and convert to CSV string."""
    mask = (df.notna().any() & (df != '').any() &
            ((df != 0).any() | (df.dtypes == 'object')))
    return df.loc[:, mask].fillna('').to_csv(index=False)


class MarketMoversTool(Tool):
    """Tool that fetches market movers (gainers, losers, most active)."""
    
    name = "get_market_movers"
    description = "Get market movers including gainers, losers, and most active stocks. Supports different market sessions."
    input_model = MarketMoversInput
    output_model = MarketMoversOutput
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "input": self.input_model.model_json_schema(),
            "output": self.output_model.model_json_schema(),
        }
    
    async def execute(self, input_data: MarketMoversInput) -> ToolResponse:
        """Execute the market movers tool.
        
        Args:
            input_data: The validated input for the tool
            
        Returns:
            A response containing the market movers data as CSV
        """
        # URLs for different market movers categories
        YAHOO_MOST_ACTIVE_URL = "https://finance.yahoo.com/most-active"
        YAHOO_PRE_MARKET_URL = "https://finance.yahoo.com/markets/stocks/pre-market"
        YAHOO_AFTER_HOURS_URL = "https://finance.yahoo.com/markets/stocks/after-hours"
        YAHOO_GAINERS_URL = "https://finance.yahoo.com/gainers"
        YAHOO_LOSERS_URL = "https://finance.yahoo.com/losers"
        
        BROWSER_HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        # Validate and constrain count
        count = min(max(input_data.count, 1), 100)

        # Build URLs with direct lookups to avoid dictionary recreation
        params = f"?count={count}&offset=0"

        if input_data.category == "most-active":
            if input_data.market_session == "regular":
                url = YAHOO_MOST_ACTIVE_URL + params
            elif input_data.market_session == "pre-market":
                url = YAHOO_PRE_MARKET_URL + params
            elif input_data.market_session == "after-hours":
                url = YAHOO_AFTER_HOURS_URL + params
            else:
                raise ValueError(f"Invalid market session: {input_data.market_session}")
        elif input_data.category == "gainers":
            url = YAHOO_GAINERS_URL + params
        elif input_data.category == "losers":
            url = YAHOO_LOSERS_URL + params
        else:
            raise ValueError(f"Invalid category: {input_data.category}")

        logger.info(f"Fetching {input_data.category} ({input_data.market_session} session) from: {url}")
        response_text = await fetch_text(url, BROWSER_HEADERS)
        tables = pd.read_html(StringIO(response_text))
        if not tables or tables[0].empty:
            raise ValueError(f"No data found for {input_data.category}")

        df = tables[0].loc[:, ~tables[0].columns.str.contains('^Unnamed')]
        csv_data = to_clean_csv(df.head(count))
        
        output = MarketMoversOutput(movers_data=csv_data)
        return ToolResponse.from_model(output)
