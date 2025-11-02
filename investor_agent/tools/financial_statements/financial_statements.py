"""Tool for fetching financial statements."""

import logging
import pandas as pd
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception, after_log
from yfinance.exceptions import YFRateLimitError

from ..interfaces.tool import Tool, ToolResponse
from .models import FinancialStatementsInput, FinancialStatementsOutput

logger = logging.getLogger(__name__)


def validate_ticker(ticker: str) -> str:
    """Validate and normalize ticker symbol."""
    ticker = ticker.upper().strip()
    if not ticker:
        raise ValueError("Ticker symbol cannot be empty")
    return ticker


def api_retry(func):
    """Unified retry decorator for API calls."""
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


def to_clean_csv(df: pd.DataFrame) -> str:
    """Clean DataFrame by removing empty columns and convert to CSV string."""
    mask = (df.notna().any() & (df != '').any() &
            ((df != 0).any() | (df.dtypes == 'object')))
    return df.loc[:, mask].fillna('').to_csv(index=False)


class FinancialStatementsTool(Tool):
    """Tool that fetches financial statements (income, balance sheet, cash flow)."""
    
    name = "get_financial_statements"
    description = "Get financial statements including income statement, balance sheet, and cash flow statement with quarterly or annual frequency"
    input_model = FinancialStatementsInput
    output_model = FinancialStatementsOutput
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "input": self.input_model.model_json_schema(),
            "output": self.output_model.model_json_schema(),
        }
    
    async def execute(self, input_data: FinancialStatementsInput) -> ToolResponse:
        """Execute the financial statements tool.
        
        Args:
            input_data: The validated input for the tool
            
        Returns:
            A response containing financial statement data as CSV
        """
        ticker = validate_ticker(input_data.ticker)

        @api_retry
        def get_single_statement(stmt_type: str):
            t = yf.Ticker(ticker)
            if stmt_type == "income":
                return t.quarterly_income_stmt if input_data.frequency == "quarterly" else t.income_stmt
            elif stmt_type == "balance":
                return t.quarterly_balance_sheet if input_data.frequency == "quarterly" else t.balance_sheet
            else:  # cash
                return t.quarterly_cashflow if input_data.frequency == "quarterly" else t.cashflow

        # Fetch all requested statements in parallel
        with ThreadPoolExecutor() as executor:
            futures = {stmt_type: executor.submit(get_single_statement, stmt_type) for stmt_type in input_data.statement_types}

            results = {}
            for stmt_type, future in futures.items():
                df = future.result()
                if df is None or df.empty:
                    raise ValueError(f"No {stmt_type} statement data found for {ticker}")

                if len(df.columns) > input_data.max_periods:
                    df = df.iloc[:, :input_data.max_periods]

                df_reset = df.reset_index()
                results[stmt_type] = to_clean_csv(df_reset)

        output = FinancialStatementsOutput(statements=results)
        return ToolResponse.from_model(output)
