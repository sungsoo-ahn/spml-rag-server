"""PDF document extractor using pypdf."""

from pathlib import Path
from pypdf import PdfReader

from src.rag.extractors.base import BaseExtractor, ExtractedDocument


class PDFExtractor(BaseExtractor):
    """Extract text from PDF files using pypdf."""

    supported_extensions = [".pdf"]

    def extract(self, file_path: Path) -> ExtractedDocument:
        """Extract text content from a PDF file."""
        reader = PdfReader(str(file_path))
        pages = []

        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)

        content = "\n\n".join(pages)

        # Extract metadata safely
        metadata = {}
        if reader.metadata:
            for key, value in reader.metadata.items():
                if isinstance(key, str):
                    metadata[key] = str(value) if value else None

        return ExtractedDocument(
            content=content,
            source_path=str(file_path),
            file_type="pdf",
            title=file_path.stem,
            page_count=len(reader.pages),
            metadata=metadata,
        )
