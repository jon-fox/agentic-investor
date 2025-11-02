"""Tool for fetching Crypto Fear & Greed Index."""

import logging
from typing import Dict, Any

from ...utils import fetch_json
from ..interfaces.tool import Tool, ToolResponse
from .models import CryptoFearGreedInput, CryptoFearGreedOutput

logger = logging.getLogger(__name__)


class CryptoFearGreedTool(Tool):
    """Tool that fetches the current Crypto Fear & Greed Index."""
    
    name = "get_crypto_fear_greed_index"
    description = "Get the current Crypto Fear & Greed Index from alternative.me API"
    input_model = CryptoFearGreedInput
    output_model = CryptoFearGreedOutput
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "input": self.input_model.model_json_schema(),
            "output": self.output_model.model_json_schema(),
        }
    
    async def execute(self, input_data: CryptoFearGreedInput) -> ToolResponse:
        """Execute the crypto fear & greed index tool.
        
        Args:
            input_data: The validated input for the tool
            
        Returns:
            A response containing the index data
        """
        CRYPTO_FEAR_GREED_URL = "https://api.alternative.me/fng/"

        data = await fetch_json(CRYPTO_FEAR_GREED_URL)
        if "data" not in data or not data["data"]:
            raise ValueError("Invalid response format from alternative.me API")

        current_data = data["data"][0]
        output = CryptoFearGreedOutput(
            value=current_data["value"],
            classification=current_data["value_classification"],
            timestamp=current_data["timestamp"]
        )
        return ToolResponse.from_model(output)
