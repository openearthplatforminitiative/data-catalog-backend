import logging
import uuid

from sqlalchemy import select

from data_catalog_backend.models import Category
from data_catalog_backend.models.resource_category import ResourceCategory
from data_catalog_backend.schemas.User import User


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

    def get_additional_categories_by_resource_id(
        self, resource_id: uuid.UUID
    ) -> list[Category]:
        stmt = (
            select(Category)
            .select_from(ResourceCategory)
            .join(Category, ResourceCategory.category_id == Category.id)
            .where(
                ResourceCategory.resource_id == resource_id,
                ResourceCategory.is_main_category.is_(False),
            )
        )
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

        existing_category = self.get_category(category_id)
        if not existing_category:
            raise ValueError(f"Category with ID: {category_id} not found")

        existing_category.title = category.title or existing_category.title
        existing_category.abstract = category.abstract or existing_category.abstract

        existing_category.icon = category.icon or existing_category.icon
        existing_category.updated_by = user.email

        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

        return existing_category

    def delete_category(self, category_id: uuid.UUID, user: User):
        category = self.get_category(category_id)
        if not category:
            raise ValueError(f"Category with ID {category_id} does not exist.")

        if category.resources and len(category.resources) > 0:
            raise ValueError(
                "Cannot delete category with resources. Please remove resources first."
            )
        self.session.delete(category)
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
