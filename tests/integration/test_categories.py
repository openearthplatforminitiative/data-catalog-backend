import pytest
from data_catalog_backend.models import Category


@pytest.mark.usefixtures("seed_database")
def test_get_categories(client, db_session):
    response = client.get("/v1/categories/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    titles = [category["title"] for category in data]
    assert "Test Category 1" in titles
    assert "Test Category 2" in titles


@pytest.mark.usefixtures("seed_database")
def test_get_category_by_id(client, db_session):
    # Get a category from the database
    category = db_session.query(Category).filter_by(title="Test Category 1").first()
    assert category is not None
    response = client.get(f"/v1/categories/{category.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(category.id)
    assert data["title"] == "Test Category 1"
