"""Configuration for the local file extraction exporter."""

from document_extraction_tools.config import (
    BaseExtractionExporterConfig,
)
from document_extraction_tools.types import PathIdentifier
from pydantic import Field


class LocalFileExtractionExporterConfig(BaseExtractionExporterConfig):
    """Configuration for local file extraction export."""

    destination: PathIdentifier = Field(
        ...,
        description="The root destination where exported files will be saved.",
    )
