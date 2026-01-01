# Update Your Local Configuration to Use Dropbox

This guide is for **you** (the admin) to switch your local setup to use the Dropbox-synced ChromaDB.

## What Changed

- ✅ ChromaDB copied to Dropbox: `~/Sungsahn0215 Dropbox/SPML/data/rag-chroma-db/`
- ✅ New config created: `configs/rag/dropbox_shared.yaml`
- ✅ Config loader updated to support environment variables
- ✅ Team documentation created in `docs/TEAM_SETUP.md`

## Update Your Claude Desktop Config

Edit your Claude Desktop config file:
- **Location**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Update the `env` section** to add:

```json
{
  "mcpServers": {
    "rag-server": {
      "command": "/Users/sungsoo/.local/bin/uv",
      "args": [
        "run",
        "--directory",
        "/Users/sungsoo/Code/spml-rag-server",
        "python",
        "-m",
        "src.rag.server"
      ],
      "env": {
        "OPENAI_API_KEY": "YOUR_API_KEY",
        "DROPBOX_PATH": "/Users/sungsoo/Sungsahn0215 Dropbox",
        "RAG_CONFIG_PATH": "configs/rag/dropbox_shared.yaml"
      }
    }
  }
}
```

**Key additions**:
- `DROPBOX_PATH`: Points to your Dropbox root
- `RAG_CONFIG_PATH`: Uses the shared config instead of default

## Update Your .env File

Add to `/Users/sungsoo/Code/spml-rag-server/.env`:

```bash
DROPBOX_PATH=/Users/sungsoo/Sungsahn0215 Dropbox
```

## Test the Setup

```bash
# Test from CLI (should show 926 documents)
cd /Users/sungsoo/Code/spml-rag-server
export DROPBOX_PATH="/Users/sungsoo/Sungsahn0215 Dropbox"
export RAG_CONFIG_PATH=configs/rag/dropbox_shared.yaml
uv run python -m src.rag.cli stats
```

Expected output:
```
Total Chunks: 12550
Unique Documents: 926
Persist Directory: /Users/sungsoo/Sungsahn0215 Dropbox/SPML/data/rag-chroma-db
```

## Restart Claude Desktop

1. Quit Claude Desktop completely
2. Reopen Claude Desktop
3. Verify the RAG server connects with the Dropbox database

## Next Steps

### 1. Push to GitHub

```bash
cd /Users/sungsoo/Code/spml-rag-server

# Check what will be committed
git status

# Add the new files
git add configs/rag/dropbox_shared.yaml
git add docs/TEAM_SETUP.md
git add README_RAG.md
git add .env.example
git add src/rag/config.py
git add scripts/rag/index_new_documents.py

# Commit
git commit -m "Add Dropbox-shared RAG server setup

- Add dropbox_shared.yaml config with environment variable support
- Create comprehensive team setup documentation
- Add smart incremental indexing script
- Update README with usage examples and architecture
- Support environment variable expansion in configs"

# Push to your repository
git push origin main  # or your branch name
```

### 2. Share with Team

1. Share the Dropbox folder `SPML/data/rag-chroma-db` with team members
2. Send them the GitHub repository URL
3. Point them to `docs/TEAM_SETUP.md`

### 3. Maintain the Shared Database

When adding new documents:

```bash
# Add new files to data/rag/documents/
# Then run the smart indexing script:
export DROPBOX_PATH="/Users/sungsoo/Sungsahn0215 Dropbox"
export RAG_CONFIG_PATH=configs/rag/dropbox_shared.yaml
uv run python scripts/rag/index_new_documents.py --yes
```

This will:
- Only index new files (skip already-indexed ones)
- Update the ChromaDB in Dropbox
- Dropbox will sync to team members automatically

## Important Notes

### Avoiding Conflicts

- **Coordinate indexing**: Let team know when you're adding documents
- **Read-mostly**: Team members should primarily search, not index
- **Sync time**: After indexing, wait for Dropbox to sync before notifying team

### Local ChromaDB

Your old local ChromaDB is still at:
- `/Users/sungsoo/Code/spml-rag-server/data/rag/chroma_db/`

You can delete it once you've verified the Dropbox setup works:

```bash
# AFTER verifying Dropbox setup works
rm -rf /Users/sungsoo/Code/spml-rag-server/data/rag/chroma_db/
```

---

**Ready to go!** Your team can now access the shared RAG server through Dropbox.
