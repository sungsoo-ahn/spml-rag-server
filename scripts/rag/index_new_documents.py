#!/usr/bin/env python3
"""Index only new documents that aren't already in the vector store."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.rag.chunker import RecursiveChunker
from src.rag.config import load_config
from src.rag.document_processor import DocumentProcessor
from src.rag.vector_store import VectorStore

console = Console()


def main():
    """Index new documents only."""
    # Check for --yes flag
    skip_confirm = "--yes" in sys.argv or "-y" in sys.argv
    # Load config
    config_path = "configs/rag/default.yaml"
    console.print(f"[cyan]Loading config from {config_path}...[/cyan]")
    cfg = load_config(config_path)

    # Initialize components
    console.print("[cyan]Initializing vector store...[/cyan]")
    vector_store = VectorStore(
        persist_directory=cfg.chroma_db_path,
        collection_name=cfg.collection_name,
        embedding_model=cfg.embedding_model,
    )

    # Get already indexed sources
    console.print("[cyan]Checking existing index...[/cyan]")
    indexed_sources = set(vector_store.get_all_sources())
    console.print(f"[green]Found {len(indexed_sources)} documents already indexed[/green]")

    # Find all files in documents directory
    docs_path = Path(cfg.documents_path)
    if not docs_path.exists():
        console.print(f"[red]Error: Documents path does not exist: {docs_path}[/red]")
        return

    # Get all supported files
    processor = DocumentProcessor()
    all_files = []
    for ext in cfg.supported_extensions:
        all_files.extend(docs_path.rglob(f"*{ext}"))

    console.print(f"[cyan]Found {len(all_files)} total files in {docs_path}[/cyan]")

    # Filter to only new files
    # Note: indexed sources are stored as relative paths like "data/rag/documents/file.pdf"
    new_files = []
    for file_path in all_files:
        # Convert to relative path from project root to match stored format
        try:
            rel_path = str(file_path.relative_to(project_root))
        except ValueError:
            # If not relative to project root, try absolute path
            rel_path = str(file_path)

        if rel_path not in indexed_sources:
            new_files.append(file_path)

    if not new_files:
        console.print("[green]No new files to index! Everything is up to date.[/green]")
        return

    console.print(f"[yellow]Found {len(new_files)} new files to index[/yellow]")
    console.print(f"[dim]Skipping {len(indexed_sources)} already-indexed files[/dim]")

    # Confirm before proceeding
    if len(new_files) > 100 and not skip_confirm:
        console.print(f"\n[yellow]Warning: About to index {len(new_files)} files.[/yellow]")
        console.print(f"[yellow]This will use OpenAI API for embeddings.[/yellow]")
        response = console.input("[yellow]Continue? (y/n): [/yellow]")
        if response.lower() != 'y':
            console.print("[red]Aborted[/red]")
            return
    elif len(new_files) > 100:
        console.print(f"\n[cyan]Indexing {len(new_files)} files (confirmed via --yes flag)...[/cyan]")

    # Initialize chunker
    chunker = RecursiveChunker(
        chunk_size=cfg.chunk_size,
        chunk_overlap=cfg.chunk_overlap,
        model=cfg.embedding_model,
    )

    # Index new files
    total_chunks = 0
    successful = 0
    failed = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Indexing {len(new_files)} files...", total=len(new_files))

        for file_path in new_files:
            try:
                # Extract document
                doc = processor.process_file(file_path)
                if doc is None:
                    console.print(f"[yellow]  Skipped (unsupported): {file_path.name}[/yellow]")
                    failed += 1
                    progress.advance(task)
                    continue

                # Chunk document
                chunks = chunker.chunk(doc.content, doc.source_path)
                if not chunks:
                    console.print(f"[yellow]  Skipped (no content): {file_path.name}[/yellow]")
                    failed += 1
                    progress.advance(task)
                    continue

                # Add to vector store
                vector_store.add_chunks(chunks)
                total_chunks += len(chunks)
                successful += 1

                console.print(
                    f"[green]  ✓ {file_path.name}[/green] [dim]({len(chunks)} chunks)[/dim]"
                )

            except Exception as e:
                console.print(f"[red]  ✗ {file_path.name}: {e}[/red]")
                failed += 1

            progress.advance(task)

    # Summary
    console.print("\n[bold]Summary:[/bold]")
    console.print(f"  Successfully indexed: [green]{successful}[/green] documents")
    console.print(f"  Failed/Skipped: [yellow]{failed}[/yellow] documents")
    console.print(f"  Total chunks added: [cyan]{total_chunks}[/cyan]")
    console.print(f"  Total documents in index: [cyan]{len(indexed_sources) + successful}[/cyan]")


if __name__ == "__main__":
    main()
