import logging
import uuid

from sqlalchemy import select

from data_catalog_backend.models import Category
from data_catalog_backend.schemas.User import User
from data_catalog_backend.schemas.category import (
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

    def get_main_category(self, resource_id: uuid.UUID) -> Category:
        from data_catalog_backend.models.resource_category import ResourceCategory

        stmt = (
            select(ResourceCategory.category)
            .where(
                ResourceCategory.resource_id == resource_id,
                ResourceCategory.is_main_category.is_(True),
            )
            .join(Category)
        )
        return self.session.scalars(stmt).unique().one_or_none()

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

    def update_category(
        self, category: Category, category_id: uuid.UUID, user: User
    ) -> Category:

        logger.info(f"Modified objects: {self.session.dirty}")

        existing_category = self.get_category(category_id)
        logger.debug(f"Fetched category: {existing_category}")
        if not existing_category:
            raise ValueError(f"Category with ID: {category_id} not found")

        category.created_by = existing_category.created_by

        for key, value in category.__dict__.items():
            if hasattr(existing_category, key) and value is not None:
                logger.debug(
                    f"Updating {key} from {getattr(existing_category, key)} to {value}"
                )
                setattr(existing_category, key, value)

        existing_category.updated_by = user.email

        try:
            logger.info(f"Session dirty objects before commit: {self.session.dirty}")
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

        return existing_category
