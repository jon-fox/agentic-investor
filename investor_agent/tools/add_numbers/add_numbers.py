"""Tool for adding two numbers."""

from typing import Dict, Any

from ..interfaces.tool import Tool, ToolResponse
from .models import AddNumbersInput, AddNumbersOutput


class AddNumbersTool(Tool):
    """Tool that adds two numbers together."""

    name = "AddNumbers"
    description = "Adds two numbers (number1 + number2) and returns the sum"
    input_model = AddNumbersInput
    output_model = AddNumbersOutput

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "input": self.input_model.model_json_schema(),
            "output": self.output_model.model_json_schema(),
        }

    async def execute(self, input_data: AddNumbersInput) -> ToolResponse:
        """Execute the add numbers tool.

        Args:
            input_data: The validated input for the tool

        Returns:
            A response containing the sum
        """
        result = input_data.number1 + input_data.number2
        output = AddNumbersOutput(sum=result, error=None)
        return ToolResponse.from_model(output)
