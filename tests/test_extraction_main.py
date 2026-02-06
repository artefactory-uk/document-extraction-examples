"""Tests for extraction_main orchestration."""

from pathlib import Path

import pytest
from document_extraction_tools.types import PathIdentifier

from document_extraction_examples.simple_lease_extraction import extraction_main


def test_run_extraction_pipeline_invokes_orchestrator(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Run extraction pipeline with a mocked orchestrator."""
    config_stub = object()
    monkeypatch.setattr(
        extraction_main,
        "load_extraction_config",
        lambda **_kwargs: config_stub,
    )

    files = [PathIdentifier(path="a.pdf"), PathIdentifier(path="b.pdf")]

    class DummyFileLister:
        def list_files(self) -> list[PathIdentifier]:
            return files

    class DummyOrchestrator:
        def __init__(self) -> None:
            self.file_lister = DummyFileLister()
            self.ran_with: list[PathIdentifier] | None = None

        async def run(self, run_files: list[PathIdentifier]) -> None:
            self.ran_with = run_files

    dummy = DummyOrchestrator()
    monkeypatch.setattr(
        extraction_main.ExtractionOrchestrator,
        "from_config",
        lambda **_kwargs: dummy,
    )

    result = extraction_main.run_extraction_pipeline(Path("config"))

    assert result == {"files_processed": 2}
    assert dummy.ran_with == files
