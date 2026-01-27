"""Configuration for the local file evaluation exporter."""

from document_extraction_tools.config import (
    BaseEvaluationExporterConfig,
)
from document_extraction_tools.types import PathIdentifier
from pydantic import Field


class LocalFileEvaluationExporterConfig(BaseEvaluationExporterConfig):
    """Configuration for local evaluation results export."""

    destination: PathIdentifier = Field(
        ...,
        description="The root destination where evaluation results will be saved.",
    )
