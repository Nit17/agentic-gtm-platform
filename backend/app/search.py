from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sqlalchemy.orm import Session
from . import models


def search_notes(db: Session, query: str, limit: int = 5):
    notes: List[models.Note] = db.query(models.Note).all()
    if not notes:
        return []
    corpus = [n.text for n in notes]
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(corpus)
    q_vec = vectorizer.transform([query])
    scores = (q_vec * matrix.T).toarray().ravel()
    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
    results = []
    for idx, score in ranked[:limit]:
        note = notes[idx]
        results.append({
            "id": note.id,
            "contact_id": note.contact_id,
            "text_excerpt": note.text[:240],
            "score": float(score),
        })
    return results
