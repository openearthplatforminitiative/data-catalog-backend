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

    def get_categories(self) -> list[Category]:
        stmt = select(Category)
        categories = self.session.execute(stmt).scalars().all()
        return [
            Category(
                id=category.id,
                title=category.title,
                abstract=category.abstract,
                icon=category.icon or "",
            )
            for category in categories
        ]

    def create_category(self, category: Category, user: User) -> Category:
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

    def delete_category(self, category_id: uuid.UUID, user: User) -> Category:
        category = self.get_category(category_id)

        self.session.delete(category)
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        return category
