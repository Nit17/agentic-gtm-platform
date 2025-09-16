import os
from pathlib import Path
import pytest


# Ensure tests use an isolated SQLite DB file
backend_dir = Path(__file__).resolve().parents[1]
test_db_path = backend_dir / "test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{test_db_path}"


@pytest.fixture(autouse=True, scope="session")
def setup_test_db():
    # Import after env var set so db engine points at test DB
    from app.db import Base, engine
    # Start from a clean slate
    if test_db_path.exists():
        try:
            test_db_path.unlink()
        except Exception:
            pass
    Base.metadata.create_all(bind=engine)
    yield
    # Teardown
    try:
        if test_db_path.exists():
            test_db_path.unlink()
    except Exception:
        pass
