import uuid
from datetime import datetime
from typing import List

from data_catalog_backend.models import Examples

from sqlalchemy import select

from data_catalog_backend.schemas.User import User


class ExampleService:
    def __init__(self, session, resource_service):
        self.session = session
        self.resource_service = resource_service

    def create_examples(
        self, examples: List[Examples], resource_id: uuid.UUID, user: User
    ) -> List[Examples]:
        created_examples = []
        resource = self.resource_service.get_resource(resource_id)
        if not resource:
            raise ValueError(f"Resource with ID: {resource_id} not found")

        for example in examples:
            new_example = Examples(
                title=example.title,
                type=example.type,
                description=example.description,
                example_url=example.example_url,
                favicon_url=example.favicon_url,
                created_by=user.email,
                resource_id=resource_id,
            )
            self.session.add(new_example)
            created_examples.append(new_example)

        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

        return created_examples

    def get_examples(self, id: uuid.UUID) -> List[Examples]:
        stmt = select(Examples).where(Examples.id == id)
        return self.session.scalars(stmt).unique().all()

    def get_example(self, id: uuid.UUID) -> Examples:
        stmt = select(Examples).where(Examples.id == id)
        return self.session.scalars(stmt).unique().one_or_none()

    def update_example(
        self, example_id: uuid.UUID, example: Examples, user: User
    ) -> Examples:
        existing_example = self.get_example(example_id)

        if existing_example is None:
            raise ValueError(f"Example with id {example_id} not found")

        for key, value in vars(example).items():
            if hasattr(example, key) and value is not None:
                setattr(example, key, value)

        setattr(example, "updated_by", user.email)
        setattr(example, "updated_at", datetime.now())

        self.session.commit()
        return example
