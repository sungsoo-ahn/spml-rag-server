"""Document processor for orchestrating extraction from multiple file types."""

from pathlib import Path
from typing import List, Optional
from tqdm import tqdm

from src.rag.extractors.base import BaseExtractor, ExtractedDocument
from src.rag.extractors.pdf_extractor import PDFExtractor
from src.rag.extractors.docx_extractor import DocxExtractor
from src.rag.extractors.pptx_extractor import PptxExtractor
from src.rag.extractors.text_extractor import TextExtractor
from src.rag.extractors.markdown_extractor import MarkdownExtractor


class DocumentProcessor:
    """Orchestrates document extraction from multiple file types."""

    def __init__(self):
        self.extractors: List[BaseExtractor] = [
            PDFExtractor(),
            DocxExtractor(),
            PptxExtractor(),
            TextExtractor(),
            MarkdownExtractor(),
        ]

    def get_extractor(self, file_path: Path) -> Optional[BaseExtractor]:
        """Find the appropriate extractor for a file."""
        for extractor in self.extractors:
            if extractor.can_handle(file_path):
                return extractor
        return None

    def process_file(self, file_path: Path) -> Optional[ExtractedDocument]:
        """Process a single file and return extracted document."""
        extractor = self.get_extractor(file_path)
        if extractor is None:
            return None

        try:
            return extractor.extract(file_path)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None

    def process_directory(
        self, directory: Path, recursive: bool = True, show_progress: bool = True
    ) -> List[ExtractedDocument]:
        """Process all supported files in a directory."""
        documents = []

        pattern = "**/*" if recursive else "*"
        files = list(directory.glob(pattern))
        files = [f for f in files if f.is_file() and self.get_extractor(f) is not None]

        iterator = tqdm(files, desc="Processing documents") if show_progress else files

        for file_path in iterator:
            doc = self.process_file(file_path)
            if doc:
                documents.append(doc)

        return documents
