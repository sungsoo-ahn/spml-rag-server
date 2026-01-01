"""Configuration management for RAG server."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import yaml


@dataclass
class RAGConfig:
    """Configuration for the RAG system."""

    # Embedding settings
    embedding_model: str = "text-embedding-3-small"

    # Chunking settings
    chunk_size: int = 512  # tokens
    chunk_overlap: int = 50  # tokens

    # ChromaDB settings
    chroma_db_path: str = "data/rag/chroma_db"
    collection_name: str = "documents"

    # Document settings
    documents_path: str = "data/rag/documents"
    supported_extensions: List[str] = field(
        default_factory=lambda: [
            ".pdf",
            ".docx",
            ".doc",
            ".pptx",
            ".ppt",
            ".txt",
            ".md",
            ".markdown",
        ]
    )

    # Retrieval settings
    default_top_k: int = 5
    similarity_threshold: float = 0.3

    # Server settings
    server_name: str = "rag-server"
    log_level: str = "INFO"


def load_config(config_path: Optional[str] = None) -> RAGConfig:
    """Load configuration from YAML file or use defaults."""
    if config_path is None:
        return RAGConfig()

    path = Path(config_path)
    if not path.exists():
        print(f"Config file not found: {config_path}, using defaults")
        return RAGConfig()

    with open(path, "r") as f:
        config_dict = yaml.safe_load(f) or {}

    # Expand environment variables in string values
    def expand_env_vars(value):
        if isinstance(value, str):
            return os.path.expandvars(value)
        return value

    config_dict = {k: expand_env_vars(v) for k, v in config_dict.items()}

    return RAGConfig(**config_dict)
