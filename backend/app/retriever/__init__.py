from .tfidf_backend import TfidfRetriever
from .chroma_backend import ChromaRetriever
from .pinecone_stub import PineconeRetrieverStub

# Pinecone retriever is optional; avoid import errors when dependency is missing
try:  # pragma: no cover - optional path
    from .pinecone_backend import PineconeRetriever  # type: ignore
except Exception:  # pragma: no cover - optional path
    PineconeRetriever = None  # type: ignore

__all__ = [
    "TfidfRetriever",
    "ChromaRetriever",
    "PineconeRetrieverStub",
    "PineconeRetriever",
]
