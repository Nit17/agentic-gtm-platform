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

Dockerless Postgres (macOS):
- Option A — Postgres.app
	1) Install Postgres.app from https://postgresapp.com and start a new 16.x server.
	2) Create user and database:
		 - Open psql from Postgres.app and run:
			 - `CREATE USER gtm WITH PASSWORD 'gtm';`
			 - `CREATE DATABASE gtm OWNER gtm;`
			 - `GRANT ALL PRIVILEGES ON DATABASE gtm TO gtm;`
	3) Set env and run migrations:
		 - `export DATABASE_URL=postgresql+psycopg://gtm:gtm@localhost:5432/gtm`
		 - `uv run alembic -c backend/alembic.ini upgrade head` (or use the venv python as below)

- Option B — Homebrew
	1) Install and start Postgres 16:
		 - `brew install postgresql@16`
		 - `brew services start postgresql@16`
		 - Ensure binaries are on PATH (e.g., `export PATH=/opt/homebrew/opt/postgresql@16/bin:$PATH`)
	2) Create user and database:
		 - `createuser gtm --pwprompt` (enter password: gtm)
		 - `createdb gtm -O gtm`
	3) Set env and run migrations:
		 - `export DATABASE_URL=postgresql+psycopg://gtm:gtm@localhost:5432/gtm`
		 - `uv run alembic -c backend/alembic.ini upgrade head` (or use the venv python as below)

Notes:
- If you’re not using `uv`, run migrations with your venv python:
	- `DATABASE_URL=postgresql+psycopg://gtm:gtm@localhost:5432/gtm .venv/bin/python -m alembic -c backend/alembic.ini upgrade head`
- To generate a new migration from models:
	- `DATABASE_URL=... .venv/bin/python -m alembic -c backend/alembic.ini revision --autogenerate -m "<message>"`

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
