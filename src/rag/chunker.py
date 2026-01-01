"""Text chunking strategies for RAG."""

from dataclasses import dataclass
from typing import List
import tiktoken


@dataclass
class Chunk:
    """Represents a text chunk with metadata."""

    text: str
    chunk_index: int
    source_path: str
    start_char: int
    end_char: int
    token_count: int


class RecursiveChunker:
    """
    Recursive text chunker following RAG best practices.
    Uses hierarchical separators and configurable overlap.
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(
        self,
        chunk_size: int = 512,  # tokens
        chunk_overlap: int = 50,  # tokens (~10% overlap)
        model: str = "text-embedding-3-small",
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.tokenizer = tiktoken.encoding_for_model("gpt-4")  # Compatible with embedding models
        self.separators = self.DEFAULT_SEPARATORS

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.tokenizer.encode(text))

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """Recursively split text using hierarchical separators."""
        if not separators:
            return [text]

        separator = separators[0]
        remaining_separators = separators[1:]

        if not separator:
            # Base case: split by characters (shouldn't normally reach here)
            return [text[i : i + 100] for i in range(0, len(text), 100)]

        splits = text.split(separator)

        # Recombine small splits
        chunks = []
        current_chunk = ""

        for split in splits:
            test_chunk = current_chunk + separator + split if current_chunk else split

            if self.count_tokens(test_chunk) <= self.chunk_size:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk)

                # If single split is too large, recurse with finer separator
                if self.count_tokens(split) > self.chunk_size:
                    sub_chunks = self._split_text(split, remaining_separators)
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = split

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def chunk(self, text: str, source_path: str) -> List[Chunk]:
        """Split text into overlapping chunks."""
        if not text.strip():
            return []

        raw_chunks = self._split_text(text, self.separators)

        # Build chunks with overlap
        chunks = []
        char_position = 0

        for i, chunk_text in enumerate(raw_chunks):
            # Calculate overlap from previous chunk
            if i > 0 and chunks:
                prev_text = chunks[-1].text
                words = prev_text.split()
                overlap_word_count = max(1, len(words) // 10)  # ~10% overlap
                overlap_text = " ".join(words[-overlap_word_count:])
                full_text = overlap_text + " " + chunk_text
            else:
                full_text = chunk_text

            start_char = char_position
            end_char = char_position + len(chunk_text)

            chunks.append(
                Chunk(
                    text=full_text.strip(),
                    chunk_index=i,
                    source_path=source_path,
                    start_char=start_char,
                    end_char=end_char,
                    token_count=self.count_tokens(full_text),
                )
            )

            char_position = end_char

        return chunks
