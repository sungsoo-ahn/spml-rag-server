"""ChromaDB vector store for RAG."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv

from src.rag.chunker import Chunk


class VectorStore:
    """ChromaDB vector store for RAG."""

    def __init__(
        self,
        persist_directory: str = "data/rag/chroma_db",
        collection_name: str = "documents",
        embedding_model: str = "text-embedding-3-small",
    ):
        load_dotenv()

        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB with persistence
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False),
        )

        # Use OpenAI embedding function
        self.embedding_function = OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"), model_name=embedding_model
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(self, chunks: List[Chunk], batch_size: int = 100) -> None:
        """Add chunks to the vector store."""
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]

            ids = [f"{chunk.source_path}_{chunk.chunk_index}" for chunk in batch]
            documents = [chunk.text for chunk in batch]
            metadatas = [
                {
                    "source_path": chunk.source_path,
                    "chunk_index": chunk.chunk_index,
                    "start_char": chunk.start_char,
                    "end_char": chunk.end_char,
                    "token_count": chunk.token_count,
                }
                for chunk in batch
            ]

            self.collection.add(ids=ids, documents=documents, metadatas=metadatas)

    def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Query the vector store for similar documents."""
        return self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return {
            "total_documents": self.collection.count(),
            "collection_name": self.collection.name,
            "persist_directory": str(self.persist_directory),
        }

    def get_all_sources(self) -> List[str]:
        """Get all unique source paths."""
        try:
            results = self.collection.get(include=["metadatas"])
            sources = set()
            if results["metadatas"]:
                for meta in results["metadatas"]:
                    sources.add(meta.get("source_path", "unknown"))
            return sorted(list(sources))
        except Exception:
            return []

    def delete_by_source(self, source_path: str) -> None:
        """Delete all chunks from a specific source."""
        self.collection.delete(where={"source_path": source_path})

    def clear(self) -> None:
        """Clear all documents from the collection."""
        # ChromaDB requires deleting and recreating collection
        collection_name = self.collection.name
        self.client.delete_collection(collection_name)
        self.collection = self.client.create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )
