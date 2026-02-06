"""Tests for evaluation_main orchestration."""

from pathlib import Path
from types import SimpleNamespace

import pytest
from document_extraction_tools.types import (
    EvaluationExample,
    ExtractionResult,
    PathIdentifier,
)

from document_extraction_examples.simple_lease_extraction import evaluation_main
from document_extraction_examples.simple_lease_extraction.schemas.schema import (
    SimpleLeaseDetails,
)


def test_run_evaluation_pipeline_invokes_orchestrator(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Run evaluation pipeline with a mocked orchestrator."""
    test_data = PathIdentifier(path="tests.json")
    config_stub = SimpleNamespace(test_data_loader=SimpleNamespace(test_data=test_data))
    monkeypatch.setattr(
        evaluation_main,
        "load_evaluation_config",
        lambda **_kwargs: config_stub,
    )

    examples = [
        EvaluationExample(
            id="doc-1",
            path_identifier=PathIdentifier(path="doc-1.pdf"),
            true=ExtractionResult(data=SimpleLeaseDetails(landlord="A", tenant="B")),
        )
    ]

    class DummyLoader:
        def __init__(self) -> None:
            self.called_with = None

        def load_test_data(
            self,
            path_identifier: PathIdentifier,
        ) -> list[EvaluationExample]:
            self.called_with = path_identifier
            return examples

    class DummyOrchestrator:
        def __init__(self) -> None:
            self.test_data_loader = DummyLoader()
            self.ran_with: list[EvaluationExample] | None = None

        async def run(self, run_examples: list[EvaluationExample]) -> None:
            self.ran_with = run_examples

    dummy = DummyOrchestrator()
    monkeypatch.setattr(
        evaluation_main.EvaluationOrchestrator,
        "from_config",
        lambda **_kwargs: dummy,
    )

    result = evaluation_main.run_evaluation_pipeline(Path("config"))

    assert result == {"examples_processed": 1}
    assert dummy.test_data_loader.called_with == test_data
    assert dummy.ran_with == examples
