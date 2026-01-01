# RAG Server Setup Guide for Team Members

This guide will help you set up the RAG (Retrieval-Augmented Generation) server on your machine to access the shared document collection via Dropbox.

## Prerequisites

1. **Dropbox Account** with access to the `SPML/data/spml-rag-server/chroma-db` folder
2. **Dropbox Desktop App** installed and syncing
3. **Claude Desktop** installed
4. **Python 3.10+** installed
5. **uv** package manager installed ([installation guide](https://github.com/astral-sh/uv))
6. **OpenAI API Key** (get from team lead or create your own)

## Setup Instructions

### Step 1: Clone the Repository

```bash
git clone <REPOSITORY_URL>
cd spml-rag-server
```

### Step 2: Install Dependencies

```bash
# Create virtual environment and install dependencies
uv sync
```

### Step 3: Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add:

```bash
# Your OpenAI API key
OPENAI_API_KEY=sk-proj-...

# Your Dropbox path (adjust based on your OS)
# macOS:
DROPBOX_PATH=/Users/YOUR_USERNAME/Dropbox
# Windows:
# DROPBOX_PATH=C:/Users/YOUR_USERNAME/Dropbox
# Linux:
# DROPBOX_PATH=/home/YOUR_USERNAME/Dropbox
```

**Important**: Replace `YOUR_USERNAME` with your actual username!

### Step 4: Verify Dropbox Sync

Make sure the ChromaDB is synced to your machine:

```bash
# macOS/Linux:
ls -lh ~/Dropbox/SPML/data/spml-rag-server/chroma-db/

# Windows:
dir %USERPROFILE%\Dropbox\SPML\data\spml-rag-server\chroma-db\
```

You should see two directories:
- `chroma-db/` - Vector database (~195MB)
- `documents/` - Source documents (~4.4GB)

### Step 5: Test the RAG Server

Test that you can query the shared database:

```bash
uv run python -m src.rag.cli stats
```

You should see:
```
Vector Store Statistics
- Total Chunks: 12550
- Unique Documents: 926
- Collection: documents
```

Try a search:
```bash
uv run python -m src.rag.cli search "machine learning" --top-k 3
```

### Step 6: Configure Claude Desktop

#### macOS/Linux

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "rag-server": {
      "command": "/Users/YOUR_USERNAME/.local/bin/uv",
      "args": [
        "run",
        "--directory",
        "/PATH/TO/spml-rag-server",
        "python",
        "-m",
        "src.rag.server"
      ],
      "env": {
        "OPENAI_API_KEY": "YOUR_OPENAI_API_KEY",
        "DROPBOX_PATH": "/Users/YOUR_USERNAME/Dropbox",
        "RAG_CONFIG_PATH": "configs/rag/dropbox_shared.yaml"
      }
    }
  }
}
```

#### Windows

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "rag-server": {
      "command": "C:\\Users\\YOUR_USERNAME\\.local\\bin\\uv.exe",
      "args": [
        "run",
        "--directory",
        "C:\\PATH\\TO\\spml-rag-server",
        "python",
        "-m",
        "src.rag.server"
      ],
      "env": {
        "OPENAI_API_KEY": "YOUR_OPENAI_API_KEY",
        "DROPBOX_PATH": "C:\\Users\\YOUR_USERNAME\\Dropbox",
        "RAG_CONFIG_PATH": "configs/rag/dropbox_shared.yaml"
      }
    }
  }
}
```

**Important**:
- Replace `YOUR_USERNAME` with your actual username
- Replace `/PATH/TO/spml-rag-server` with the full path where you cloned the repo
- Replace `YOUR_OPENAI_API_KEY` with your actual API key

#### Finding the `uv` Path

If you're not sure where `uv` is installed:

```bash
# macOS/Linux:
which uv

# Windows (PowerShell):
Get-Command uv
```

### Step 7: Restart Claude Desktop

1. Quit Claude Desktop completely
2. Reopen Claude Desktop
3. Start a new conversation
4. You should now see the RAG server tools available!

## Using the RAG Server

In Claude Desktop, you can now use these tools:

### 1. Search Documents
```
Use the search_documents tool to find information about "graph neural networks"
```

### 2. List Indexed Documents
```
Use the list_indexed_documents tool to see what's available
```

### 3. Get Document Info
```
Use the get_document_info tool for "data/rag/documents/publication/paper.pdf"
```

### 4. Index New Documents (Advanced)
If you have access to add documents:
```
Use the index_document tool to index "/path/to/new/document.pdf"
```

## Troubleshooting

### "No module named 'src'"
- Make sure you're running from the project root directory
- Check that `uv sync` completed successfully

### "ChromaDB not found" or "No documents indexed"
- Verify Dropbox is syncing: Check the Dropbox icon in your system tray
- Wait for sync to complete (the ChromaDB folder is ~195MB)
- Check the `DROPBOX_PATH` in your `.env` file

### "OpenAI API Error"
- Verify your API key is correct in `.env` and `claude_desktop_config.json`
- Check you have credits available in your OpenAI account

### Claude Desktop doesn't show the RAG server
- Check the config file path is correct for your OS
- Verify the `uv` command path is correct
- Look for errors in Claude Desktop logs:
  - macOS: `~/Library/Logs/Claude/mcp*.log`
  - Windows: `%APPDATA%\Claude\logs\mcp*.log`

### "Command not found: uv"
Install uv:
```bash
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell):
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Important Notes

### Read-Only Access
- The shared ChromaDB is primarily for **reading** (searching documents)
- **Avoid** indexing new documents simultaneously with other team members
- Coordinate with the team if you need to add new documents

### Dropbox Sync
- Keep Dropbox running while using the RAG server
- If you see stale results, wait for Dropbox to sync updates
- The ChromaDB is about 195MB - ensure you have enough space

### API Costs
- Each search uses OpenAI's embedding API (~$0.0001 per query)
- Be mindful of usage if using a personal API key
- Consider sharing a team API key (coordinate with team lead)

## Getting Help

If you encounter issues:
1. Check this troubleshooting section first
2. Ask in the team chat
3. Contact the repository maintainer

## Advanced: CLI Usage

You can also use the RAG system from the command line:

```bash
# Search documents
uv run python -m src.rag.cli search "your query" --top-k 5

# Show statistics
uv run python -m src.rag.cli stats

# Index a single file (coordinate with team!)
uv run python -m src.rag.cli index path/to/document.pdf

# Index a directory
uv run python -m src.rag.cli index data/rag/documents --recursive
```

## Repository Structure

```
spml-rag-server/
├── configs/rag/
│   ├── default.yaml           # Local development config
│   └── dropbox_shared.yaml    # Shared Dropbox config
├── src/rag/
│   ├── server.py              # MCP server
│   ├── cli.py                 # CLI commands
│   ├── vector_store.py        # ChromaDB interface
│   └── ...
├── scripts/rag/
│   └── index_new_documents.py # Smart indexing script
└── docs/
    └── TEAM_SETUP.md          # This file
```

---

**Last Updated**: January 2026
