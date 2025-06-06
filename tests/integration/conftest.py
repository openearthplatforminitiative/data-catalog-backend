import pytest
import uuid
from ..conftest import db_session
from sqlalchemy.orm import Session
from data_catalog_backend.models import Category, Provider, Resource


@pytest.fixture(scope="function")
def seed_database(db_session: Session):
    """Seed the database with test data."""
    # Create test categories
    category1 = Category(
        id=uuid.uuid4(),
        title="Test Category 1",
        icon="icon1.png",
        abstract="Abstract for Test Category 1",
        created_by="test_user",
    )
    category2 = Category(
        id=uuid.uuid4(),
        title="Test Category 2",
        icon="icon2.png",
        abstract="Abstract for Test Category 2",
        created_by="test_user",
    )

    # Create test providers
    provider1 = Provider(
        id=uuid.uuid4(),
        name="Test Provider 1",
        short_name="TP1",
        provider_url="https://provider1.com",
        description="Description for Test Provider 1",
        created_by="test_user",
    )
    provider2 = Provider(
        id=uuid.uuid4(),
        name="Test Provider 2",
        short_name="TP2",
        provider_url="https://provider2.com",
        description="Description for Test Provider 2",
        created_by="test_user",
    )

    # Create test resources
    resource1 = Resource(
        id=uuid.uuid4(),
        title="Test Resource 1",
        abstract="Abstract for Test Resource 1",
        html_content="<p>HTML content for Test Resource 1</p>",
        resource_url="https://resource1.com",
        created_by="test_user",
    )
    resource2 = Resource(
        id=uuid.uuid4(),
        title="Test Resource 2",
        abstract="Abstract for Test Resource 2",
        html_content="<p>HTML content for Test Resource 2</p>",
        resource_url="https://resource2.com",
        created_by="test_user",
    )

    # Add the test data to the session
    db_session.add_all(
        [category1, category2, provider1, provider2, resource1, resource2]
    )
    db_session.commit()

    yield

    # Clean up the test data after the test
    db_session.query(Category).delete()
    db_session.query(Provider).delete()
    db_session.query(Resource).delete()
    db_session.commit()
