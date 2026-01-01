"""OpenAI embeddings wrapper."""

import os
from typing import List, Optional
from openai import OpenAI
from dotenv import load_dotenv


class OpenAIEmbeddings:
    """Wrapper for OpenAI embeddings API."""

    SUPPORTED_MODELS = [
        "text-embedding-3-small",  # 1536 dimensions
        "text-embedding-3-large",  # 3072 dimensions
        "text-embedding-ada-002",  # 1536 dimensions (legacy)
    ]

    def __init__(
        self, model: str = "text-embedding-3-small", api_key: Optional[str] = None
    ):
        load_dotenv()
        self.model = model
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

        if model not in self.SUPPORTED_MODELS:
            raise ValueError(f"Model {model} not supported")

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        if not texts:
            return []

        # OpenAI API handles batching internally
        response = self.client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]

    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query."""
        return self.embed([text])[0]
