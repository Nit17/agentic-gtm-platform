# Backend (FastAPI)

FastAPI backend for the Agentic GTM Platform.

Key features:
- Health endpoint and versioning
- SQLAlchemy models for contacts and notes (SQLite by default; Postgres supported)
- Retrieval backends: TF-IDF (default), Chroma (in-memory), Pinecone (optional)
- Decision placeholder endpoint
- Email tool endpoint with SendGrid integration (optional; dry-run fallback)

Run locally:
- Create venv and install deps from `requirements.txt`
- Set environment variables as needed; see `.env.example`
- Start API: `uvicorn app.main:app --reload`

Databases:
- Default is SQLite at `backend/dev.db`. Override with `DATABASE_URL` (e.g., Postgres).
- Alembic scaffolding is present for migrations.

Retrievers:
- Choose via `RETRIEVER_BACKEND`: `tfidf` | `chroma` | `pinecone`.
- Pinecone requires: `PINECONE_API_KEY`, `PINECONE_INDEX`, and an existing index (cosine, dimension 512 by default). Adjust `PineconeRetriever` dim if your index differs.

Email tool:
- If `SENDGRID_API_KEY` and `EMAIL_FROM_ADDRESS` are set, `/tools/email/send` will send via SendGrid.
- Without these, the endpoint returns a queued dry-run response so you can test without sending emails.

Next:
- Switch local dev to Postgres and generate initial Alembic migration
- Persist Chroma or adopt a managed vector DB
- Implement richer decision/action planning and additional tool adapters
