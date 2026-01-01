#!/bin/bash
# Run the RAG MCP server

set -e

CONFIG_PATH="${1:-configs/rag/default.yaml}"

echo "Starting RAG MCP Server..."
echo "Using config: $CONFIG_PATH"

export RAG_CONFIG_PATH="$CONFIG_PATH"
uv run python -m src.rag.server
