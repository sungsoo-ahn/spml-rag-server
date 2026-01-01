"""Plain text file extractor."""

from pathlib import Path

from src.rag.extractors.base import BaseExtractor, ExtractedDocument


class TextExtractor(BaseExtractor):
    """Extract text from plain text files."""

    supported_extensions = [".txt"]

    def extract(self, file_path: Path) -> ExtractedDocument:
        """Extract text content from a plain text file."""
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        return ExtractedDocument(
            content=content,
            source_path=str(file_path),
            file_type="txt",
            title=file_path.stem,
        )
