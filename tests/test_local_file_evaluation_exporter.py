"""Tests for LocalFileEvaluationExporter."""

import asyncio
import json
from pathlib import Path

import pytest
from document_extraction_tools.types import Document, EvaluationResult, PathIdentifier

from document_extraction_examples.simple_lease_extraction.components.exporter.local_file_evaluation_exporter import (
    LocalFileEvaluationExporter,
)
from document_extraction_examples.simple_lease_extraction.config.local_file_evaluation_exporter_config import (
    LocalFileEvaluationExporterConfig,
)


def test_local_file_evaluation_exporter_writes_metrics(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Write per-metric JSON files and log averages."""
    logged_metrics = {}

    def fake_log_metric(name: str, value: float) -> None:
        logged_metrics[name] = value

    monkeypatch.setattr("mlflow.log_metric", fake_log_metric)

    config = LocalFileEvaluationExporterConfig(destination={"path": str(tmp_path)})
    exporter = LocalFileEvaluationExporter(config)

    document = Document(
        id="doc-1",
        content_type="text",
        pages=[],
        path_identifier=PathIdentifier(path="doc-1.pdf"),
    )
    results = [
        EvaluationResult(name="accuracy", result=1.0, description="ok"),
        EvaluationResult(name="accuracy", result=0.0, description="bad"),
        EvaluationResult(name="f1", result=0.5, description="f1"),
    ]

    asyncio.run(exporter.export([(document, results)]))

    accuracy_path = tmp_path / "accuracy.json"
    assert accuracy_path.exists()
    data = json.loads(accuracy_path.read_text())
    assert data[0]["document_id"] == "doc-1"

    assert logged_metrics["avg_accuracy"] == 0.5
    assert logged_metrics["avg_f1"] == 0.5
