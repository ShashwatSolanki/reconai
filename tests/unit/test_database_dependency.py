from collections.abc import Generator

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.dependencies import get_db
from app.db.schema import create_schema


def test_get_db_yields_configured_session() -> None:
    engine = create_engine("sqlite:///:memory:")
    create_schema(engine)

    session_factory = sessionmaker(
        bind=engine,
        class_=Session,
        expire_on_commit=False,
    )

    def override_get_db() -> Generator[Session]:
        with session_factory() as session:
            yield session

    app = FastAPI()

    @app.get("/test")
    def test_endpoint(db: Session = Depends(get_db)) -> dict[str, bool]:  # noqa: B008
        return {"bound_to_test_engine": db.bind is engine}

    app.dependency_overrides[get_db] = override_get_db

    try:
        response = TestClient(app).get("/test")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"bound_to_test_engine": True}