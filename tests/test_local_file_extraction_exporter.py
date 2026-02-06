"""Tests for LocalFileExtractionExporter."""

import asyncio
import json
from pathlib import Path

from document_extraction_tools.types import Document, ExtractionResult, PathIdentifier
from pydantic import BaseModel

from document_extraction_examples.simple_lease_extraction.components.exporter.local_file_extraction_exporter import (
    LocalFileExtractionExporter,
)
from document_extraction_examples.simple_lease_extraction.config.local_file_extraction_exporter_config import (
    LocalFileExtractionExporterConfig,
)


class DummySchema(BaseModel):
    """Simple schema used in exporter tests."""

    value: str


def test_local_file_extraction_exporter_writes_json(tmp_path: Path) -> None:
    """Write extracted data to a JSON file."""
    config = LocalFileExtractionExporterConfig(destination={"path": str(tmp_path)})
    exporter = LocalFileExtractionExporter(config)

    document = Document(
        id="doc-1",
        content_type="text",
        pages=[],
        path_identifier=PathIdentifier(path="doc-1.pdf"),
    )
    data = ExtractionResult(data=DummySchema(value="ok"))

    asyncio.run(exporter.export(document, data))

    out_path = tmp_path / "result_doc-1.json"
    assert out_path.exists()
    payload = json.loads(out_path.read_text())
    assert payload["value"] == "ok"
