import uuid
from datetime import datetime
from typing import List

from data_catalog_backend.models import Examples

from sqlalchemy import select

from data_catalog_backend.schemas.User import User


class ExampleService:
    def __init__(self, session):
        self.session = session

    def create_examples(
        self, examples_data: List[dict], resource_id: uuid.UUID, user: User
    ) -> List[Examples]:
        created_examples = []

        for example in examples_data:
            new_example = Examples(
                title=example["title"],
                type=example["type"],
                description=example["description"],
                example_url=example["example_url"],
                favicon_url=example["favicon_url"],
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

        existing_example.title = (
            example.title if example.title else existing_example.title
        )
        existing_example.type = example.type if example.type else existing_example.type
        existing_example.description = (
            example.description if example.description else existing_example.description
        )
        existing_example.example_url = (
            example.example_url if example.example_url else existing_example.example_url
        )
        existing_example.favicon_url = (
            example.favicon_url if example.favicon_url else existing_example.favicon_url
        )
        existing_example.updated_by = user.email
        existing_example.updated_at = datetime.now()

        self.session.commit()
        return existing_example
