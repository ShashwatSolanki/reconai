from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def get_db() -> Generator[Session]:
    """Yield a database session and close it after use."""
    with SessionLocal() as session:
        yield session
