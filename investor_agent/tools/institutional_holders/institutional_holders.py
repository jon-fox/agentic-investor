"""Tool for fetching institutional and mutual fund holders."""

import logging
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any

from ...utils import validate_ticker, yf_call, to_clean_csv
from ..interfaces.tool import Tool, ToolResponse
from .models import InstitutionalHoldersInput, InstitutionalHoldersOutput

logger = logging.getLogger(__name__)


class InstitutionalHoldersTool(Tool):
    """Tool that fetches major institutional and mutual fund holders."""
    
    name = "get_institutional_holders"
    description = "Get major institutional and mutual fund holders with their share positions"
    input_model = InstitutionalHoldersInput
    output_model = InstitutionalHoldersOutput
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "input": self.input_model.model_json_schema(),
            "output": self.output_model.model_json_schema(),
        }
    
    async def execute(self, input_data: InstitutionalHoldersInput) -> ToolResponse:
        """Execute the institutional holders tool.
        
        Args:
            input_data: The validated input for the tool
            
        Returns:
            A response containing institutional and mutual fund holder data
        """
        ticker = validate_ticker(input_data.ticker)

        # Fetch both types in parallel
        with ThreadPoolExecutor() as executor:
            inst_future = executor.submit(yf_call, ticker, "get_institutional_holders")
            fund_future = executor.submit(yf_call, ticker, "get_mutualfund_holders")

            inst_holders = inst_future.result()
            fund_holders = fund_future.result()

        # Limit results
        inst_holders = inst_holders.head(input_data.top_n) if isinstance(inst_holders, pd.DataFrame) else None
        fund_holders = fund_holders.head(input_data.top_n) if isinstance(fund_holders, pd.DataFrame) else None

        if (inst_holders is None or inst_holders.empty) and (fund_holders is None or fund_holders.empty):
            raise ValueError(f"No institutional holder data found for {ticker}")

        result = {"ticker": ticker, "top_n": input_data.top_n}

        if inst_holders is not None and not inst_holders.empty:
            result["institutional_holders"] = to_clean_csv(inst_holders)

        if fund_holders is not None and not fund_holders.empty:
            result["mutual_fund_holders"] = to_clean_csv(fund_holders)

        output = InstitutionalHoldersOutput(data=result)
        return ToolResponse.from_model(output)
