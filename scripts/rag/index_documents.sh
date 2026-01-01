#!/bin/bash
# Index documents into the RAG vector store

set -e

DOCUMENTS_PATH="${1:-data/rag/documents}"
CONFIG_PATH="${2:-configs/rag/default.yaml}"

echo "Indexing documents from: $DOCUMENTS_PATH"
echo "Using config: $CONFIG_PATH"

uv run python -m src.rag.cli index "$DOCUMENTS_PATH" --config "$CONFIG_PATH"
