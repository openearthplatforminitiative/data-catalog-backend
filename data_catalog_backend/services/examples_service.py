from typing import List

from sqlalchemy.orm import joinedload

from data_catalog_backend.models import Examples, CodeExamples, Code

from sqlalchemy import select


class ExamplesService:
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

    def get_examples(self, example_id: int) -> List[Examples]:
        stmt = select(Examples).where(Examples.example_id == example_id)
        return self.session.scalars(stmt).unique().all()

    def create_code_examples(self, code_examples: List[CodeExamples]) -> List[CodeExamples]:
        created_code_examples = []
        for code_example in code_examples:
            new_code_example = CodeExamples(
                title=code_example.title,
                description=code_example.description
            )
            self.session.add(new_code_example)
            self.session.commit()

            for code in code_example.code:
                new_code = Code(
                    language=code.language,
                    source=code.source,
                    examples_id=new_code_example.examples_id
                )
                self.session.add(new_code)

            created_code_examples.append(new_code_example)

        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

        return created_code_examples

    def get_code_examples(self, code_example_id: int) -> List[CodeExamples]:
        stmt = select(CodeExamples).where(CodeExamples.examples_id == code_example_id).options(joinedload(CodeExamples.code))
        return self.session.scalars(stmt).unique().all()
