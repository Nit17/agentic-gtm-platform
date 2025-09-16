import os
import hashlib
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from .. import models

try:
    from pinecone import Pinecone
except Exception:  # pragma: no cover
    Pinecone = None  # type: ignore


def _hashing_embed(text: str, dim: int = 512) -> List[float]:
    vec = [0.0] * dim
    for tok in text.lower().split():
        h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
        idx = h % dim
        vec[idx] += 1.0
    # L2 normalize
    norm = sum(v * v for v in vec) ** 0.5
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


class PineconeRetriever:
    def __init__(self, dim: int = 512):
        api_key = os.getenv("PINECONE_API_KEY")
        index_name = os.getenv("PINECONE_INDEX")
        if not api_key or not index_name:
            raise RuntimeError("PINECONE_API_KEY and PINECONE_INDEX must be set")
        if Pinecone is None:
            raise RuntimeError("pinecone package not installed")
        self.dim = dim
        self.index_name = index_name
        self.pc = Pinecone(api_key=api_key)
        # Assume index already exists; creating requires cloud/region spec.
        self.index = self.pc.Index(index_name)

    def _sync(self, db: Session):
        # naive full sync
        notes: List[models.Note] = db.query(models.Note).all()
        if not notes:
            return
        vectors = []
        for n in notes:
            vectors.append({
                "id": str(n.id),
                "values": _hashing_embed(n.text, self.dim),
                "metadata": {"contact_id": n.contact_id},
            })
        # Upsert in chunks
        for i in range(0, len(vectors), 100):
            chunk = vectors[i:i+100]
            self.index.upsert(vectors=chunk)

    def search(self, db: Session, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        self._sync(db)
        q = _hashing_embed(query, self.dim)
        res = self.index.query(vector=q, top_k=limit, include_metadata=True)
        results: List[Dict[str, Any]] = []
        for match in res.matches or []:
            results.append({
                "id": int(match.id),
                "contact_id": match.metadata.get("contact_id") if match.metadata else None,
                "text_excerpt": "",  # Pinecone stores vectors only; could join from DB if needed
                "score": float(match.score) if match.score is not None else 0.0,
            })
        return results
