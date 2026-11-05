import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Matches the postgres service in your Module 9 docker-compose.yml.
# Tests can override this with the DATABASE_URL environment variable.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/fastapi_db",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """Yield a database session and close it when the request is done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()