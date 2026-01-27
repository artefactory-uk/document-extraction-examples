"""Configuration for the PDF to image converter."""

from document_extraction_tools.config import BaseConverterConfig
from pydantic import Field


class PDFToImageConverterConfig(BaseConverterConfig):
    """Configuration for PDF to image conversion."""

    dpi: int = Field(default=200, description="DPI to render PDF pages.")
    format: str = Field(default="jpeg", description="Image format for output.")
