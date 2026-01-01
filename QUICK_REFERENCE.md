# RAG Server - Quick Reference

## For Administrators

### Index New Documents
```bash
cd /Users/sungsoo/Code/mcp-sungsoo
export DROPBOX_PATH="/Users/sungsoo/Sungsahn0215 Dropbox"
export RAG_CONFIG_PATH=configs/rag/dropbox_shared.yaml

# Smart indexing (skips already-indexed files)
uv run python scripts/rag/index_new_documents.py --yes
```

### Check Stats
```bash
uv run python -m src.rag.cli stats
```

### Search from CLI
```bash
uv run python -m src.rag.cli search "your query" --top-k 5
```

## For Team Members

### Claude Desktop Config Path
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### Required Environment Variables
```bash
OPENAI_API_KEY=sk-proj-...
DROPBOX_PATH=/Users/YOUR_USERNAME/Dropbox
RAG_CONFIG_PATH=configs/rag/dropbox_shared.yaml
```

### Verify Setup
```bash
# Check Dropbox sync
ls ~/Dropbox/SPML/data/rag-chroma-db/chroma.sqlite3

# Test CLI
uv run python -m src.rag.cli stats
```

## Common Commands

### CLI
```bash
# Show stats
uv run python -m src.rag.cli stats

# Search
uv run python -m src.rag.cli search "query" --top-k 5

# Index single file
uv run python -m src.rag.cli index path/to/file.pdf

# Index directory
uv run python -m src.rag.cli index data/rag/documents --recursive

# Clear index (admin only!)
uv run python -m src.rag.cli clear
```

### In Claude Desktop
```
"Search for papers about machine learning"
→ Uses search_documents tool

"What documents do we have?"
→ Uses list_indexed_documents tool

"Tell me about [specific document]"
→ Uses get_document_info tool
```

## File Locations

### Config Files
- Local dev: `configs/rag/default.yaml`
- Team shared: `configs/rag/dropbox_shared.yaml`

### Data
- Source docs: `data/rag/documents/`
- Local ChromaDB: `data/rag/chroma_db/`
- Shared ChromaDB: `~/Dropbox/SPML/data/rag-chroma-db/`

### Documentation
- Team setup: `docs/TEAM_SETUP.md`
- Main README: `README_RAG.md`
- This file: `QUICK_REFERENCE.md`

## Troubleshooting

### ChromaDB not found
```bash
# Check Dropbox sync
ls ~/Dropbox/SPML/data/rag-chroma-db/

# Verify environment variable
echo $DROPBOX_PATH
```

### MCP server not appearing
```bash
# Check Claude Desktop logs
tail -f ~/Library/Logs/Claude/mcp*.log  # macOS
```

### OpenAI API errors
```bash
# Verify API key
echo $OPENAI_API_KEY

# Test embedding
uv run python -c "from openai import OpenAI; print(OpenAI().embeddings.create(input='test', model='text-embedding-3-small'))"
```

## Current Stats

- **Documents**: 926
- **Chunks**: 12,550
- **Size**: ~195MB
- **Model**: text-embedding-3-small
- **Chunk size**: 512 tokens
- **Chunk overlap**: 50 tokens

## Key Files Modified

```
src/rag/config.py              # Added env var support
configs/rag/dropbox_shared.yaml # New shared config
scripts/rag/index_new_documents.py # Smart indexing
docs/TEAM_SETUP.md             # Team instructions
```

## Contact

**Questions?** Check `docs/TEAM_SETUP.md` or contact the admin.

---
Last updated: January 2026
