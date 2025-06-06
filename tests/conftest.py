import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data_catalog_backend.database import Base
from data_catalog_backend.dependencies import get_db
from fastapi.testclient import TestClient
from data_catalog_backend.__main__ import app


# PostGIS database URL for testing
POSTGIS_TEST_DATABASE_URL = (
    "postgresql://test_user:test_password@localhost:5433/test_db"
)

# Create a SQLAlchemy engine for the test database
engine = create_engine(POSTGIS_TEST_DATABASE_URL)

# Create a sessionmaker to manage sessions
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables in the test database
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a new database session with a rollback at the end of the test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session, monkeypatch):
    """Create a test client that uses the override_get_db fixture to return a session."""

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
