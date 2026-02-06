"""Tests for LocalFileLister."""

from pathlib import Path

import pytest

from document_extraction_examples.simple_lease_extraction.components.file_lister.local_file_lister import (
    LocalFileLister,
)
from document_extraction_examples.simple_lease_extraction.config.local_file_lister_config import (
    LocalFileListerConfig,
)


def test_local_file_lister_returns_matching_files(tmp_path: Path) -> None:
    """List files using configured extensions with case-insensitive matches."""
    (tmp_path / "a.pdf").write_bytes(b"%PDF")
    (tmp_path / "b.PDF").write_bytes(b"%PDF")
    (tmp_path / "c.txt").write_text("skip")

    config = LocalFileListerConfig(source_dir=str(tmp_path), extensions=[".pdf"])
    lister = LocalFileLister(config)

    results = lister.list_files()
    paths = {Path(item.path).name for item in results}

    assert paths == {"a.pdf", "b.PDF"}


def test_local_file_lister_missing_directory_raises(tmp_path: Path) -> None:
    """Raise when source directory is missing."""
    missing_dir = tmp_path / "missing"
    config = LocalFileListerConfig(source_dir=str(missing_dir), extensions=[".pdf"])
    lister = LocalFileLister(config)

    with pytest.raises(FileNotFoundError):
        lister.list_files()
