"""Tool for fetching Crypto Fear & Greed Index."""

import logging
from typing import Dict, Any

from agentic_investor.utils import fetch_json
from agentic_investor.interfaces.tool import Tool, ToolResponse
from agentic_investor.utils.logger import get_debug_logger
from .models import CryptoFearGreedInput, CryptoFearGreedOutput

logger = get_debug_logger(__name__)


class CryptoFearGreedTool(Tool):
    """Tool that fetches the current Crypto Fear & Greed Index."""

    name = "get_crypto_fear_greed_index"
    description = "Get the current Crypto Fear & Greed Index (0-100 scale) from Alternative.me, indicating cryptocurrency market sentiment where 0 represents extreme fear and 100 represents extreme greed. Use this when asked about crypto market sentiment, investor psychology in digital assets, Bitcoin market mood, altcoin risk appetite, or whether it's a good time to buy/sell cryptocurrencies. Includes historical data and trend analysis."
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
        logger.debug("Fetching Crypto Fear & Greed Index from alternative.me")
        CRYPTO_FEAR_GREED_URL = "https://api.alternative.me/fng/"

        data = await fetch_json(CRYPTO_FEAR_GREED_URL)
        logger.debug(f"Successfully fetched Crypto Fear & Greed Index: {data.get('data', [{}])[0].get('value_classification', 'unknown')}")
        if "data" not in data or not data["data"]:
            raise ValueError("Invalid response format from alternative.me API")

        current_data = data["data"][0]
        output = CryptoFearGreedOutput(
            value=current_data["value"],
            classification=current_data["value_classification"],
            timestamp=current_data["timestamp"],
        )
        return ToolResponse.from_model(output)
