"""Tests for PDFToImageConverter."""

import pytest
from document_extraction_tools.types import DocumentBytes, PathIdentifier
from PIL import Image

from document_extraction_examples.simple_lease_extraction.components.converter.pdf_to_image_converter import (
    PDFToImageConverter,
)
from document_extraction_examples.simple_lease_extraction.config.pdf_to_image_converter_config import (
    PDFToImageConverterConfig,
)


def test_pdf_to_image_converter_builds_document(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Convert PDF bytes into a Document with image pages."""
    image = Image.new("RGB", (2, 2), color="red")

    def fake_convert_from_bytes(*_args: object, **_kwargs: object):
        return [image]

    monkeypatch.setattr(
        "document_extraction_examples.simple_lease_extraction.components.converter.pdf_to_image_converter.convert_from_bytes",
        fake_convert_from_bytes,
    )

    converter = PDFToImageConverter(PDFToImageConverterConfig(dpi=200, format="jpeg"))
    doc_bytes = DocumentBytes(
        file_bytes=b"%PDF",
        path_identifier=PathIdentifier(path="sample.pdf"),
    )

    document = converter.convert(doc_bytes)

    assert document.id == "sample"
    assert document.content_type == "image"
    assert len(document.pages) == 1
    assert document.pages[0].page_number == 1
    assert document.pages[0].data.content != b""
