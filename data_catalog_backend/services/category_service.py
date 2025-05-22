import logging
import uuid

from sqlalchemy import select

from data_catalog_backend.models import Category
from data_catalog_backend.schemas.User import User
from data_catalog_backend.schemas.category import (
    CategoryRequest,
    CategorySummaryResponse,
)

logger = logging.getLogger(__name__)


class CategoryService:
    def __init__(self, session):
        self.session = session

    def get_category(self, category_id: uuid.UUID) -> Category:
        stmt = select(Category).where(Category.id == category_id)
        return self.session.scalars(stmt).unique().one_or_none()

    def get_category_by_title(self, title: str) -> Category:
        stmt = select(Category).where(Category.title == title)
        return self.session.scalars(stmt).unique().one_or_none()

    def get_categories(self) -> list[CategorySummaryResponse]:
        stmt = select(Category)
        return self.session.scalars(stmt).all()

    def create_category(self, category: CategoryRequest, user: User) -> Category:
        category = Category(
            title=category.title,
            abstract=category.abstract,
            icon=category.icon,
            created_by=user.email,
        )
        self.session.add(category)
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        return category

    def update_category(self, category, category_id: uuid.UUID) -> Category:
        existing_category = self.get_category(category_id)
        if not existing_category:
            raise ValueError("Category not found")

        category_data = category.dict()

        for key, value in category_data.items():
            if hasattr(existing_category, key):
                setattr(existing_category, key, value)

        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

        return existing_category
