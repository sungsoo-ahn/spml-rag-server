"""Markdown file extractor."""

from pathlib import Path

from src.rag.extractors.base import BaseExtractor, ExtractedDocument


class MarkdownExtractor(BaseExtractor):
    """Extract text from Markdown files."""

    supported_extensions = [".md", ".markdown"]

    def extract(self, file_path: Path) -> ExtractedDocument:
        """Extract text content from a Markdown file."""
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        # Extract title from first heading if present
        title = file_path.stem
        lines = content.split("\n")
        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
                break

        return ExtractedDocument(
            content=content,
            source_path=str(file_path),
            file_type="markdown",
            title=title,
        )
