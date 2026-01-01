# MCP RAG Server - Shared Document Retrieval

A Model Context Protocol (MCP) server that provides RAG (Retrieval-Augmented Generation) capabilities for Claude Desktop, with support for shared team access via Dropbox.

## Overview

This MCP server indexes and retrieves information from a shared collection of research documents (papers, grants, presentations, etc.) and makes them searchable through Claude Desktop conversations.

### Current Collection
- **926 documents** indexed
- **12,550 text chunks** (512 tokens each)
- **~195MB** ChromaDB vector database
- Supports: PDF, DOCX, PPTX, TXT, Markdown

### Features
- 🔍 **Semantic search** across all indexed documents
- 📚 **Source citation** with file paths and relevance scores
- 🔄 **Shared access** via Dropbox for team collaboration
- 🚀 **Fast retrieval** using ChromaDB vector store
- 🤖 **Claude Desktop integration** via MCP protocol

## Quick Start

### For Team Members

If you're joining an existing setup with shared documents:

**👉 See [TEAM_SETUP.md](docs/TEAM_SETUP.md) for complete instructions**

Quick version:
```bash
# 1. Clone and install
git clone <REPOSITORY_URL>
cd mcp-sungsoo
uv sync

# 2. Configure environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY and DROPBOX_PATH

# 3. Verify Dropbox sync
ls ~/Dropbox/SPML/data/rag-chroma-db/

# 4. Configure Claude Desktop (see TEAM_SETUP.md)

# 5. Restart Claude Desktop
```

### For Administrators

Setting up a new instance or managing the shared database:

```bash
# Index new documents
uv run python scripts/rag/index_new_documents.py --yes

# Check statistics
uv run python -m src.rag.cli stats

# Search from CLI
uv run python -m src.rag.cli search "your query"
```

## Architecture

```
┌─────────────────┐
│ Claude Desktop  │
└────────┬────────┘
         │ MCP Protocol
         │
┌────────▼────────┐
│  MCP RAG Server │ (runs locally on each user's machine)
│   src.rag.*     │
└────────┬────────┘
         │
         ├─────────────┐
         │             │
┌────────▼────────┐    │
│  OpenAI API     │    │
│  (embeddings)   │    │
└─────────────────┘    │
                       │
                ┌──────▼──────┐
                │  ChromaDB   │
                │  (Dropbox)  │ ← Shared across team
                └─────────────┘
```

### Why This Architecture?

- **Local MCP servers**: Each user runs their own MCP server for Claude Desktop integration
- **Shared ChromaDB**: Vector database synced via Dropbox for team collaboration
- **Read-mostly workload**: Perfect for Dropbox sync (occasional writes, frequent reads)
- **No infrastructure**: No servers to maintain, no authentication to manage

## Usage Examples

### In Claude Desktop

Once configured, you can use the RAG server naturally in conversations:

```
You: What papers do we have about graph neural networks?

Claude: [Uses search_documents tool]
I found several papers about graph neural networks...

You: Tell me more about the non-backtracking GNN paper

Claude: [Uses search_documents tool with specific query]
Based on the paper "Non-Backtracking GNN" (2310.07430)...
```

### Available MCP Tools

1. **search_documents** - Search indexed documents
   ```python
   search_documents(
       query="graph neural networks",
       top_k=5,
       similarity_threshold=0.3
   )
   ```

2. **list_indexed_documents** - See all available documents
   ```python
   list_indexed_documents()
   ```

3. **get_document_info** - Get metadata about a specific document
   ```python
   get_document_info(source_path="data/rag/documents/paper.pdf")
   ```

4. **index_document** - Add a new document (admin only)
   ```python
   index_document(file_path="/path/to/new/document.pdf")
   ```

### CLI Usage

```bash
# Search documents
uv run python -m src.rag.cli search "machine learning optimization" --top-k 5

# View statistics
uv run python -m src.rag.cli stats

# Index new documents (skips already-indexed files)
uv run python scripts/rag/index_new_documents.py --yes

# Index a specific file
uv run python -m src.rag.cli index path/to/document.pdf

# Clear the entire index (careful!)
uv run python -m src.rag.cli clear
```

