"""Local file lister implementation for the example pipeline."""

from pathlib import Path

import mlflow
from document_extraction_tools.base import BaseFileLister
from document_extraction_tools.config import ExtractionPipelineConfig
from document_extraction_tools.types import PathIdentifier, PipelineContext

from document_extraction_examples.simple_lease_extraction.config.local_file_lister_config import (
    LocalFileListerConfig,
)


class LocalFileLister(BaseFileLister):
    """Lists files from a local directory based on configured extensions."""

    def __init__(
        self, config: LocalFileListerConfig | ExtractionPipelineConfig
    ) -> None:
        """Initialize the lister with example config."""
        super().__init__(config)
        self.source_dir = Path(self.config.source_dir)
        self.extensions = [ext.lower() for ext in self.config.extensions]

    @mlflow.trace(name="list_files", span_type="RETRIEVER")
    def list_files(
        self, context: PipelineContext | None = None
    ) -> list[PathIdentifier]:
        """Return PathIdentifier entries for matching files."""
        _ = context
        span = mlflow.get_current_active_span()
        if span:
            span.set_inputs({"source_dir": str(self.source_dir)})

        if not self.source_dir.exists():
            raise FileNotFoundError(
                f"Source directory {self.source_dir} does not exist."
            )

        files: list[PathIdentifier] = []
        for ext in self.extensions:
            pattern = f"**/*{ext}"
            files.extend(
                PathIdentifier(path=path)
                for path in self.source_dir.glob(pattern, case_sensitive=False)
            )
        return files
