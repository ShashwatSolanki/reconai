from sqlalchemy.engine import Engine

from app.db import models  # noqa: F401
from app.db.base import Base


def create_schema(engine: Engine) -> None:
    """Create all registered database tables."""
    Base.metadata.create_all(engine)