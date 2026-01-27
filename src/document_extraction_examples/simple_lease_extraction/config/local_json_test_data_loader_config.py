"""Configuration for the local test data loader."""

from document_extraction_tools.config import (
    BaseTestDataLoaderConfig,
)
from document_extraction_tools.types import PathIdentifier
from pydantic import Field


class LocalJSONTestDataLoaderConfig(BaseTestDataLoaderConfig):
    """Configuration for loading local evaluation test data."""

    test_data: PathIdentifier = Field(
        ..., description="Path to the test data JSON file."
    )
