"""Tests for AccuracyEvaluator."""

import pytest
from document_extraction_tools.types import ExtractionResult

from document_extraction_examples.simple_lease_extraction.components.evaluator import (
    accuracy_evaluator,
)
from document_extraction_examples.simple_lease_extraction.components.evaluator.accuracy_evaluator import (
    AccuracyEvaluator,
)
from document_extraction_examples.simple_lease_extraction.config.evaluator_config import (
    AccuracyEvaluatorConfig,
)
from document_extraction_examples.simple_lease_extraction.schemas.schema import (
    SimpleLeaseDetails,
)


def _make_result(
    landlord: str | None, tenant: str | None
) -> ExtractionResult[SimpleLeaseDetails]:
    return ExtractionResult(data=SimpleLeaseDetails(landlord=landlord, tenant=tenant))


def test_accuracy_evaluator_basic_match() -> None:
    """Compute exact match accuracy with deterministic values."""
    evaluator = AccuracyEvaluator(AccuracyEvaluatorConfig(use_llm_judge=False))

    true = _make_result("A", "B")
    pred = _make_result("A", "C")

    result = evaluator.evaluate(true, pred)

    assert result.name == "accuracy"
    assert result.result == pytest.approx(10 / 11)
    assert "Field-level exact match" in result.description


def test_accuracy_evaluator_llm_config_validation() -> None:
    """Require model and prompt when LLM judge is enabled."""
    with pytest.raises(ValueError, match="LLM judge requires"):
        AccuracyEvaluator(AccuracyEvaluatorConfig(use_llm_judge=True))


def test_accuracy_evaluator_llm_judge_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """Use LLM judge for equality checks when enabled."""

    def _always_true(*_args: object, **_kwargs: object) -> bool:
        return True

    monkeypatch.setattr(accuracy_evaluator, "get_llm_judge_client", lambda: object())
    monkeypatch.setattr(accuracy_evaluator, "invoke_llm_as_a_judge", _always_true)

    evaluator = AccuracyEvaluator(
        AccuracyEvaluatorConfig(
            use_llm_judge=True,
            llm_judge_model="m",
            llm_judge_prompt="p",
        )
    )

    true = _make_result("A", "B")
    pred = _make_result("X", "Y")

    result = evaluator.evaluate(true, pred)
    assert result.result == 1.0