## Configuration

### Environment Variables

Create a `.env` file:
```bash
# OpenAI API key (required for embeddings)
OPENAI_API_KEY=sk-proj-...

# Dropbox path (for shared setup)
DROPBOX_PATH=/Users/YOUR_USERNAME/Dropbox
```

### Config Files

- `configs/rag/default.yaml` - Local development (ChromaDB in `data/rag/chroma_db`)
- `configs/rag/dropbox_shared.yaml` - Team shared setup (ChromaDB in Dropbox)

Switch configs via environment variable:
```bash
export RAG_CONFIG_PATH=configs/rag/dropbox_shared.yaml
```

## Project Structure

```
mcp-sungsoo/
├── src/rag/                    # RAG server source code
│   ├── server.py              # MCP server implementation
│   ├── cli.py                 # Command-line interface
│   ├── vector_store.py        # ChromaDB wrapper
│   ├── retriever.py           # Retrieval logic
│   ├── chunker.py             # Document chunking
│   ├── document_processor.py  # Document extraction
│   ├── embeddings.py          # OpenAI embeddings
│   └── extractors/            # File type extractors
│       ├── pdf_extractor.py
│       ├── docx_extractor.py
│       ├── pptx_extractor.py
│       └── ...
├── configs/rag/               # Configuration files
│   ├── default.yaml
│   └── dropbox_shared.yaml
├── scripts/rag/               # Utility scripts
│   └── index_new_documents.py # Smart incremental indexing
├── docs/                      # Documentation
│   └── TEAM_SETUP.md         # Team member setup guide
└── data/rag/                  # Data directory (gitignored)
    ├── documents/             # Source documents
    └── chroma_db/            # Vector database (or Dropbox)
```

## Development

### Adding Support for New File Types

1. Create a new extractor in `src/rag/extractors/`
2. Inherit from `BaseExtractor`
3. Implement `can_handle()` and `extract()` methods
4. Register in `DocumentProcessor`

Example:
```python
from src.rag.extractors.base import BaseExtractor, ExtractedDocument

class MyExtractor(BaseExtractor):
    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == '.myext'

    def extract(self, file_path: Path) -> ExtractedDocument:
        # Your extraction logic
        return ExtractedDocument(...)
```

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run black src/
uv run ruff check src/
```

## Troubleshooting

### Common Issues

**ChromaDB not found**
- Check Dropbox is syncing
- Verify `DROPBOX_PATH` environment variable
- Wait for initial sync (195MB)

**OpenAI API errors**
- Verify API key in `.env`
- Check API credits/quota
- Ensure network connectivity

**MCP server not appearing in Claude Desktop**
- Check `claude_desktop_config.json` syntax
- Verify paths are absolute, not relative
- Check Claude Desktop logs

### Logs

- **macOS**: `~/Library/Logs/Claude/mcp*.log`
- **Windows**: `%APPDATA%\Claude\logs\mcp*.log`

## Cost Estimation

### Indexing Costs
- **Embedding model**: `text-embedding-3-small`
- **Cost**: ~$0.02 per 1M tokens
- **Current collection**: ~6.4M tokens ≈ $0.13 total

### Query Costs
- **Per search**: ~$0.0001 (minimal)
- **Monthly (100 queries/day)**: ~$0.30

## Security Notes

- ⚠️ **API Keys**: Never commit `.env` or `claude_desktop_config.json`
- ⚠️ **Sensitive Documents**: Be mindful of what you index
- ⚠️ **Dropbox Sharing**: Only share with trusted team members
- ⚠️ **Read-Only**: Configure team members for read-only access when possible

## Contributing

1. Create a feature branch
2. Make your changes
3. Test locally
4. Submit a pull request

## License

[Add your license here]

## Contact

[Add contact information or team chat link]

---

**Maintained by**: SPML Research Group
**Last Updated**: January 2026
