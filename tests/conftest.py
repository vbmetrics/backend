from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine

from app.database import get_session
from app.main import app

DATABASE_URL_TEST = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL_TEST, connect_args={"check_same_thread": False})


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture(scope="function", autouse=True)
def create_test_tables():
    # create tables before testing
    SQLModel.metadata.create_all(engine)
    yield
    # delete tables after testing
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    def get_session_override() -> Session:
        return session

    app.dependency_overrides[get_session] = get_session_override

    yield TestClient(app)

    app.dependency_overrides.clear()
