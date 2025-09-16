from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from .store import store


_vectorizer = TfidfVectorizer(stop_words="english")
_corpus_cache: List[str] = []
_matrix = None


def _rebuild_index():
	global _matrix, _corpus_cache
	_corpus_cache = [n.text for n in store.notes]
	if _corpus_cache:
		_matrix = _vectorizer.fit_transform(_corpus_cache)
	else:
		_matrix = None


def search_notes(query: str, limit: int = 5):
	if _matrix is None:
		_rebuild_index()
	if not _corpus_cache:
		return []

	q_vec = _vectorizer.transform([query])
	scores = (q_vec * _matrix.T).toarray().ravel()
	ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)

	results = []
	for idx, score in ranked[:limit]:
		note = store.notes[idx]
		results.append({
			"id": note.id,
			"contact_id": note.contact_id,
			"text_excerpt": note.text[:240],
			"score": float(score),
		})
	return results


# Rebuild index whenever a note is added (simple hook)
orig_create_note = store.create_note


def create_note_hook(note):
	res = orig_create_note(note)
	_rebuild_index()
	return res


store.create_note = create_note_hook  # type: ignore
