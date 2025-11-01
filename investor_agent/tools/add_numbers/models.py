"""Pydantic models for the AddNumbers tool."""

from typing import Union

from pydantic import Field, BaseModel, ConfigDict

from ..interfaces.tool import BaseToolInput


class AddNumbersInput(BaseToolInput):
    """Input schema for the AddNumbers tool."""

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"number1": 5, "number2": 3}, {"number1": -2.5, "number2": 1.5}]}
    )

    number1: float = Field(description="The first number to add", examples=[5, -2.5])
    number2: float = Field(description="The second number to add", examples=[3, 1.5])


class AddNumbersOutput(BaseModel):
    """Output schema for the AddNumbers tool."""

    model_config = ConfigDict(json_schema_extra={"examples": [{"sum": 8, "error": None}, {"sum": -1.0, "error": None}]})

    sum: float = Field(description="The sum of the two numbers")
    error: Union[str, None] = Field(default=None, description="An error message if the operation failed.")
