"""Tests for MLflow helper utilities."""

import pytest

from document_extraction_examples.simple_lease_extraction.utils import mlflow_utils


def test_setup_mlflow_configures_tracking(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure setup_mlflow wires the MLflow settings."""
    calls = {"tracking": None, "experiment": None, "autolog": None}

    monkeypatch.setattr(
        mlflow_utils.mlflow,
        "set_tracking_uri",
        lambda uri: calls.__setitem__("tracking", uri),
    )
    monkeypatch.setattr(
        mlflow_utils.mlflow,
        "set_experiment",
        lambda name: calls.__setitem__("experiment", name),
    )
    monkeypatch.setattr(
        mlflow_utils.mlflow.gemini,
        "autolog",
        lambda log_traces=True: calls.__setitem__("autolog", log_traces),
    )

    mlflow_utils.setup_mlflow(experiment_name="exp", tracking_uri="http://mlflow")

    assert calls["tracking"] == "http://mlflow"
    assert calls["experiment"] == "exp"
    assert calls["autolog"] is True
