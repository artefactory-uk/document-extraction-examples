"""Configuration for the local file reader."""

from document_extraction_tools.config import BaseReaderConfig


class LocalFileReaderConfig(BaseReaderConfig):
    """Configuration for readers that load documents from the local file system.

    This configuration class does not currently introduce any new options beyond
    those defined in :class:`document_extraction_tools.config.BaseReaderConfig`.
    It exists to provide a clear, explicit configuration type for local file
    readers and to allow project-specific defaults or extensions to be added in
    the future without changing call sites.
    """
