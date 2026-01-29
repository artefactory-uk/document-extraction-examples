"""Configuration for the local file reader."""

from document_extraction_tools.config import BaseReaderConfig
from pydantic import Field


class LocalFileReaderConfig(BaseReaderConfig):
    """Configuration for local file reading."""

    mime_type: str = Field(
        default="application/pdf",
        description="MIME type to associate with read files.",
    )
