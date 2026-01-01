# RAG Server Development Guide

This guide covers how to extend and maintain the SPML RAG server.

## Table of Contents

- [Development Setup](#development-setup)
- [Code Structure](#code-structure)
- [Adding File Type Support](#adding-file-type-support)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Contributing](#contributing)

## Development Setup

### Prerequisites

- Python 3.10+
- uv (package manager)
- OpenAI API key
- Dropbox (for team setup)

### Local Development Environment

```bash
# Clone repository
git clone https://github.com/sungsoo-ahn/spml-rag-server.git
cd spml-rag-server

# Install dependencies
uv sync

# Set up environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# Use local config for development
export RAG_CONFIG_PATH=configs/rag/default.yaml

# Verify setup
uv run python -m src.rag.cli stats
```

### Development Workflow

1. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes**
   - Edit code in `src/rag/`
   - Add tests if needed
   - Update documentation

3. **Test locally**
   ```bash
   # Run tests
   uv run pytest

   # Test CLI
   uv run python -m src.rag.cli search "test query"

   # Test indexing
   uv run python -m src.rag.cli index test_document.pdf
   ```

4. **Submit pull request**
   ```bash
   git add .
   git commit -m "Descriptive commit message"
   git push origin feature/your-feature-name
   ```

## Code Structure

### Module Organization

```
src/rag/
├── __init__.py
├── server.py              # MCP server implementation
├── cli.py                 # Command-line interface
├── config.py              # Configuration loading
├── vector_store.py        # ChromaDB wrapper
├── retriever.py           # Search and retrieval logic
├── embeddings.py          # OpenAI embeddings interface
├── chunker.py             # Text chunking logic
├── document_processor.py  # Document processing coordination
└── extractors/            # File type extractors
    ├── __init__.py
    ├── base.py           # Base extractor class
    ├── pdf_extractor.py  # PDF extraction
    ├── docx_extractor.py # Word document extraction
    ├── pptx_extractor.py # PowerPoint extraction
    ├── text_extractor.py # Plain text extraction
    └── markdown_extractor.py # Markdown extraction
```

### Key Components

**server.py** - MCP Protocol Server
- Implements MCP protocol for Claude Desktop
- Provides tools: search_documents, list_indexed_documents, etc.
- Handles request/response formatting

**cli.py** - Command Line Interface
- Provides CLI commands using Typer
- Commands: search, stats, list, index, clear
- User-friendly output formatting

**vector_store.py** - ChromaDB Interface
- Manages ChromaDB collection
- Handles document storage and retrieval
- Provides search functionality

**retriever.py** - Search Logic
- Coordinates embedding generation and search
- Implements similarity scoring
- Formats search results

**document_processor.py** - Document Processing
- Coordinates file type detection
- Routes to appropriate extractor
- Handles extraction errors

**extractors/** - File Type Handlers
- Each file type has dedicated extractor
- Inherits from BaseExtractor
- Implements extraction logic

## Adding File Type Support

### Step 1: Create Extractor

Create a new file in `src/rag/extractors/`:

```python
# src/rag/extractors/new_type_extractor.py

from pathlib import Path
from typing import Optional
from .base import BaseExtractor, ExtractedDocument

class NewTypeExtractor(BaseExtractor):
    """Extractor for .newtype files."""

    def can_handle(self, file_path: Path) -> bool:
        """Check if this extractor can handle the file."""
        return file_path.suffix.lower() == '.newtype'

    def extract(self, file_path: Path) -> ExtractedDocument:
        """Extract text and metadata from the file."""
        try:
            # Your extraction logic here
            # Example:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

            # Extract metadata
            metadata = {
                'file_type': 'newtype',
                'file_size': file_path.stat().st_size,
                # Add other metadata
            }

            return ExtractedDocument(
                text=text,
                metadata=metadata,
                source_path=str(file_path)
            )

        except Exception as e:
            raise ValueError(f"Failed to extract {file_path}: {e}")
```

### Step 2: Register Extractor

Add your extractor to `src/rag/document_processor.py`:

```python
from src.rag.extractors.new_type_extractor import NewTypeExtractor

class DocumentProcessor:
    def __init__(self):
        self.extractors = [
            PDFExtractor(),
            DocxExtractor(),
            PptxExtractor(),
            MarkdownExtractor(),
            TextExtractor(),
            NewTypeExtractor(),  # Add your extractor
        ]
```

### Step 3: Test Your Extractor

```python
# tests/test_new_type_extractor.py

import pytest
from pathlib import Path
from src.rag.extractors.new_type_extractor import NewTypeExtractor

def test_can_handle_newtype():
    extractor = NewTypeExtractor()
    assert extractor.can_handle(Path("test.newtype"))
    assert not extractor.can_handle(Path("test.pdf"))

def test_extract_newtype():
    extractor = NewTypeExtractor()
    result = extractor.extract(Path("test_files/sample.newtype"))

    assert result.text is not None
    assert len(result.text) > 0
    assert result.metadata['file_type'] == 'newtype'
```

### Step 4: Update Documentation

Add to this document and README.md:
- List of supported file types
- Any special considerations for the new type

### Example: Real Extractor

Here's the actual PDF extractor as reference:

```python
# src/rag/extractors/pdf_extractor.py

from pathlib import Path
from pypdf import PdfReader
from .base import BaseExtractor, ExtractedDocument

class PDFExtractor(BaseExtractor):
    """Extractor for PDF files using pypdf."""

    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == '.pdf'

    def extract(self, file_path: Path) -> ExtractedDocument:
        try:
            reader = PdfReader(file_path)

            # Extract text from all pages
            text_parts = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

            text = "\n\n".join(text_parts)

            # Extract metadata
            metadata = {
                'file_type': 'pdf',
                'num_pages': len(reader.pages),
            }

            # Add PDF metadata if available
            if reader.metadata:
                metadata.update({
                    'title': reader.metadata.get('/Title', ''),
                    'author': reader.metadata.get('/Author', ''),
                })

            return ExtractedDocument(
                text=text,
                metadata=metadata,
                source_path=str(file_path)
            )

        except Exception as e:
            raise ValueError(f"Failed to extract PDF {file_path}: {e}")
```

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_extractors.py

# Run with coverage
uv run pytest --cov=src/rag

# Run with verbose output
uv run pytest -v
```

### Writing Tests

Create test files in `tests/`:

```python
# tests/test_retriever.py

import pytest
from src.rag.retriever import Retriever
from src.rag.config import load_config

@pytest.fixture
def retriever():
    """Create a retriever instance for testing."""
    config = load_config("configs/rag/default.yaml")
    return Retriever(config)

def test_search(retriever):
    """Test basic search functionality."""
    results = retriever.search("test query", top_k=5)

    assert isinstance(results, list)
    assert len(results) <= 5

    if results:
        assert 'content' in results[0]
        assert 'source' in results[0]
        assert 'similarity' in results[0]

def test_search_threshold(retriever):
    """Test similarity threshold filtering."""
    results = retriever.search(
        "test query",
        top_k=10,
        similarity_threshold=0.8
    )

    for result in results:
        assert result['similarity'] >= 0.8
```

### Test Data

Create test documents in `tests/test_data/`:

```
tests/
├── test_data/
│   ├── sample.pdf
│   ├── sample.docx
│   ├── sample.pptx
│   └── sample.md
└── test_extractors.py
```

## Code Quality

### Formatting

```bash
# Format code with black
uv run black src/

# Check formatting
uv run black --check src/

# Sort imports
uv run isort src/
```

### Linting

```bash
# Lint with ruff
uv run ruff check src/

# Fix auto-fixable issues
uv run ruff check --fix src/

# Type checking (if using mypy)
uv run mypy src/
```

### Code Style Guidelines

**Naming Conventions**:
- Classes: `PascalCase` (e.g., `PDFExtractor`)
- Functions/methods: `snake_case` (e.g., `extract_text`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_CHUNK_SIZE`)
- Private: prefix with `_` (e.g., `_internal_method`)

**Documentation**:
- Docstrings for all public classes and functions
- Type hints for function parameters and returns
- Comments for complex logic

**Example**:
```python
def extract_text(file_path: Path, encoding: str = 'utf-8') -> str:
    """Extract text from a file.

    Args:
        file_path: Path to the file to extract
        encoding: Character encoding (default: utf-8)

    Returns:
        Extracted text as string

    Raises:
        ValueError: If file cannot be read
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        raise ValueError(f"Failed to read {file_path}: {e}")
```

### Error Handling

**Fail Fast Philosophy**:
- Validate inputs immediately
- Raise exceptions for invalid states
- No silent failures or fallbacks
- Clear error messages

**Example**:
```python
def index_document(file_path: Path) -> None:
    """Index a document."""
    # Validate input immediately
    if not file_path.exists():
        raise FileNotFoundError(f"Document not found: {file_path}")

    if not file_path.is_file():
        raise ValueError(f"Not a file: {file_path}")

    # Fail fast on unsupported type
    if not self._can_process(file_path):
        raise ValueError(
            f"Unsupported file type: {file_path.suffix}. "
            f"Supported types: {self._supported_types()}"
        )

    # Process document
    # ...
```

## Contributing

### Contribution Workflow

1. **Check existing issues** or create new one
2. **Discuss approach** before major changes
3. **Create feature branch** from main
4. **Implement changes** with tests
5. **Update documentation** as needed
6. **Submit pull request** with clear description

### Pull Request Guidelines

**Good PR Description**:
```markdown
## Summary
Brief description of what this PR does

## Changes
- Added support for .epub files
- Created EpubExtractor class
- Added tests for epub extraction

## Testing
- [ ] Added unit tests
- [ ] Tested locally with sample files
- [ ] Updated documentation

## Related Issues
Closes #123
```

**Checklist**:
- [ ] Code follows project style
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] All tests pass
- [ ] No breaking changes (or discussed)

### Review Process

1. Automated checks run (formatting, tests)
2. Code review by maintainer
3. Address feedback
4. Approval and merge

## Debugging

### Enable Debug Logging

```bash
# Set debug mode
export RAG_DEBUG=1

# Run with debug output
uv run python -m src.rag.cli search "test" --verbose
```

### Common Debug Tasks

**Check ChromaDB State**:
```python
from src.rag.vector_store import VectorStore
from src.rag.config import load_config

config = load_config()
store = VectorStore(config)

print(f"Total documents: {store.collection.count()}")
print(f"Sample: {store.collection.peek()}")
```

**Test Embeddings**:
```python
from src.rag.embeddings import EmbeddingGenerator

generator = EmbeddingGenerator()
embedding = generator.generate("test text")

print(f"Embedding dimensions: {len(embedding)}")
print(f"First 5 values: {embedding[:5]}")
```

**Test Document Processing**:
```python
from src.rag.document_processor import DocumentProcessor

processor = DocumentProcessor()
result = processor.process(Path("test.pdf"))

print(f"Extracted text length: {len(result.text)}")
print(f"Metadata: {result.metadata}")
```

## Deployment

### For Administrators

**Update Shared ChromaDB**:
```bash
# Set Dropbox environment
export DROPBOX_PATH="/Users/YOUR_USERNAME/Dropbox"
export RAG_CONFIG_PATH=configs/rag/dropbox_shared.yaml

# Index new documents
uv run python scripts/rag/index_new_documents.py --yes

# Wait for Dropbox to sync
# Notify team when complete
```

### For Team Members

After code updates:
```bash
# Pull latest changes
git pull origin main

# Update dependencies
uv sync

# Restart Claude Desktop
# (to pick up code changes in MCP server)
```

## Performance Optimization

### Profiling

```python
import cProfile
import pstats

# Profile search operation
profiler = cProfile.Profile()
profiler.enable()

retriever.search("test query", top_k=10)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

### Optimization Tips

1. **Batch embeddings**: Generate embeddings in batches when indexing
2. **Cache frequently used embeddings**: Consider caching common queries
3. **Optimize chunk size**: Balance between granularity and performance
4. **Use appropriate top_k**: Don't retrieve more results than needed

## Maintenance

### Regular Tasks

**Weekly**:
- Check for new documents to index
- Monitor OpenAI API costs

**Monthly**:
- Review ChromaDB size
- Check for duplicate documents
- Update dependencies

**As Needed**:
- Add new file type support
- Optimize chunk strategy
- Update documentation

### Monitoring

```bash
# Check system health
uv run python -m src.rag.cli stats --verbose

# Verify Dropbox sync
ls -lah ~/Dropbox/SPML/data/spml-rag-server/chroma-db/

# Test search functionality
uv run python -m src.rag.cli search "test query"
```

---

**Questions?**
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- See [USAGE.md](USAGE.md) for user guide
- Ask in team chat or create an issue

**Last Updated**: January 2026
