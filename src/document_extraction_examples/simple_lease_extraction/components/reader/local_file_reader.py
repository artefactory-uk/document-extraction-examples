"""Local file reader implementation for the example pipeline."""

from pathlib import Path

from document_extraction_tools.base import BaseReader
from document_extraction_tools.types import DocumentBytes, PathIdentifier

from document_extraction_examples.simple_lease_extraction.config.local_file_reader_config import (
    LocalFileReaderConfig,
)


class LocalFileReader(BaseReader):
    """Reads document bytes from local disk."""

    def __init__(self, config: LocalFileReaderConfig) -> None:
        """Initialize the reader with example config."""
        super().__init__(config)

    def read(self, path: PathIdentifier) -> DocumentBytes:
        """Read bytes from the given path identifier."""
        file_path = Path(path.path)

        return DocumentBytes(
            file_bytes=file_path.read_bytes(),
            path_identifier=path,
            mime_type=self.config.mime_type,
        )
