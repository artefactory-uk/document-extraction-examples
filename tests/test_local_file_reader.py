"""Tests for LocalFileReader."""

from pathlib import Path

from document_extraction_tools.types import PathIdentifier

from document_extraction_examples.simple_lease_extraction.components.reader.local_file_reader import (
    LocalFileReader,
)
from document_extraction_examples.simple_lease_extraction.config.local_file_reader_config import (
    LocalFileReaderConfig,
)


def test_local_file_reader_reads_bytes(tmp_path: Path) -> None:
    """Read bytes from a file path identifier."""
    file_path = tmp_path / "doc.pdf"
    payload = b"pdf-bytes"
    file_path.write_bytes(payload)

    reader = LocalFileReader(LocalFileReaderConfig())
    result = reader.read(PathIdentifier(path=str(file_path)))

    assert result.file_bytes == payload
    assert result.path_identifier.path == str(file_path)
