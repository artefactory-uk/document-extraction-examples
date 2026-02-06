"""Example entrypoint for the simple lease evaluation pipeline."""

import asyncio
import logging
from pathlib import Path

import mlflow
from document_extraction_tools.base import BaseEvaluator
from document_extraction_tools.config import (
    BaseEvaluatorConfig,
    EvaluationOrchestratorConfig,
    EvaluationPipelineConfig,
    load_evaluation_config,
)
from document_extraction_tools.runners import (
    EvaluationOrchestrator,
)
from document_extraction_tools.types import EvaluationExample, PathIdentifier
from mlflow.entities.span import LiveSpan

from document_extraction_examples.simple_lease_extraction.components.converter.pdf_to_image_converter import (
    PDFToImageConverter,
)
from document_extraction_examples.simple_lease_extraction.components.evaluator.accuracy_evaluator import (
    AccuracyEvaluator,
)
from document_extraction_examples.simple_lease_extraction.components.evaluator.f1_evaluator import (
    F1Evaluator,
)
from document_extraction_examples.simple_lease_extraction.components.exporter.local_file_evaluation_exporter import (
    LocalFileEvaluationExporter,
)
from document_extraction_examples.simple_lease_extraction.components.extractor.gemini_image_extractor import (
    GeminiImageExtractor,
)
from document_extraction_examples.simple_lease_extraction.components.reader.local_file_reader import (
    LocalFileReader,
)
from document_extraction_examples.simple_lease_extraction.components.test_data_loader.local_json_test_data_loader import (  # noqa: E501
    LocalJSONTestDataLoader,
)
from document_extraction_examples.simple_lease_extraction.config.evaluator_config import (
    AccuracyEvaluatorConfig,
    F1EvaluatorConfig,
)
from document_extraction_examples.simple_lease_extraction.config.gemini_image_extractor_config import (
    GeminiImageExtractorConfig,
)
from document_extraction_examples.simple_lease_extraction.config.local_file_evaluation_exporter_config import (
    LocalFileEvaluationExporterConfig,
)
from document_extraction_examples.simple_lease_extraction.config.local_file_reader_config import (
    LocalFileReaderConfig,
)
from document_extraction_examples.simple_lease_extraction.config.local_json_test_data_loader_config import (
    LocalJSONTestDataLoaderConfig,
)
from document_extraction_examples.simple_lease_extraction.config.pdf_to_image_converter_config import (
    PDFToImageConverterConfig,
)
from document_extraction_examples.simple_lease_extraction.schemas.schema import (
    SimpleLeaseDetails,
)
from document_extraction_examples.simple_lease_extraction.utils.mlflow_utils import (
    setup_mlflow,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


@mlflow.trace(name="run_evaluation_pipeline", span_type="CHAIN")
def run_evaluation_pipeline(config_dir: Path) -> dict[str, int]:
    """Run the example evaluation pipeline."""
    span = mlflow.get_current_active_span()
    if span is not None:
        span.set_inputs({"config_dir": str(config_dir)})

    # 1. Load Configuration
    evaluator_config_classes: list[type[BaseEvaluatorConfig]] = [
        AccuracyEvaluatorConfig,
        F1EvaluatorConfig,
    ]
    config: EvaluationPipelineConfig = load_evaluation_config(
        config_dir=config_dir,
        evaluation_orchestrator_config_cls=EvaluationOrchestratorConfig,
        test_data_loader_config_cls=LocalJSONTestDataLoaderConfig,
        evaluator_config_classes=evaluator_config_classes,
        reader_config_cls=LocalFileReaderConfig,
        converter_config_cls=PDFToImageConverterConfig,
        extractor_config_cls=GeminiImageExtractorConfig,
        evaluation_exporter_config_cls=LocalFileEvaluationExporterConfig,
    )

    logger.info("Configuration loaded successfully.")

    # 2. Initialize Orchestrator
    evaluator_classes: list[type[BaseEvaluator[SimpleLeaseDetails]]] = [
        AccuracyEvaluator,
        F1Evaluator,
    ]
    orchestrator: EvaluationOrchestrator[SimpleLeaseDetails] = (
        EvaluationOrchestrator.from_config(
            config=config,
            schema=SimpleLeaseDetails,
            reader_cls=LocalFileReader,
            converter_cls=PDFToImageConverter,
            extractor_cls=GeminiImageExtractor,
            test_data_loader_cls=LocalJSONTestDataLoader,
            evaluator_classes=evaluator_classes,
            evaluation_exporter_cls=LocalFileEvaluationExporter,
        )
    )

    # 3. Load Evaluation Examples
    loader_path = PathIdentifier(path=config.test_data_loader.test_data.path)
    examples: list[EvaluationExample] = orchestrator.test_data_loader.load_test_data(
        loader_path
    )

    logger.info("Loaded %d evaluation examples.", len(examples))

    # 4. Run Evaluation
    asyncio.run(orchestrator.run(examples))

    return {"examples_processed": len(examples)}


if __name__ == "__main__":
    # Decorate orchestrator methods with MLflow tracing
    traced_process_example = mlflow.trace(name="process_example", span_type="CHAIN")(
        EvaluationOrchestrator.process_example
    )
    setattr(EvaluationOrchestrator, "process_example", traced_process_example)

    # Silent overly verbose logs from dependencies
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("google_genai").setLevel(logging.WARNING)

    # Set up MLflow tracking
    setup_mlflow(
        tracking_uri="http://localhost:8080", experiment_name="simple_lease_evaluation"
    )

    # Configure MLflow to drop large outputs from process_example spans
    def _drop_process_example_outputs(span: LiveSpan) -> None:
        """Span processor to drop outputs from process_example spans."""
        if span.name == "process_example":
            span.set_outputs(None)

    mlflow.tracing.configure(span_processors=[_drop_process_example_outputs])

    # Run the evaluation pipeline with the config directory
    config_dir = Path(__file__).parent / "config/yaml"
    with mlflow.start_run():
        run_evaluation_pipeline(config_dir)
