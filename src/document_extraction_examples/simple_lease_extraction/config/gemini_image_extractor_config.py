"""Configuration for the Gemini with images extractor."""

from document_extraction_tools.config import BaseExtractorConfig
from pydantic import Field


class GeminiImageExtractorConfig(BaseExtractorConfig):
    """Configuration for the Gemini with images extractor."""

    model_name: str = Field(
        default="gemini-3-flash-preview",
        description="Gemini model to use for extraction.",
    )
    mlflow_prompt_name: str = Field(
        default=...,
        description="MLflow prompt name to use for prompt retrieval.",
    )
    mlflow_prompt_version: int = Field(
        default=...,
        description="MLflow prompt version to use for prompt retrieval.",
    )
