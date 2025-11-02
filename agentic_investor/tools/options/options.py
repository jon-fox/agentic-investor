"""Tool for fetching options chain data."""

import logging
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Literal
import datetime

from agentic_investor.utils import (
    validate_ticker,
    validate_date,
    validate_date_range,
    get_options_chain,
    to_clean_csv,
)
from agentic_investor.interfaces.tool import Tool, ToolResponse
from agentic_investor.utils.logger import get_debug_logger
from .models import OptionsInput, OptionsOutput

logger = get_debug_logger(__name__)


class OptionsTool(Tool):
    """Tool that fetches options chain data with filtering capabilities."""

    name = "get_options"
    description = "Retrieve options chain data including strike prices, expiration dates, bid/ask spreads, implied volatility, open interest, trading volume, and Greeks (delta, gamma, theta, vega) for both call and put options. Use this when asked about options strategies, checking option premiums, evaluating covered calls, analyzing protective puts, finding strike prices, assessing derivatives positions, volatility trading opportunities, or options expiring soon. Supports flexible filtering by strike price range, expiration date window (start/end dates), and option type (calls only, puts only, or both). Returns up to 1000 contracts per query. Example usage: AAPL calls expiring in 30 days, TSLA puts near current price."
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
        logger.debug(f"Fetching options chain for {input_data.ticker_symbol}, expiration={input_data.expiration_date}")
        ticker_symbol = validate_ticker(input_data.ticker_symbol)

        try:
            # Validate dates
            validate_date_range(input_data.start_date, input_data.end_date)

            # Get options expirations - this is a property, not a method
            import yfinance as yf

            t = yf.Ticker(ticker_symbol)
            expirations = t.options
            if not expirations:
                raise ValueError(f"No options available for {ticker_symbol}")

            # Filter by date
            valid_expirations = [
                exp
                for exp in expirations
                if (
                    (not input_data.start_date or exp >= input_data.start_date)
                    and (not input_data.end_date or exp <= input_data.end_date)
                )
            ]

            if not valid_expirations:
                raise ValueError(
                    f"No options found for {ticker_symbol} within specified date range"
                )

            # Parallel fetch with error handling
            with ThreadPoolExecutor() as executor:
                chains = [
                    chain.assign(expiryDate=expiry)
                    for chain, expiry in zip(
                        executor.map(
                            lambda exp: get_options_chain(
                                ticker_symbol, exp, input_data.option_type
                            ),
                            valid_expirations,
                        ),
                        valid_expirations,
                    )
                    if chain is not None
                ]

            if not chains:
                raise ValueError(
                    f"No options found for {ticker_symbol} matching criteria"
                )

            df = pd.concat(chains, ignore_index=True)

            # Apply strike filters
            if input_data.strike_lower is not None:
                df = df[df["strike"] >= input_data.strike_lower]
            if input_data.strike_upper is not None:
                df = df[df["strike"] <= input_data.strike_upper]

            df = df.sort_values(["openInterest", "volume"], ascending=[False, False])
            df_subset = df.head(input_data.num_options)
            csv_data = to_clean_csv(df_subset)

            output = OptionsOutput(options_data=csv_data)
            return ToolResponse.from_model(output)

        except Exception as e:
            raise ValueError(f"Failed to retrieve options data: {str(e)}")
