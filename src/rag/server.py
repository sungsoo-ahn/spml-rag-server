"""
MCP Server for RAG-based document retrieval.
Integrates with Claude Desktop for document Q&A.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from src.rag.chunker import RecursiveChunker
from src.rag.config import RAGConfig, load_config
from src.rag.document_processor import DocumentProcessor
from src.rag.retriever import RAGRetriever
from src.rag.vector_store import VectorStore

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP(
    name="rag-server",
    instructions="""You are a document retrieval assistant. You have access to a collection of indexed documents that you can search through.

Use the search_documents tool to find relevant information from the indexed documents when answering questions.
Always cite your sources when providing information from the documents.""",
)

# Global instances (initialized on first use)
_config: Optional[RAGConfig] = None
_vector_store: Optional[VectorStore] = None
_retriever: Optional[RAGRetriever] = None
_processor: Optional[DocumentProcessor] = None
_chunker: Optional[RecursiveChunker] = None


def get_config() -> RAGConfig:
    """Get or load configuration."""
    global _config
    if _config is None:
        config_path = os.getenv("RAG_CONFIG_PATH", "configs/rag/default.yaml")
        _config = load_config(config_path)
    return _config


def get_vector_store() -> VectorStore:
    """Get or initialize vector store."""
    global _vector_store
    if _vector_store is None:
        config = get_config()
        _vector_store = VectorStore(
            persist_directory=config.chroma_db_path,
            collection_name=config.collection_name,
            embedding_model=config.embedding_model,
        )
    return _vector_store


def get_retriever() -> RAGRetriever:
    """Get or initialize retriever."""
    global _retriever
    if _retriever is None:
        _retriever = RAGRetriever(get_vector_store())
    return _retriever


# ============================================================================
# MCP Tools
# ============================================================================


@mcp.tool()
def search_documents(
    query: str, top_k: int = 5, similarity_threshold: float = 0.3
) -> str:
    """
    Search indexed documents for relevant information.

    Args:
        query: The search query or question
        top_k: Number of results to return (default: 5)
        similarity_threshold: Minimum similarity score 0-1 (default: 0.3)

    Returns:
        Formatted context from relevant documents with source citations
    """
    retriever = get_retriever()
    contexts = retriever.retrieve(
        query=query, top_k=top_k, similarity_threshold=similarity_threshold
    )

    if not contexts:
        return "No relevant documents found for your query."

    return retriever.format_context(contexts, include_sources=True)


@mcp.tool()
def list_indexed_documents() -> str:
    """
    List all documents currently indexed in the vector store.

    Returns:
        Summary of indexed documents and statistics
    """
    vector_store = get_vector_store()
    stats = vector_store.get_stats()
    sources = vector_store.get_all_sources()

    output = [
        "Vector Store Statistics:",
        f"- Total chunks: {stats['total_documents']}",
        f"- Collection: {stats['collection_name']}",
        f"- Unique documents: {len(sources)}",
        "",
        "Indexed Documents:",
    ]

    for source in sources:
        output.append(f"  - {source}")

    if not sources:
        output.append("  (No documents indexed)")

    return "\n".join(output)


@mcp.tool()
def get_document_info(source_path: str) -> str:
    """
    Get information about a specific indexed document.

    Args:
        source_path: Path to the document

    Returns:
        Document metadata and chunk count
    """
    vector_store = get_vector_store()

    try:
        results = vector_store.collection.get(
            where={"source_path": source_path}, include=["metadatas"]
        )

        if not results["ids"]:
            return f"Document not found: {source_path}"

        chunk_count = len(results["ids"])

        return f"""Document: {source_path}
- Total chunks: {chunk_count}
- Indexed: Yes"""

    except Exception as e:
        return f"Error getting document info: {e}"


@mcp.tool()
def index_document(file_path: str) -> str:
    """
    Index a single document into the vector store.

    Args:
        file_path: Path to the document to index

    Returns:
        Status message indicating success or failure
    """
    global _processor, _chunker

    if _processor is None:
        _processor = DocumentProcessor()

    if _chunker is None:
        config = get_config()
        _chunker = RecursiveChunker(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            model=config.embedding_model,
        )

    path = Path(file_path)
    if not path.exists():
        return f"Error: File not found: {file_path}"

    # Extract document
    doc = _processor.process_file(path)
    if doc is None:
        return f"Error: Could not extract text from {file_path}. Unsupported file type."

    # Chunk document
    chunks = _chunker.chunk(doc.content, doc.source_path)

    if not chunks:
        return f"Error: No content chunks generated from {file_path}"

    # Add to vector store
    vector_store = get_vector_store()
    vector_store.add_chunks(chunks)

    return f"""Successfully indexed document:
- Path: {file_path}
- Chunks created: {len(chunks)}
- Total tokens: {sum(c.token_count for c in chunks)}"""


# ============================================================================
# MCP Resources
# ============================================================================


@mcp.resource("rag://stats")
def get_rag_stats() -> str:
    """Get current RAG system statistics."""
    vector_store = get_vector_store()
    stats = vector_store.get_stats()
    config = get_config()

    return f"""RAG System Statistics
=====================
Collection: {stats['collection_name']}
Total Chunks: {stats['total_documents']}
Persist Directory: {stats['persist_directory']}

Configuration:
- Embedding Model: {config.embedding_model}
- Chunk Size: {config.chunk_size} tokens
- Chunk Overlap: {config.chunk_overlap} tokens
"""


@mcp.resource("rag://config")
def get_rag_config() -> str:
    """Get current RAG configuration."""
    config = get_config()
    return f"""RAG Configuration
=================
Embedding Model: {config.embedding_model}
Chunk Size: {config.chunk_size} tokens
Chunk Overlap: {config.chunk_overlap} tokens
ChromaDB Path: {config.chroma_db_path}
Collection Name: {config.collection_name}
Documents Path: {config.documents_path}
"""


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    mcp.run()
