"""Tests for GeminiImageExtractor."""

import asyncio
import types
from typing import Any

import pytest
from document_extraction_tools.types import Document, ImageData, Page, PathIdentifier

from document_extraction_examples.simple_lease_extraction.components.extractor.gemini_image_extractor import (
    GeminiImageExtractor,
)
from document_extraction_examples.simple_lease_extraction.config.gemini_image_extractor_config import (
    GeminiImageExtractorConfig,
)
from document_extraction_examples.simple_lease_extraction.schemas.schema import (
    SimpleLeaseDetails,
)


class DummyResponse:
    """Response wrapper for Gemini extractor tests."""

    def __init__(self, parsed: SimpleLeaseDetails) -> None:
        """Initialize with parsed schema data."""
        self.parsed = parsed


class DummyAioModels:
    """Async models stub for Gemini tests."""

    def __init__(self, response: DummyResponse) -> None:
        """Initialize with a fixed response."""
        self._response = response
        self.called_with: dict[str, Any] | None = None

    async def generate_content(self, **kwargs: object) -> DummyResponse:
        """Return a fixed response and record call."""
        self.called_with = dict(kwargs)
        return self._response


class DummyClient:
    """Client stub with async model access."""

    def __init__(self, response: DummyResponse) -> None:
        """Initialize with a fixed response."""
        self.aio = types.SimpleNamespace(models=DummyAioModels(response))


def test_gemini_image_extractor_calls_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure extractor calls Gemini client and returns parsed data."""
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(
        "document_extraction_examples.simple_lease_extraction.components.extractor.gemini_image_extractor.load_dotenv",
        lambda: None,
    )

    parsed = SimpleLeaseDetails(landlord="A", tenant="B")
    dummy_client = DummyClient(DummyResponse(parsed))

    def _client(*, api_key: str) -> DummyClient:
        _ = api_key
        return dummy_client

    monkeypatch.setattr(
        "document_extraction_examples.simple_lease_extraction.components.extractor.gemini_image_extractor.genai.Client",
        _client,
    )
    monkeypatch.setattr(
        "document_extraction_examples.simple_lease_extraction.components.extractor.gemini_image_extractor.mlflow.genai.load_prompt",
        lambda *_args, **_kwargs: "PROMPT",
    )

    extractor = GeminiImageExtractor(
        GeminiImageExtractorConfig(
            model_name="fake-model",
            mlflow_prompt_name="p",
            mlflow_prompt_version=1,
        )
    )
    document = Document(
        id="doc-1",
        content_type="image",
        pages=[Page(page_number=1, data=ImageData(content=b"img"))],
        path_identifier=PathIdentifier(path="doc-1.pdf"),
    )

    result = asyncio.run(extractor.extract(document, SimpleLeaseDetails))

    assert result.data == parsed
    called = dummy_client.aio.models.called_with
    assert called["model"] == "fake-model"
    assert called["config"].response_schema is SimpleLeaseDetails
