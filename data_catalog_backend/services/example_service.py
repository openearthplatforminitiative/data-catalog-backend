from typing import List

from data_catalog_backend.models import Examples

from sqlalchemy import select


class ExampleService:
    def __init__(self, session):
        self.session = session

    def create_examples(self, examples: List[Examples]) -> List[Examples]:
        created_examples = []
        for example in examples:
            new_example = Examples(
                type=example.type,
                description=example.description,
                example_url=example.example_url,
                favicon_url=example.favicon_url,
            )
            self.session.add(new_example)
            created_examples.append(new_example)

        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

        return created_examples

    def get_examples(self, id: int) -> List[Examples]:
        stmt = select(Examples).where(Examples.id == id)
        return self.session.scalars(stmt).unique().all()
