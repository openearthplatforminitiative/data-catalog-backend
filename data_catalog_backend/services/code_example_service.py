import uuid
from typing import List

from sqlalchemy.orm import joinedload

from data_catalog_backend.models import CodeExamples, Code

from sqlalchemy import select

from data_catalog_backend.schemas.User import User


class CodeExampleService:
    def __init__(self, session):
        self.session = session

    def create_code_examples(
        self, code_examples: List[CodeExamples], user: User
        self, code_examples: List[CodeExamples], resource_id: uuid.UUID
    ) -> List[CodeExamples]:
        created_code_examples = []
        for code_example in code_examples:
            new_code_example = CodeExamples(
                title=code_example.title,
                description=code_example.description,
                created_by=user.email,
                title=code_example.title,
                description=code_example.description,
                resource_id=resource_id,
            )
            self.session.add(new_code_example)
            self.session.commit()

            for code in code_example.code:
                new_code = Code(
                    language=code.language,
                    source=code.source,
                    examples_id=new_code_example.id,
                    created_by=user.email,
                )
                self.session.add(new_code)

            created_code_examples.append(new_code_example)

        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

        return created_code_examples

    def get_code_examples(self, id: int) -> List[CodeExamples]:
        stmt = (
            select(CodeExamples)
            .where(CodeExamples.id == id)
            .options(joinedload(CodeExamples.code))
        )
        return self.session.scalars(stmt).unique().all()

    def get_code_example(self, id: uuid.UUID) -> CodeExamples:
        stmt = (
            select(CodeExamples)
            .where(CodeExamples.id == id)
            .options(joinedload(CodeExamples.code))
        )
        return self.session.scalars(stmt).unique().first()

    def update_code_example(
        self, resource_id, code_example_id, example_data
    ) -> CodeExamples:
        code_example = self.get_code_example(code_example_id)
        if not code_example:
            raise ValueError("Code example not found")

        # Update attributes directly on the ORM instance
        code_example.title = example_data.title
        code_example.description = example_data.description
        code_example.resource_id = resource_id

        # Update nested code objects if necessary
        for code, new_code_data in zip(code_example.code, example_data.code):
            code.language = new_code_data.language
            code.source = new_code_data.source

        self.session.commit()
        return code_example
