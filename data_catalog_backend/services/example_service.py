import uuid
from datetime import datetime
from typing import List

from data_catalog_backend.models import Examples

from sqlalchemy import select

from data_catalog_backend.schemas.User import User
from data_catalog_backend.schemas.example import (
    ExampleResponse,
    ExampleRequest,
    UpdateExampleRequest,
)


class ExampleService:
    def __init__(self, session):
        self.session = session

    def create_examples(
        self, examples: List[ExampleRequest], resource_id: uuid.UUID, user: User
    ) -> List[Examples]:
        created_examples = []
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
        self, example_id: uuid.UUID, example_data: UpdateExampleRequest, user: User
    ) -> Examples:
        example = self.get_example(example_id)

        if example is None:
            raise ValueError(f"Example with id {example_id} not found")

        for key, value in example_data.dict(exclude_unset=True).items():
            if hasattr(example, key) and value is not None:
                setattr(example, key, value)

        setattr(example, "updated_by", user.email)
        setattr(example, "updated_at", datetime.now())

        self.session.commit()
        return example
