"""Tool for fetching CNN Fear & Greed Index."""

import logging
from typing import Dict, Any

from agentic_investor.utils import fetch_json, BROWSER_HEADERS
from agentic_investor.interfaces.tool import Tool, ToolResponse
from .models import CNNFearGreedInput, CNNFearGreedOutput

logger = logging.getLogger(__name__)


class CNNFearGreedTool(Tool):
    """Tool that fetches the CNN Fear & Greed Index and its indicators."""

    name = "get_cnn_fear_greed_index"
    description = "Get CNN Fear & Greed Index with various market sentiment indicators including VIX, put/call options, junk bond demand, and safe haven demand"
    input_model = CNNFearGreedInput
    output_model = CNNFearGreedOutput

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "input": self.input_model.model_json_schema(),
            "output": self.output_model.model_json_schema(),
        }

    async def execute(self, input_data: CNNFearGreedInput) -> ToolResponse:
        """Execute the CNN Fear & Greed Index tool.

        Args:
            input_data: The validated input for the tool

        Returns:
            A response containing the fear & greed index data
        """
        CNN_FEAR_GREED_URL = (
            "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
        )

        raw_data = await fetch_json(CNN_FEAR_GREED_URL, BROWSER_HEADERS)
        if not raw_data:
            raise ValueError("Empty response data")

        # Remove historical time series data arrays
        result = {
            k: (
                {
                    inner_k: inner_v
                    for inner_k, inner_v in v.items()
                    if inner_k != "data"
                }
                if isinstance(v, dict)
                else v
            )
            for k, v in raw_data.items()
            if k != "fear_and_greed_historical"
        }

        # Filter by indicators if specified
        if input_data.indicators:
            if invalid := set(input_data.indicators) - set(result.keys()):
                raise ValueError(
                    f"Invalid indicators: {list(invalid)}. Available: {list(result.keys())}"
                )
            result = {k: v for k, v in result.items() if k in input_data.indicators}

        output = CNNFearGreedOutput(data=result)
        return ToolResponse.from_model(output)
