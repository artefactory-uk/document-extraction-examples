"""Tests for LocalJSONTestDataLoader."""

import json
from pathlib import Path

import pytest
from document_extraction_tools.types import (
    ExtractionResult,
    PathIdentifier,
)

from document_extraction_examples.simple_lease_extraction.components.test_data_loader import (
    local_json_test_data_loader,
)
from document_extraction_examples.simple_lease_extraction.config.local_json_test_data_loader_config import (
    LocalJSONTestDataLoaderConfig,
)
from document_extraction_examples.simple_lease_extraction.schemas.schema import (
    SimpleLeaseDetails,
)


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload))


def test_local_json_test_data_loader_parses_examples(tmp_path: Path) -> None:
    """Load JSON test data into EvaluationExample objects."""
    payload = [
        {
            "inputs": {"input_pdf_path": str(tmp_path / "doc-1.pdf")},
            "expectations": {"landlord": "A", "tenant": "B"},
        }
    ]
    json_path = tmp_path / "test_data.json"
    _write_json(json_path, payload)

    loader = local_json_test_data_loader.LocalJSONTestDataLoader(
        LocalJSONTestDataLoaderConfig(test_data=PathIdentifier(path=json_path))
    )
    examples = loader.load_test_data(PathIdentifier(path=json_path))

    assert len(examples) == 1
    assert examples[0].id == "doc-1"
    assert examples[0].path_identifier.path == Path(tmp_path / "doc-1.pdf")
    assert isinstance(examples[0].true, ExtractionResult)
    assert examples[0].true.data == SimpleLeaseDetails(landlord="A", tenant="B")


def test_local_json_test_data_loader_rejects_non_list(tmp_path: Path) -> None:
    """Reject non-list JSON payloads."""
    json_path = tmp_path / "bad.json"
    _write_json(json_path, {"inputs": {"input_pdf_path": "doc.pdf"}})

    loader = local_json_test_data_loader.LocalJSONTestDataLoader(
        LocalJSONTestDataLoaderConfig(test_data=PathIdentifier(path=json_path))
    )
    with pytest.raises(ValueError, match="JSON array"):
        loader.load_test_data(PathIdentifier(path=json_path))
