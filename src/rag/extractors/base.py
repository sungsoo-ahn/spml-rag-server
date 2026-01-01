"""Base extractor interface for document extraction."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any


@dataclass
class ExtractedDocument:
    """Represents an extracted document with metadata."""

    content: str
    source_path: str
    file_type: str
    title: Optional[str] = None
    page_count: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)


class BaseExtractor(ABC):
    """Abstract base class for document extractors."""

    supported_extensions: List[str] = []

    @abstractmethod
    def extract(self, file_path: Path) -> ExtractedDocument:
        """Extract text content from a file."""
        pass

    @classmethod
    def can_handle(cls, file_path: Path) -> bool:
        """Check if this extractor can handle the given file."""
        return file_path.suffix.lower() in cls.supported_extensions
