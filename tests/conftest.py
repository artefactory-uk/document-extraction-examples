"""Shared test fixtures and MLflow stubs for example tests."""

import types

import mlflow


def _noop(*_args: object, **_kwargs: object) -> None:
    return None


def _trace(*_args: object, **_kwargs: object):
    return lambda fn: fn


mlflow.trace = _trace  # type: ignore[assignment]
mlflow.get_current_active_span = lambda: None  # type: ignore[assignment]
mlflow.log_metric = _noop  # type: ignore[assignment]
mlflow.log_param = _noop  # type: ignore[assignment]
mlflow.log_dict = _noop  # type: ignore[assignment]
mlflow.set_tracking_uri = _noop  # type: ignore[assignment]
mlflow.set_experiment = _noop  # type: ignore[assignment]
mlflow.gemini = types.SimpleNamespace(autolog=_noop)  # type: ignore[attr-defined]
mlflow.genai = types.SimpleNamespace(load_prompt=lambda *_args, **_kwargs: "prompt")
