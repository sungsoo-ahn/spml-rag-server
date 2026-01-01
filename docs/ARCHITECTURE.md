# RAG Server Architecture

This document describes the architecture, design decisions, and technical details of the SPML RAG server.

## System Overview

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
                │  Dropbox    │ ← Shared across team
                │   Folder    │
                └──────┬──────┘
                       │
                ┌──────┴──────┬─────────────┐
                │             │             │
        ┌───────▼────────┐ ┌─▼──────────┐  │
        │   ChromaDB     │ │ Documents  │  │
        │ (chroma-db/)   │ │ (~4.4GB)   │  │
        └────────────────┘ └────────────┘  │
                                           │
                                     spml-rag-server/
```

## Architecture Components

### 1. Local MCP Server (per user)

Each team member runs their own MCP server instance that:
- Connects to Claude Desktop via MCP protocol
- Reads from shared Dropbox-synced ChromaDB
- Uses their own OpenAI API key for embeddings
- Provides document search capabilities to Claude

**Location**: `src/rag/server.py`

### 2. Shared Storage (Dropbox)

**Unified Dropbox Structure**:
```
~/Dropbox/SPML/data/spml-rag-server/
├── chroma-db/          # Vector database (~195MB)
│   └── ...             # ChromaDB internal files
└── documents/          # Source documents (~4.4GB)
    ├── papers/
    ├── grants/
    ├── presentations/
    └── ...
```

**Why Unified Structure?**
- Both database and documents in one location
- Easier to share and manage
- Single sync point for all data
- Simpler backup and migration

### 3. ChromaDB Vector Store

**Storage**: Persistent ChromaDB instance in Dropbox
**Size**: ~195MB (for 12,550 chunks from 926 documents)
**Collection**: Single collection named "documents"

**Metadata per chunk**:
- `source` - Original file path
- `chunk_index` - Position in document
- `document_type` - File type (pdf, docx, etc.)

**Location**: `src/rag/vector_store.py`

### 4. Document Processing Pipeline

```
Document File
    ↓
Extractor (file type specific)
    ↓
Raw Text + Metadata
    ↓
Chunker (512 token chunks)
    ↓
Text Chunks
    ↓
Embeddings (OpenAI text-embedding-3-small)
    ↓
ChromaDB Storage
```

**Components**:
- `src/rag/document_processor.py` - Coordinates extraction
- `src/rag/extractors/` - File type specific extractors
- `src/rag/chunker.py` - Text chunking logic
- `src/rag/embeddings.py` - OpenAI embedding interface

## Design Decisions

### Why Dropbox + Local MCP Servers?

**Advantages**:
- ✅ No server infrastructure to maintain
- ✅ Simple setup for team members
- ✅ Works seamlessly with MCP protocol
- ✅ Low latency (local server)
- ✅ Automatic synchronization
- ✅ No authentication complexity
- ✅ Built-in version history (Dropbox)

**Trade-offs**:
- ⚠️ ChromaDB not optimized for concurrent writes
  - Mitigation: Read-mostly workload (searches >> indexing)
  - Coordination: Single admin handles indexing
- ⚠️ Requires Dropbox access
  - Acceptable: Team already uses Dropbox
- ⚠️ Each user needs OpenAI API key
  - Acceptable: Low cost per user (~$0.30/month)

### Alternatives Considered

1. **ChromaDB Server**
   - Better for concurrent writes
   - More complex setup
   - Requires server maintenance
   - Not necessary for read-heavy workload

2. **Centralized MCP Server**
   - Doesn't fit MCP model (local servers)
   - Would require authentication
   - Single point of failure

3. **S3 + Read-Only ChromaDB**
   - No Dropbox dependency
   - More complex setup
   - Requires AWS credentials
   - Additional cost

**Decision**: Dropbox + Local MCP is optimal for our use case (read-heavy, small team, minimal maintenance).

### Why ChromaDB?

- Simple Python API
- Persistent storage
- Good performance for our scale (10k+ chunks)
- Built-in similarity search
- Works well with filesystem sync

### Why 512 Token Chunks?

- Balances context vs. granularity
- Fits well within Claude's context window
- Good semantic coherence for most documents
- Tested and works well for research papers

## Data Flow

### Indexing New Documents

```
1. Admin adds files to documents/ folder
2. Run: scripts/rag/index_new_documents.py
3. For each new document:
   a. Extract text using appropriate extractor
   b. Split into 512-token chunks
   c. Generate embeddings via OpenAI
   d. Store in ChromaDB with metadata
4. Dropbox syncs updated ChromaDB to team
```

### Document Retrieval

```
1. User asks question in Claude Desktop
2. Claude invokes search_documents MCP tool
3. MCP server:
   a. Embeds query via OpenAI
   b. Searches ChromaDB for similar chunks
   c. Filters by similarity threshold
   d. Returns top-k results with metadata
