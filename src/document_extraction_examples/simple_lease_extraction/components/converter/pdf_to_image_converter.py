"""PDF-to-image converter implementation for the example pipeline."""

import io
from pathlib import Path

from document_extraction_tools.base import BaseConverter
from document_extraction_tools.config import (
    EvaluationPipelineConfig,
    ExtractionPipelineConfig,
)
from document_extraction_tools.types import (
    Document,
    DocumentBytes,
    ImageData,
    Page,
    PipelineContext,
)
from pdf2image import convert_from_bytes

from document_extraction_examples.simple_lease_extraction.config.pdf_to_image_converter_config import (
    PDFToImageConverterConfig,
)


class PDFToImageConverter(BaseConverter):
    """Converts PDF bytes into image pages."""

    def __init__(
        self,
        config: (
            PDFToImageConverterConfig
            | ExtractionPipelineConfig
            | EvaluationPipelineConfig
        ),
    ) -> None:
        """Initialize converter with example config."""
        super().__init__(config)
        self.dpi = self.config.dpi
        self.image_format = self.config.format

    def convert(
        self,
        document_bytes: DocumentBytes,
        context: PipelineContext | None = None,
    ) -> Document:
        """Convert raw PDF bytes into a Document with image pages."""
        _ = context  # Required by BaseConverter; reserved for future metadata.
        pil_images = convert_from_bytes(
            document_bytes.file_bytes, dpi=self.dpi, fmt=self.image_format
        )

        pages = []
        for i, img in enumerate(pil_images):
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format=self.image_format.upper())

            pages.append(
                Page(
                    page_number=i + 1,
                    data=ImageData(
                        content=img_byte_arr.getvalue(),
                    ),
                )
            )

        file_path = Path(document_bytes.path_identifier.path)

        return Document(
            id=file_path.stem,
            content_type="image",
            path_identifier=document_bytes.path_identifier,
            pages=pages,
        )
