"""RAG retriever for querying indexed documents."""

from dataclasses import dataclass
from typing import List

from src.rag.vector_store import VectorStore


@dataclass
class RetrievedContext:
    """Represents a retrieved context chunk."""

    text: str
    source_path: str
    chunk_index: int
    similarity_score: float
    metadata: dict


class RAGRetriever:
    """Retriever for RAG queries."""

    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.0,
    ) -> List[RetrievedContext]:
        """Retrieve relevant context for a query."""
        results = self.vector_store.query(query_text=query, n_results=top_k)

        contexts = []

        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                distance = results["distances"][0][i]
                # Convert distance to similarity (cosine distance to similarity)
                similarity = 1 - distance

                if similarity >= similarity_threshold:
                    metadata = results["metadatas"][0][i]
                    contexts.append(
                        RetrievedContext(
                            text=doc,
                            source_path=metadata["source_path"],
                            chunk_index=metadata["chunk_index"],
                            similarity_score=similarity,
                            metadata=metadata,
                        )
                    )

        return contexts

    def format_context(
        self, contexts: List[RetrievedContext], include_sources: bool = True
    ) -> str:
        """Format retrieved contexts into a single string."""
        if not contexts:
            return "No relevant context found."

        formatted_parts = []

        for i, ctx in enumerate(contexts, 1):
            if include_sources:
                formatted_parts.append(
                    f"[Source {i}: {ctx.source_path} (Score: {ctx.similarity_score:.3f})]\n{ctx.text}"
                )
            else:
                formatted_parts.append(ctx.text)

        return "\n\n---\n\n".join(formatted_parts)
