"""Local file extraction exporter implementation for the example pipeline."""

from pathlib import Path

import aiofiles
import mlflow
from document_extraction_tools.base import (
    BaseExtractionExporter,
)
from document_extraction_tools.config import ExtractionPipelineConfig
from document_extraction_tools.types import Document, ExtractionResult, PipelineContext
from pydantic import BaseModel

from document_extraction_examples.simple_lease_extraction.config.local_file_extraction_exporter_config import (
    LocalFileExtractionExporterConfig,
)


class LocalFileExtractionExporter(BaseExtractionExporter):
    """Writes extracted data to local JSON files."""

    def __init__(
        self,
        config: LocalFileExtractionExporterConfig | ExtractionPipelineConfig,
    ) -> None:
        """Initialize exporter and ensure output directory exists."""
        super().__init__(config)
        Path(self.config.destination.path).mkdir(parents=True, exist_ok=True)

    @mlflow.trace(name="export_extracted_data", span_type="MEMORY")
    async def export(
        self,
        document: Document,
        data: ExtractionResult[BaseModel],
        context: PipelineContext | None = None,
    ) -> None:
        """Persist the extracted data as JSON."""
        _ = context
        span = mlflow.get_current_active_span()
        if span:
            span.set_inputs(
                {"document_id": document.id, "data": data.data.model_dump()}
            )

        filename = f"result_{document.id}"
        out_path = Path(self.config.destination.path) / f"{filename}.json"

        async with aiofiles.open(out_path, "w") as f:
            await f.write(data.data.model_dump_json(indent=2))
