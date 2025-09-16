# Backend (FastAPI)

Minimal backend to bootstrap the Agentic GTM Platform.

Features (initial):
- Health and version endpoints
- In-memory stores for contacts and notes
- Simple TF-IDF search over notes (no external vector DB yet)
- Skeleton endpoint for decision proposal

Run locally:
- Create venv and install deps (see requirements.txt)
- Start: `uvicorn app.main:app --reload`

Next:
- Replace in-memory with Postgres (SQLAlchemy)
- Add background workers and RAG retriever
- Integrate external tools (email, CRM) via adapters
