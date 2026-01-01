# SPML RAG Server

A Model Context Protocol (MCP) server providing RAG (Retrieval-Augmented Generation) capabilities for Claude Desktop, with support for shared team access via Dropbox.

## Overview

This MCP server indexes and retrieves information from a shared collection of research documents (papers, grants, presentations, etc.) and makes them searchable through Claude Desktop conversations.

### Current Collection
- **926 documents** indexed (~4.4GB)
- **12,550 text chunks** (512 tokens each)
- **~195MB** ChromaDB vector database
- Supports: PDF, DOCX, PPTX, TXT, Markdown
- **Shared via Dropbox**: Both documents and database accessible to all team members

### Features
- Semantic search across all indexed documents
- Source citation with file paths and relevance scores
- Shared access via Dropbox for team collaboration
- Fast retrieval using ChromaDB vector store
- Claude Desktop integration via MCP protocol

## Quick Start

### For Team Members

**See [docs/TEAM_SETUP.md](docs/TEAM_SETUP.md) for complete setup instructions**

Quick version:
```bash
# 1. Clone and install
git clone https://github.com/sungsoo-ahn/spml-rag-server.git
cd spml-rag-server
uv sync

# 2. Configure environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY and DROPBOX_PATH

# 3. Verify Dropbox sync
ls ~/Dropbox/SPML/data/spml-rag-server/

# 4. Configure Claude Desktop (see docs/TEAM_SETUP.md)

# 5. Restart Claude Desktop
```

### For Administrators

```bash
# Index new documents
uv run python scripts/rag/index_new_documents.py --yes

# Check statistics
uv run python -m src.rag.cli stats

# Search from CLI
uv run python -m src.rag.cli search "your query"
```

## Documentation

- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture and design decisions
- **[docs/USAGE.md](docs/USAGE.md)** - Usage guide (CLI and Claude Desktop)
- **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Development and contributing guide
- **[docs/TEAM_SETUP.md](docs/TEAM_SETUP.md)** - Team member setup guide
- **[DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)** - Deployment details
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick reference for common tasks
- **[CLAUDE.md](CLAUDE.md)** - Development guidelines

## Project Structure

| Folder | Purpose |
|--------|---------|
| `src/rag/` | RAG server source code (MCP server, CLI, vector store) |
| `src/rag/extractors/` | Document extractors for different file types |
| `configs/rag/` | YAML configuration files |
| `scripts/rag/` | Utility scripts for indexing and management |
| `docs/` | Documentation and team setup guides |
| `data/` | Local data directory (gitignored) |
| `scratch/` | Temporary work directory (gitignored) |

## Usage in Claude Desktop

Once configured, use the RAG server naturally in conversations:

```
You: What papers do we have about graph neural networks?

Claude: [Uses search_documents tool]
I found several papers about graph neural networks...
```

## CLI Usage

```bash
# Search documents
uv run python -m src.rag.cli search "machine learning" --top-k 5

# View statistics
uv run python -m src.rag.cli stats

# Index new documents
uv run python scripts/rag/index_new_documents.py --yes
```

## Architecture

Each team member runs a local MCP server that connects to:
- **Shared ChromaDB** in Dropbox (`~/Dropbox/SPML/data/spml-rag-server/chroma-db/`)
- **Shared documents** in Dropbox (`~/Dropbox/SPML/data/spml-rag-server/documents/`)
- **OpenAI API** for embeddings (each user needs their own API key)

See [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md) for detailed architecture.

## Contributing

1. Create a feature branch
2. Make your changes
3. Test locally
4. Submit a pull request

## Maintained By

SPML Research Group
Last Updated: January 2026