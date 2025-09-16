from typing import List, Dict, Any
from sqlalchemy.orm import Session
import chromadb
from chromadb.utils import embedding_functions
from .. import models


class ChromaRetriever:
    def __init__(self, collection_name: str = "notes"):
        self.client = chromadb.Client()  # default in-memory persistent dir under ~/.chromadb
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_functions.DefaultEmbeddingFunction(),
        )

    def _sync_collection(self, db: Session):
        # naive sync: clear and re-add all notes
        self.collection.delete(where={})
        notes: List[models.Note] = db.query(models.Note).all()
        if not notes:
            return
        ids = [str(n.id) for n in notes]
        docs = [n.text for n in notes]
        metadatas = [{"contact_id": n.contact_id} for n in notes]
        self.collection.add(ids=ids, documents=docs, metadatas=metadatas)

    def search(self, db: Session, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        self._sync_collection(db)
        res = self.collection.query(query_texts=[query], n_results=limit)
        results: List[Dict[str, Any]] = []
        ids = res.get("ids", [[]])[0]
        docs = res.get("documents", [[]])[0]
        dists = res.get("distances", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        for i in range(len(ids)):
            results.append({
                "id": int(ids[i]),
                "contact_id": metas[i].get("contact_id") if metas and i < len(metas) else None,
                "text_excerpt": docs[i][:240] if docs and i < len(docs) else "",
                "score": float(1.0 - dists[i]) if dists and i < len(dists) else 0.0,
            })
        return results
