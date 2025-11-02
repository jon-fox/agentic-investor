"""Tool for calculating technical indicators using TA-Lib."""

import logging
import pandas as pd
from typing import Dict, Any

from ...utils import validate_ticker, yf_call, to_clean_csv
from ..interfaces.tool import Tool, ToolResponse
from .models import TechnicalIndicatorsInput, TechnicalIndicatorsOutput

logger = logging.getLogger(__name__)


class TechnicalIndicatorsTool(Tool):
    """Tool that calculates technical indicators using TA-Lib."""

    name = "calculate_technical_indicator"
    description = "Calculate technical indicators (SMA, EMA, RSI, MACD, BBANDS) for stock analysis using TA-Lib"
    input_model = TechnicalIndicatorsInput
    output_model = TechnicalIndicatorsOutput

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "input": self.input_model.model_json_schema(),
            "output": self.output_model.model_json_schema(),
        }

    async def execute(self, input_data: TechnicalIndicatorsInput) -> ToolResponse:
        """Execute the technical indicators tool.

        Args:
            input_data: The validated input for the tool

        Returns:
            A response containing price and indicator data or error message
        """
        # Check if TA-Lib is available
        try:
            import talib
            from talib import MA_Type
            import numpy as np
        except ImportError:
            error_msg = "TA-Lib is not available. Please install TA-Lib to use this tool. See: https://github.com/mrjbq7/ta-lib#installation"
            output = TechnicalIndicatorsOutput(data={"error": error_msg})
            return ToolResponse.from_model(output)

        try:
            ticker = validate_ticker(input_data.ticker)

            history = yf_call(
                ticker, "history", period=input_data.period, interval="1d"
            )
            if history is None or history.empty or "Close" not in history.columns:
                raise ValueError(f"No valid historical data found for {ticker}")

            close_prices = history["Close"].values
            min_required = {
                "SMA": input_data.timeperiod,
                "EMA": input_data.timeperiod * 2,
                "RSI": input_data.timeperiod + 1,
                "MACD": input_data.slowperiod + input_data.signalperiod,
                "BBANDS": input_data.timeperiod,
            }.get(input_data.indicator, input_data.timeperiod)

            if len(close_prices) < min_required:
                raise ValueError(
                    f"Insufficient data for {input_data.indicator} ({len(close_prices)} points, need {min_required})"
                )

            # Calculate indicators using mapping
            indicator_funcs = {
                "SMA": lambda: {
                    "sma": talib.SMA(close_prices, timeperiod=input_data.timeperiod)
                },
                "EMA": lambda: {
                    "ema": talib.EMA(close_prices, timeperiod=input_data.timeperiod)
                },
                "RSI": lambda: {
                    "rsi": talib.RSI(close_prices, timeperiod=input_data.timeperiod)
                },
                "MACD": lambda: dict(
                    zip(
                        ["macd", "signal", "histogram"],
                        talib.MACD(
                            close_prices,
                            fastperiod=input_data.fastperiod,
                            slowperiod=input_data.slowperiod,
                            signalperiod=input_data.signalperiod,
                        ),
                    )
                ),
                "BBANDS": lambda: dict(
                    zip(
                        ["upper_band", "middle_band", "lower_band"],
                        talib.BBANDS(
                            close_prices,
                            timeperiod=input_data.timeperiod,
                            nbdevup=input_data.nbdev,
                            nbdevdn=input_data.nbdev,
                            matype=MA_Type(input_data.matype),
                        ),
                    )
                ),
            }
            indicator_values = indicator_funcs[input_data.indicator]()

            # Limit results to num_results
            if input_data.num_results > 0:
                history = history.tail(input_data.num_results)

            # Reset index to show dates as a column
            price_df = history.reset_index()
            price_df["Date"] = pd.to_datetime(price_df["Date"]).dt.strftime("%Y-%m-%d")

            # Create indicator DataFrame with same date range
            indicator_rows = []
            for i, date in enumerate(price_df["Date"]):
                row = {"Date": date}
                for name, values in indicator_values.items():
                    # Get the corresponding value for this date
                    slice_values = (
                        values[-input_data.num_results :]
                        if input_data.num_results > 0
                        else values
                    )

                    if i < len(slice_values):
                        val = slice_values[i]
                        row[name] = f"{val:.4f}" if not np.isnan(val) else "N/A"
                    else:
                        row[name] = "N/A"
                indicator_rows.append(row)

            indicator_df = pd.DataFrame(indicator_rows)

            result = {
                "price_data": to_clean_csv(price_df),
                "indicator_data": to_clean_csv(indicator_df),
            }

            output = TechnicalIndicatorsOutput(data=result)
            return ToolResponse.from_model(output)

        except Exception as e:
            error_msg = (
                f"Error calculating {input_data.indicator} for {input_data.ticker}: {e}"
            )
            output = TechnicalIndicatorsOutput(data={"error": error_msg})
            return ToolResponse.from_model(output)
