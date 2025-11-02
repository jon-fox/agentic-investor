"""Tool for fetching options chain data."""

import logging
import pandas as pd
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Literal
import datetime

from ..interfaces.tool import Tool, ToolResponse
from .models import OptionsInput, OptionsOutput

logger = logging.getLogger(__name__)


def validate_ticker(ticker: str) -> str:
    """Validate and normalize ticker symbol."""
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
    """Validate date range."""
    start_date = None
    end_date = None

    if start_str:
        start_date = validate_date(start_str)
    if end_str:
        end_date = validate_date(end_str)

    if start_date and end_date and start_date > end_date:
        raise ValueError("start_date must be before or equal to end_date")


def get_options_chain(ticker: str, expiry: str, option_type: Literal["C", "P"] | None = None) -> pd.DataFrame:
    """Get options chain with optional filtering by type."""
    t = yf.Ticker(ticker)
    chain = t.option_chain(expiry)

    if option_type == "C":
        return chain.calls
    elif option_type == "P":
        return chain.puts

    return pd.concat([chain.calls, chain.puts], ignore_index=True)


def to_clean_csv(df: pd.DataFrame) -> str:
    """Clean DataFrame by removing empty columns and convert to CSV string."""
    mask = (df.notna().any() & (df != '').any() &
            ((df != 0).any() | (df.dtypes == 'object')))
    return df.loc[:, mask].fillna('').to_csv(index=False)


class OptionsTool(Tool):
    """Tool that fetches options chain data with filtering capabilities."""
    
    name = "get_options"
    description = "Get options chain data with filtering by expiration date, strike price, and option type (calls/puts)"
    input_model = OptionsInput
    output_model = OptionsOutput
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "input": self.input_model.model_json_schema(),
            "output": self.output_model.model_json_schema(),
        }
    
    async def execute(self, input_data: OptionsInput) -> ToolResponse:
        """Execute the options tool.
        
        Args:
            input_data: The validated input for the tool
            
        Returns:
            A response containing options chain data as CSV
        """
        ticker_symbol = validate_ticker(input_data.ticker_symbol)

        try:
            # Validate dates
            validate_date_range(input_data.start_date, input_data.end_date)

            # Get options expirations - this is a property, not a method
            t = yf.Ticker(ticker_symbol)
            expirations = t.options
            if not expirations:
                raise ValueError(f"No options available for {ticker_symbol}")

            # Filter by date
            valid_expirations = [
                exp for exp in expirations
                if ((not input_data.start_date or exp >= input_data.start_date) and
                    (not input_data.end_date or exp <= input_data.end_date))
            ]

            if not valid_expirations:
                raise ValueError(f"No options found for {ticker_symbol} within specified date range")

            # Parallel fetch with error handling
            with ThreadPoolExecutor() as executor:
                chains = [
                    chain.assign(expiryDate=expiry)
                    for chain, expiry in zip(
                        executor.map(lambda exp: get_options_chain(ticker_symbol, exp, input_data.option_type), valid_expirations),
                        valid_expirations
                    ) if chain is not None
                ]

            if not chains:
                raise ValueError(f"No options found for {ticker_symbol} matching criteria")

            df = pd.concat(chains, ignore_index=True)

            # Apply strike filters
            if input_data.strike_lower is not None:
                df = df[df['strike'] >= input_data.strike_lower]
            if input_data.strike_upper is not None:
                df = df[df['strike'] <= input_data.strike_upper]

            df = df.sort_values(['openInterest', 'volume'], ascending=[False, False])
            df_subset = df.head(input_data.num_options)
            csv_data = to_clean_csv(df_subset)

            output = OptionsOutput(options_data=csv_data)
            return ToolResponse.from_model(output)

        except Exception as e:
            raise ValueError(f"Failed to retrieve options data: {str(e)}")
