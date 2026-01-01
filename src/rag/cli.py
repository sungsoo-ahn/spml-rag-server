"""CLI commands for RAG server management."""

from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from src.rag.chunker import RecursiveChunker
from src.rag.config import load_config
from src.rag.document_processor import DocumentProcessor
from src.rag.retriever import RAGRetriever
from src.rag.vector_store import VectorStore

app = typer.Typer(name="rag", help="RAG server CLI for document indexing and management")
console = Console()


@app.command()
def index(
    path: str = typer.Argument(..., help="Path to document or directory"),
    config: str = typer.Option(
        "configs/rag/default.yaml", "--config", "-c", help="Path to configuration file"
    ),
    recursive: bool = typer.Option(
        True, "--recursive/--no-recursive", help="Recursively process directories"
    ),
    clear: bool = typer.Option(
        False, "--clear", help="Clear existing index before indexing"
    ),
):
    """Index documents into the vector store."""
    cfg = load_config(config)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Initializing...", total=None)

        processor = DocumentProcessor()
        chunker = RecursiveChunker(
            chunk_size=cfg.chunk_size,
            chunk_overlap=cfg.chunk_overlap,
            model=cfg.embedding_model,
        )
        vector_store = VectorStore(
            persist_directory=cfg.chroma_db_path,
            collection_name=cfg.collection_name,
            embedding_model=cfg.embedding_model,
        )

        if clear:
            console.print("[yellow]Clearing existing index...[/yellow]")
            vector_store.clear()

    # Process documents
    target_path = Path(path)

    if target_path.is_file():
        doc = processor.process_file(target_path)
        documents = [doc] if doc else []
    elif target_path.is_dir():
        documents = processor.process_directory(target_path, recursive=recursive)
    else:
        console.print(f"[red]Error: Path not found: {path}[/red]")
        raise typer.Exit(1)

    if not documents:
        console.print("[yellow]No documents found to index[/yellow]")
        raise typer.Exit(0)

    # Chunk and index
    total_chunks = 0
    for doc in documents:
        chunks = chunker.chunk(doc.content, doc.source_path)
        vector_store.add_chunks(chunks)
        total_chunks += len(chunks)
        console.print(f"  Indexed: {doc.source_path} ({len(chunks)} chunks)")

    console.print(
        f"\n[green]Successfully indexed {len(documents)} documents ({total_chunks} chunks)[/green]"
    )


@app.command()
def stats(
    config: str = typer.Option(
        "configs/rag/default.yaml", "--config", "-c", help="Path to configuration file"
    ),
):
    """Show vector store statistics."""
    cfg = load_config(config)
    vector_store = VectorStore(
        persist_directory=cfg.chroma_db_path,
        collection_name=cfg.collection_name,
        embedding_model=cfg.embedding_model,
    )

    store_stats = vector_store.get_stats()
    sources = vector_store.get_all_sources()

    table = Table(title="Vector Store Statistics")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Collection Name", store_stats["collection_name"])
    table.add_row("Total Chunks", str(store_stats["total_documents"]))
    table.add_row("Unique Documents", str(len(sources)))
    table.add_row("Persist Directory", store_stats["persist_directory"])

    console.print(table)

    if sources:
        console.print("\n[bold]Indexed Documents:[/bold]")
        for source in sources:
            console.print(f"  - {source}")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    top_k: int = typer.Option(5, "--top-k", "-k", help="Number of results"),
    config: str = typer.Option(
        "configs/rag/default.yaml", "--config", "-c", help="Path to configuration file"
    ),
):
    """Search indexed documents."""
    cfg = load_config(config)
    vector_store = VectorStore(
        persist_directory=cfg.chroma_db_path,
        collection_name=cfg.collection_name,
        embedding_model=cfg.embedding_model,
    )

    retriever = RAGRetriever(vector_store)
    contexts = retriever.retrieve(query, top_k=top_k)

    if not contexts:
        console.print("[yellow]No results found[/yellow]")
        return

    for i, ctx in enumerate(contexts, 1):
        console.print(f"\n[bold cyan]Result {i}[/bold cyan] (Score: {ctx.similarity_score:.3f})")
        console.print(f"[dim]Source: {ctx.source_path}[/dim]")
        text_preview = ctx.text[:500] + "..." if len(ctx.text) > 500 else ctx.text
        console.print(text_preview)


@app.command()
def serve(
    config: str = typer.Option(
        "configs/rag/default.yaml", "--config", "-c", help="Path to configuration file"
    ),
):
    """Run the MCP server."""
    import os

    os.environ["RAG_CONFIG_PATH"] = config

    from src.rag.server import mcp

    console.print("[green]Starting RAG MCP Server...[/green]")
    mcp.run()


@app.command()
def clear(
    config: str = typer.Option(
        "configs/rag/default.yaml", "--config", "-c", help="Path to configuration file"
    ),
):
    """Clear the vector store."""
    cfg = load_config(config)

    if not typer.confirm("Are you sure you want to clear all indexed documents?"):
        raise typer.Exit(0)

    vector_store = VectorStore(
        persist_directory=cfg.chroma_db_path,
        collection_name=cfg.collection_name,
        embedding_model=cfg.embedding_model,
    )
    vector_store.clear()
    console.print("[green]Vector store cleared[/green]")


if __name__ == "__main__":
    app()
