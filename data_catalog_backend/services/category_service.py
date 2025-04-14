import logging
import uuid
from typing import Union

from sqlalchemy import select

from data_catalog_backend.models import Category
from data_catalog_backend.schemas.category import CategoryRequest, CategorySummaryResponse

logger = logging.getLogger(__name__)

class CategoryService: 
    def __init__(self, session):
        self.session = session

    def get_category(self, category_id: uuid.UUID) -> Category:
        stmt = select(Category).where(Category.id == category_id)
        return self.session.scalars(stmt).unique().one_or_none()

    def get_categories(self) -> list[CategorySummaryResponse]:
        stmt = select(Category)
        return self.session.scalars(stmt).all()

    def create_category(self, category: CategoryRequest) -> Category:
        category = Category(
            title = category.title,
            abstract=category.abstract,
            icon=category.icon,
        )
        self.session.add(category)
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        return category