4. Claude uses retrieved context in response
```

## Performance Characteristics

### Indexing Performance

- **Speed**: ~10-50 documents/minute (varies by file type)
- **Cost**: ~$0.0001 per document average
- **Bottleneck**: OpenAI API rate limits

### Query Performance

- **Latency**: ~200-500ms per search
  - 50-100ms: OpenAI embedding API
  - 50-100ms: ChromaDB search
  - 50-300ms: Network/overhead
- **Cost**: ~$0.0001 per query
- **Throughput**: Limited by OpenAI rate limits

### Storage

- **Documents**: ~4.4GB (926 files)
- **Vector DB**: ~195MB (12,550 chunks)
- **Ratio**: ~22:1 compression (documents to vectors)

## Scalability Considerations

### Current Limits

- **Documents**: 926 (can scale to 10,000+ easily)
- **Chunks**: 12,550 (ChromaDB handles millions)
- **Team size**: Small (5-10 users optimal)

### When to Reconsider Architecture

If you experience:
- **Frequent write conflicts**: Move to ChromaDB server
- **Large team (20+ users)**: Consider centralized server
- **High query volume**: Add caching layer
- **Very large corpus (100k+ docs)**: Consider distributed search

## Security Model

### Threat Model

**Protected against**:
- Accidental data exposure (gitignore, no commits)
- API key leakage (env files not committed)

**Not protected against**:
- Malicious team members (trusted team assumed)
- Dropbox account compromise (use 2FA)

### Best Practices

1. **API Keys**: Each user uses own OpenAI key
2. **Dropbox**: Team-only sharing, 2FA enabled
3. **Sensitive Documents**: Review before indexing
4. **Access Control**: Dropbox folder permissions

## Monitoring and Maintenance

### Health Checks

```bash
# Check ChromaDB
uv run python -m src.rag.cli stats

# Test search
uv run python -m src.rag.cli search "test query"

# Verify Dropbox sync
ls -lh ~/Dropbox/SPML/data/spml-rag-server/
```

### Backup Strategy

**Primary**: Dropbox automatic sync
- 30-day version history
- Automatic recovery

**Additional** (recommended):
```bash
# Periodic backup of ChromaDB
cp -R ~/Dropbox/SPML/data/spml-rag-server/chroma-db ~/backups/rag-chroma-$(date +%Y%m%d)
```

### Cost Monitoring

**Indexing** (one-time per document):
- Current: 926 docs × ~6.9k tokens/doc = ~6.4M tokens
- Cost: ~$0.13 total (using text-embedding-3-small)

**Querying** (ongoing):
- Per query: ~100 tokens × $0.02/1M = ~$0.0001
- 100 queries/day × 30 days = ~$0.30/month/user

**Total ongoing cost**: Very low (~$0.30-1.00/month total for team)

## Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-proj-...           # For embeddings

# Optional (for Dropbox setup)
DROPBOX_PATH=/Users/username/Dropbox
```

### Config Files

**configs/rag/default.yaml** - Local development:
```yaml
chroma_db_path: "data/rag/chroma_db"
documents_path: "data/rag/documents"
```

**configs/rag/dropbox_shared.yaml** - Team shared:
```yaml
chroma_db_path: "${DROPBOX_PATH}/SPML/data/spml-rag-server/chroma-db"
documents_path: "${DROPBOX_PATH}/SPML/data/spml-rag-server/documents"
```

### Switching Configurations

```bash
# Via environment variable
export RAG_CONFIG_PATH=configs/rag/dropbox_shared.yaml
uv run python -m src.rag.cli stats

# Default: configs/rag/default.yaml
```

## Troubleshooting

### Common Issues

**ChromaDB not found**
- Check Dropbox sync status
- Verify `DROPBOX_PATH` environment variable
- Wait for initial sync to complete

**OpenAI API errors**
- Verify API key in `.env`
- Check API credits/quota
- Check rate limits

**MCP server not appearing**
- Check Claude Desktop config syntax
- Verify absolute paths (not relative)
- Check logs: `~/Library/Logs/Claude/mcp*.log` (macOS)

**Search returns no results**
- Check ChromaDB has documents: `uv run python -m src.rag.cli stats`
- Try broader search query
- Lower similarity threshold

### Debug Mode

```bash
# Enable debug logging
export RAG_DEBUG=1
uv run python -m src.rag.cli search "test"
```

## Future Enhancements

Potential improvements:

- [ ] Document update detection (reindex changed files)
- [ ] Multi-language support
- [ ] Custom chunking strategies per document type
- [ ] Usage analytics dashboard
- [ ] Web interface (optional)
- [ ] Metadata filtering in searches
- [ ] Document preview in results
- [ ] Hybrid search (semantic + keyword)

---

**Last Updated**: January 2026
**Maintained By**: SPML Research Group
