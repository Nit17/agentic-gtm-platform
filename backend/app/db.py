from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from .settings import get_db_url


DATABASE_URL = get_db_url()

# SQLite needs check_same_thread; for Postgres default pooling is fine
connect_args = {}
if DATABASE_URL.startswith("sqlite"):  # file-based sqlite or sqlite:///:memory:
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args, poolclass=NullPool if DATABASE_URL.startswith("sqlite") else None)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
