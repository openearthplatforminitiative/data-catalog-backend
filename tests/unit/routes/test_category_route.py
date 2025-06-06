import uuid
from unittest.mock import MagicMock
import pytest

from data_catalog_backend.__main__ import app
from data_catalog_backend.routes.v1 import category_routes
from data_catalog_backend.schemas.category import (
    CategorySummaryResponse,
    CategoryResponse,
)
from tests.conftest import client


@pytest.fixture
def category_id() -> uuid.UUID:
    """Generate a category ID."""
    return uuid.uuid4()


@pytest.fixture
def mock_category_service(category_id):
    mock_service = MagicMock()
    mock_service.get_categories.return_value = [
        CategorySummaryResponse(
            id=category_id,
            title="Test Category",
            icon="icon.png",
            abstract="some abstract",
        )
    ]
    mock_service.get_category.return_value = CategoryResponse(
        id=category_id,
        title="Test Category",
        icon="icon.png",
        abstract="desc",
        resources=[],
    )
    return mock_service


@pytest.fixture(autouse=True)
def override_category_service(mock_category_service):
    app.dependency_overrides[category_routes.get_category_service] = (
        lambda: mock_category_service
    )
    yield
    app.dependency_overrides = {}


def test_get_categories(client):
    response = client.get("/v1/categories/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["title"] == "Test Category"


def test_get_category(client, category_id):
    response = client.get(f"/v1/categories/{category_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Category"
