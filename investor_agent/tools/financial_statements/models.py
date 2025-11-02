"""Pydantic models for the Financial Statements tool."""

from typing import List, Literal, Dict
from pydantic import BaseModel, Field, ConfigDict

from ..interfaces.tool import BaseToolInput


class FinancialStatementsInput(BaseToolInput):
    """Input schema for Financial Statements tool."""
    
    model_config = ConfigDict(
        json_schema_extra={"examples": [
            {"ticker": "AAPL", "statement_types": ["income"], "frequency": "quarterly", "max_periods": 8},
            {"ticker": "TSLA", "statement_types": ["income", "balance", "cash"], "frequency": "annual", "max_periods": 4}
        ]}
    )
    
    ticker: str = Field(description="Stock ticker symbol (e.g., AAPL, TSLA)")
    statement_types: List[Literal["income", "balance", "cash"]] = Field(
        default=["income"],
        description="Types of financial statements to retrieve"
    )
    frequency: Literal["quarterly", "annual"] = Field(
        default="quarterly",
        description="Reporting frequency"
    )
    max_periods: int = Field(
        default=8,
        description="Maximum number of periods to return",
        ge=1,
        le=20
    )


class FinancialStatementsOutput(BaseModel):
    """Output schema for Financial Statements tool."""
    
    model_config = ConfigDict(
        json_schema_extra={"examples": [{
            "statements": {
                "income": "Date,Revenue,NetIncome\n2024-Q3,100000000,25000000\n",
                "balance": "Date,TotalAssets,TotalLiabilities\n2024-Q3,500000000,200000000\n"
            }
        }]}
    )
    
    statements: Dict[str, str] = Field(description="Dictionary mapping statement type to CSV formatted data")
