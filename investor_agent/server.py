import datetime
import logging
import sys
from concurrent.futures import ThreadPoolExecutor
from io import StringIO
from typing import Literal, Any

import httpx
import pandas as pd
import yfinance as yf
from hishel.httpx import AsyncCacheClient
from mcp.server.fastmcp import FastMCP
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception, after_log
from yfinance.exceptions import YFRateLimitError

from .services.tool_service import ToolService
from .tools.crypto_fear_greed import CryptoFearGreedTool
from .tools.google_trends import GoogleTrendsTool
from .tools.market_movers import MarketMoversTool
from .tools.cnn_fear_greed import CNNFearGreedTool
from .tools.ticker_data import TickerDataTool
from .tools.options import OptionsTool
from .tools.price_history import PriceHistoryTool
from .tools.financial_statements import FinancialStatementsTool
from .tools.earnings_history import EarningsHistoryTool
from .tools.insider_trades import InsiderTradesTool
from .tools.institutional_holders import InstitutionalHoldersTool
from .tools.nasdaq_earnings_calendar import NasdaqEarningsCalendarTool
from .tools.intraday_data import IntradayDataTool
from .tools.technical_indicators import TechnicalIndicatorsTool

mcp = FastMCP("Investor-Agent", dependencies=["yfinance", "pandas", "pytrends"])

# Initialize tool service and register tools
tool_service = ToolService()
tool_service.register_tools([
    CryptoFearGreedTool(),
    GoogleTrendsTool(),
    MarketMoversTool(),
    CNNFearGreedTool(),
    TickerDataTool(),
    OptionsTool(),
    PriceHistoryTool(),
    FinancialStatementsTool(),
    EarningsHistoryTool(),
    InsiderTradesTool(),
    InstitutionalHoldersTool(),
    NasdaqEarningsCalendarTool(),
    IntradayDataTool(),
    TechnicalIndicatorsTool(),
])

# Configure pandas
pd.set_option('future.no_silent_downcasting', True)

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)

# Minimal HTTP Headers - only essential ones
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Unified retry decorator for API calls (yfinance and HTTP)
def api_retry(func):
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2.0, min=2.0, max=30.0),
        retry=retry_if_exception(lambda e:
            isinstance(e, YFRateLimitError) or
            (hasattr(e, 'status_code') and getattr(e, 'status_code', 0) >= 500) or
            any(term in str(e).lower() for term in [
                "rate limit", "too many requests", "temporarily blocked",
                "timeout", "connection", "network", "temporary", "5", "429", "502", "503", "504"
            ])
        ),
        after=after_log(logger, logging.WARNING)
    )(func)

# HTTP client utility
def create_async_client(headers: dict | None = None) -> AsyncCacheClient:
    """Create a cached async HTTP client with longer timeout, automatic redirect and custom headers."""
    return AsyncCacheClient(
        timeout=30.0,
        follow_redirects=True,
        headers=headers,
    )

@api_retry
async def fetch_json(url: str, headers: dict | None = None) -> dict:
    """Generic JSON fetcher with retry logic."""
    async with create_async_client(headers=headers) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

@api_retry
async def fetch_text(url: str, headers: dict | None = None) -> str:
    """Generic text fetcher with retry logic."""
    async with create_async_client(headers=headers) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text

# Utility functions
def validate_ticker(ticker: str) -> str:
    ticker = ticker.upper().strip()
    if not ticker:
        raise ValueError("Ticker symbol cannot be empty")
    return ticker

def validate_date(date_str: str) -> datetime.date:
    """Validate and parse a date string in YYYY-MM-DD format."""
    try:
        return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")

def validate_date_range(start_str: str | None, end_str: str | None) -> None:
    start_date = None
    end_date = None

    if start_str:
        start_date = validate_date(start_str)
    if end_str:
        end_date = validate_date(end_str)

    if start_date and end_date and start_date > end_date:
        raise ValueError("start_date must be before or equal to end_date")

@api_retry
def yf_call(ticker: str, method: str, *args, **kwargs):
    """Generic yfinance API call with retry logic."""
    t = yf.Ticker(ticker)
    return getattr(t, method)(*args, **kwargs)

def get_options_chain(ticker: str, expiry: str, option_type: Literal["C", "P"] | None = None) -> pd.DataFrame:
    """Get options chain with optional filtering by type."""
    chain = yf_call(ticker, "option_chain", expiry)

    if option_type == "C":
        return chain.calls
    elif option_type == "P":
        return chain.puts

    return pd.concat([chain.calls, chain.puts], ignore_index=True)



def to_clean_csv(df: pd.DataFrame) -> str:
    """Clean DataFrame by removing empty columns and convert to CSV string."""
    # Chain operations more efficiently
    mask = (df.notna().any() & (df != '').any() &
            ((df != 0).any() | (df.dtypes == 'object')))
    return df.loc[:, mask].fillna('').to_csv(index=False)

def format_date_string(date_str: str) -> str | None:
    """Parse and format date string to YYYY-MM-DD format."""
    try:
        return datetime.datetime.fromisoformat(date_str.replace("Z", "")).strftime("%Y-%m-%d")
    except Exception:
        return date_str[:10] if date_str else None

# Google Trends timeframe mapping
TREND_TIMEFRAMES = {
    1: 'now 1-d', 7: 'now 7-d', 30: 'today 1-m',
    90: 'today 3-m', 365: 'today 12-m'
}

def get_trends_timeframe(days: int) -> str:
    """Get appropriate Google Trends timeframe for given days."""
    for max_days, timeframe in TREND_TIMEFRAMES.items():
        if days <= max_days:
            return timeframe
    return 'today 5-y'


# Register tools with MCP
tool_service.register_mcp_handlers(mcp)

if __name__ == "__main__":
    mcp.run()