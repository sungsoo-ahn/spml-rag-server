# RAG Server Usage Guide

This guide covers how to use the SPML RAG server both in Claude Desktop and via the command line.

## Table of Contents

- [Using in Claude Desktop](#using-in-claude-desktop)
- [Command Line Interface](#command-line-interface)
- [Available MCP Tools](#available-mcp-tools)
- [Search Tips](#search-tips)
- [Administrator Tasks](#administrator-tasks)

## Using in Claude Desktop

Once configured (see [TEAM_SETUP.md](TEAM_SETUP.md)), the RAG server works seamlessly in Claude Desktop conversations.

### Basic Search

Simply ask Claude about topics in your document collection:

```
You: What papers do we have about graph neural networks?

Claude: [Uses search_documents tool automatically]
I found several papers about graph neural networks in the collection...
```

### Specific Questions

Ask detailed questions about specific topics:

```
You: Tell me about the non-backtracking GNN paper

Claude: [Searches and retrieves relevant chunks]
Based on the paper "Non-Backtracking GNN" (arxiv 2310.07430),
the research proposes...
```

### Finding Related Work

```
You: What do we have on machine learning optimization techniques?

Claude: [Searches across all indexed documents]
I found 12 documents related to machine learning optimization...
```

### Citation and Sources

Claude will automatically include source information:

```
Claude: According to the paper "Attention Is All You Need"
(documents/papers/attention.pdf), the transformer architecture...

Sources:
- documents/papers/attention.pdf (relevance: 0.85)
- documents/grants/ml_research_proposal.pdf (relevance: 0.72)
```

## Command Line Interface

The CLI provides direct access to the RAG server without Claude Desktop.

### Basic Commands

```bash
# Search documents
uv run python -m src.rag.cli search "your query"

# View statistics
uv run python -m src.rag.cli stats

# List all indexed documents
uv run python -m src.rag.cli list

# Get info about a specific document
uv run python -m src.rag.cli info "path/to/document.pdf"

# Clear the entire index (careful!)
uv run python -m src.rag.cli clear
```

### Search Options

```bash
# Search with custom parameters
uv run python -m src.rag.cli search "machine learning" \
  --top-k 10 \
  --threshold 0.5

# Detailed output with metadata
uv run python -m src.rag.cli search "neural networks" \
  --verbose

# JSON output for scripting
uv run python -m src.rag.cli search "optimization" \
  --format json
```

**Parameters**:
- `--top-k`: Number of results to return (default: 5)
- `--threshold`: Minimum similarity score 0-1 (default: 0.3)
- `--verbose`: Show detailed metadata
- `--format`: Output format (text or json)

### Statistics

```bash
$ uv run python -m src.rag.cli stats

RAG Server Statistics
=====================
Collection: documents
Total Chunks: 12,550
Unique Documents: 926
ChromaDB Size: ~195MB

Document Types:
  PDF: 782 documents
  DOCX: 98 documents
  PPTX: 32 documents
  Markdown: 14 documents

Indexed: 926 documents
Last Updated: 2026-01-02
```

### Listing Documents

```bash
# List all documents
uv run python -m src.rag.cli list

# Filter by type
uv run python -m src.rag.cli list --type pdf

# Search in filenames
uv run python -m src.rag.cli list --pattern "neural"
```

### Document Information

```bash
# Get details about a specific document
uv run python -m src.rag.cli info "data/rag/documents/papers/attention.pdf"

Document: attention.pdf
Path: data/rag/documents/papers/attention.pdf
Type: PDF
Chunks: 42
Indexed: 2026-01-02 14:30:22
Size: 2.3 MB
```

## Available MCP Tools

When using Claude Desktop, these tools are available via the MCP protocol:

### 1. search_documents

Search for relevant document chunks.

**Parameters**:
- `query` (required): Search query string
- `top_k` (optional): Number of results (default: 5)
- `similarity_threshold` (optional): Minimum similarity 0-1 (default: 0.3)

**Example**:
```python
search_documents(
    query="graph neural networks",
    top_k=5,
    similarity_threshold=0.3
)
```

**Returns**:
```json
{
  "results": [
    {
      "content": "Text chunk from document...",
      "source": "data/rag/documents/papers/gnn_paper.pdf",
      "similarity": 0.87,
      "chunk_index": 5,
      "metadata": {
        "document_type": "pdf"
      }
    }
  ]
}
```

### 2. list_indexed_documents

Get a list of all indexed documents.

**Parameters**: None

**Returns**:
```json
{
  "documents": [
    {
      "path": "data/rag/documents/papers/paper1.pdf",
      "type": "pdf",
      "chunks": 42
    }
  ],
  "total": 926
}
```

### 3. get_document_info

Get metadata about a specific document.

**Parameters**:
- `source_path` (required): Path to the document

**Example**:
```python
get_document_info(
    source_path="data/rag/documents/papers/attention.pdf"
)
```

**Returns**:
```json
{
  "path": "data/rag/documents/papers/attention.pdf",
  "type": "pdf",
  "chunks": 42,
  "indexed_date": "2026-01-02T14:30:22"
}
```

### 4. index_document

Index a new document (admin only - coordinate to avoid conflicts).

**Parameters**:
- `file_path` (required): Path to file to index

**Example**:
```python
index_document(
    file_path="/path/to/new/document.pdf"
)
```

**Returns**:
```json
{
  "success": true,
  "chunks_created": 38,
  "message": "Successfully indexed document.pdf"
}
```

## Search Tips

### Effective Queries

**Good queries**:
- "graph neural network architectures"
- "transformer attention mechanisms"
- "optimization techniques for deep learning"

**Less effective**:
- "paper" (too generic)
- "the" (stop word)
- Single words without context

### Query Types

**Conceptual queries**:
```
"What are the main challenges in representation learning?"
```

**Technical queries**:
```
"How does the attention mechanism work in transformers?"
```

**Finding specific work**:
```
"Papers about non-backtracking operators on graphs"
```

**Comparative queries**:
```
"Differences between GNNs and traditional graph algorithms"
```

### Understanding Similarity Scores

- **0.8-1.0**: Highly relevant, direct match
- **0.6-0.8**: Relevant, good semantic match
- **0.4-0.6**: Somewhat relevant, related concepts
- **0.3-0.4**: Loosely related
- **< 0.3**: Likely not relevant (filtered by default)

### Adjusting Search Parameters

**Broad search** (more results, lower precision):
```bash
uv run python -m src.rag.cli search "neural networks" \
  --top-k 20 \
  --threshold 0.2
```

**Focused search** (fewer results, higher precision):
```bash
uv run python -m src.rag.cli search "transformer architecture" \
  --top-k 3 \
  --threshold 0.7
```

## Administrator Tasks

### Indexing New Documents

**Using the smart indexing script** (recommended):
```bash
# Set environment for Dropbox setup
export DROPBOX_PATH="/Users/YOUR_USERNAME/Dropbox"
export RAG_CONFIG_PATH=configs/rag/dropbox_shared.yaml

# Index new documents (skips already-indexed files)
uv run python scripts/rag/index_new_documents.py --yes

# Dry run to see what would be indexed
uv run python scripts/rag/index_new_documents.py
```

**Using the CLI**:
```bash
# Index a single file
uv run python -m src.rag.cli index path/to/document.pdf

# Index all files in a directory
uv run python -m src.rag.cli index-dir path/to/folder/
```

### Managing the Index

**Check current state**:
```bash
uv run python -m src.rag.cli stats
```

**Clear and rebuild** (use with caution):
```bash
# Clear the entire index
uv run python -m src.rag.cli clear --confirm

# Re-index all documents
uv run python scripts/rag/index_new_documents.py --force
```

### Coordination

When multiple admins need to index:

1. **Communicate**: Announce in team chat before indexing
2. **One at a time**: Only one person should index at a time
3. **Wait for sync**: After indexing, wait for Dropbox to sync
4. **Notify team**: Let team know when new documents are available

### Monitoring Costs

**Check usage**:
```bash
# View indexing stats
uv run python -m src.rag.cli stats --verbose

# Estimate costs for new documents
echo "Number of documents: X"
echo "Estimated tokens: X * 7000 = Y tokens"
echo "Estimated cost: Y / 1000000 * 0.02 = $Z"
```

**Current costs** (as of January 2026):
- Indexing: ~$0.0001 per document
- Queries: ~$0.0001 per search
- Monthly (100 queries/day): ~$0.30

## Troubleshooting

### No Results Returned

```bash
# Check if documents are indexed
uv run python -m src.rag.cli stats

# Try a broader query
uv run python -m src.rag.cli search "machine learning" --threshold 0.2

# Verify ChromaDB is accessible
ls -la ~/Dropbox/SPML/data/spml-rag-server/chroma-db/
```

### Slow Searches

```bash
# Check Dropbox sync status
# Pause Dropbox sync during searches if very slow

# Reduce top-k
uv run python -m src.rag.cli search "query" --top-k 3
```

### API Errors

```bash
# Verify OpenAI API key
echo $OPENAI_API_KEY

# Check API status
curl https://status.openai.com/

# Test with simple query
uv run python -m src.rag.cli search "test" --top-k 1
```

## Best Practices

### For Users

1. **Be specific**: More detailed queries get better results
2. **Iterate**: Try rephrasing if first results aren't helpful
3. **Use context**: Reference previous results in follow-up questions
4. **Check sources**: Verify the cited documents are relevant

### For Administrators

1. **Organize documents**: Use clear folder structure in documents/
2. **Regular backups**: Backup ChromaDB periodically
3. **Monitor costs**: Check OpenAI usage monthly
4. **Document changes**: Note when new documents are added
5. **Coordinate indexing**: Avoid simultaneous indexing operations

## Advanced Usage

### Scripting with CLI

```bash
#!/bin/bash
# Search and save results

QUERY="machine learning optimization"
OUTPUT="search_results.json"

uv run python -m src.rag.cli search "$QUERY" \
  --format json \
  --top-k 10 > "$OUTPUT"

echo "Results saved to $OUTPUT"
```

### Integration with Other Tools

```python
# Python script using the RAG server
from src.rag.retriever import Retriever
from src.rag.config import load_config

config = load_config()
retriever = Retriever(config)

results = retriever.search("neural networks", top_k=5)
for result in results:
    print(f"Source: {result['source']}")
    print(f"Score: {result['similarity']:.2f}")
    print(f"Content: {result['content'][:200]}...")
    print()
```

---

**Need Help?**
- Check [TEAM_SETUP.md](TEAM_SETUP.md) for setup issues
- See [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- Ask in team chat for support

**Last Updated**: January 2026
