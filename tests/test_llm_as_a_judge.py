"""Tests for LLM-as-a-judge utilities."""

import types

import pytest

from document_extraction_examples.simple_lease_extraction.utils import llm_as_a_judge


def test_get_llm_judge_client_requires_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Raise when GEMINI_API_KEY is missing."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr(llm_as_a_judge, "load_dotenv", lambda: None)

    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        llm_as_a_judge.get_llm_judge_client()


def test_get_llm_judge_client_uses_env_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Instantiate the Gemini client using the environment key."""
    monkeypatch.setenv("GEMINI_API_KEY", "secret")
    monkeypatch.setattr(llm_as_a_judge, "load_dotenv", lambda: None)

    created = {}

    def _client(api_key: str) -> object:
        created["api_key"] = api_key
        return object()

    monkeypatch.setattr(llm_as_a_judge.genai, "Client", _client)

    client = llm_as_a_judge.get_llm_judge_client()
    assert client is not None
    assert created["api_key"] == "secret"


def test_invoke_llm_as_a_judge_returns_bool() -> None:
    """Return parsed LLM judgment."""

    class DummyParsed:
        def __init__(self, is_equal: bool) -> None:
            self.is_equal = is_equal

    class DummyResponse:
        def __init__(self) -> None:
            self.parsed = DummyParsed(True)

    class DummyModels:
        def __init__(self) -> None:
            self.called: dict[str, object] | None = None

        def generate_content(self, **kwargs: object) -> DummyResponse:
            self.called = dict(kwargs)
            return DummyResponse()

    dummy_client = types.SimpleNamespace(models=DummyModels())

    result = llm_as_a_judge.invoke_llm_as_a_judge(
        true_value="A",
        pred_value="B",
        client=dummy_client,
        model_name="model",
        prompt_template="True={true_value}, Pred={pred_value}",
    )

    assert result is True
    assert dummy_client.models.called["model"] == "model"
