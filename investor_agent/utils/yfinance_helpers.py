"""yfinance API helper functions."""

import logging
import sys
from typing import Literal

import pandas as pd
import yfinance as yf
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception,
    after_log,
)
from yfinance.exceptions import YFRateLimitError

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)


def api_retry(func):
    """Unified retry decorator for API calls (yfinance and HTTP).

    Retries on:
    - YFRateLimitError
    - HTTP 5xx errors
    - Network/connection issues
    - Rate limiting (429)
    """
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2.0, min=2.0, max=30.0),
        retry=retry_if_exception(
            lambda e: isinstance(e, YFRateLimitError)
            or (hasattr(e, "status_code") and getattr(e, "status_code", 0) >= 500)
            or any(
                term in str(e).lower()
                for term in [
                    "rate limit",
                    "too many requests",
                    "temporarily blocked",
                    "timeout",
                    "connection",
                    "network",
                    "temporary",
                    "5",
                    "429",
                    "502",
                    "503",
                    "504",
                ]
            )
        ),
        after=after_log(logger, logging.WARNING),
    )(func)


@api_retry
def yf_call(ticker: str, method: str, *args, **kwargs):
    """Generic yfinance API call with retry logic.

    Args:
        ticker: Stock ticker symbol
        method: Method name to call on yf.Ticker object
        *args: Positional arguments to pass to the method
        **kwargs: Keyword arguments to pass to the method

    Returns:
        Result of the yfinance method call
    """
    t = yf.Ticker(ticker)
    return getattr(t, method)(*args, **kwargs)


def get_options_chain(
    ticker: str, expiry: str, option_type: Literal["C", "P"] | None = None
) -> pd.DataFrame:
    """Get options chain with optional filtering by type.

    Args:
        ticker: Stock ticker symbol
        expiry: Expiration date
        option_type: Option type - "C" for calls, "P" for puts, None for both

    Returns:
        DataFrame with options chain data
    """
    chain = yf_call(ticker, "option_chain", expiry)

    if option_type == "C":
        return chain.calls
    elif option_type == "P":
        return chain.puts

    return pd.concat([chain.calls, chain.puts], ignore_index=True)
