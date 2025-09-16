import os
from pathlib import Path


def get_db_url() -> str:
    # Prefer env var; fallback to local SQLite file for dev/tests
    env = os.getenv("DATABASE_URL")
    if env:
        return env
    base_dir = Path(__file__).resolve().parents[1]  # backend/
    db_path = base_dir / "dev.db"
    # absolute path form for sqlite
    return f"sqlite:///{db_path}"


RETRIEVER_BACKEND = os.getenv("RETRIEVER_BACKEND", "tfidf")  # tfidf | chroma | pinecone
