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
    ) -> List[CodeExamples]:
        created_code_examples = []
        for code_example in code_examples:
            new_code_example = CodeExamples(
                title=code_example.title,
                description=code_example.description,
                created_by=user.email,
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

    def update_code_example(self, example_data) -> CodeExamples:
        print(example_data["id"])
        code_example = self.session.get(CodeExamples, example_data["id"])
        print("code_example: ", code_example)
        if not code_example:
            raise ValueError("Code example not found")

        for key, value in example_data.items():
            if hasattr(code_example, key):
                print(f"Updating {key} to {value}")
                try:
                    if key == "code":
                        print("ree")
                        for code, new_code_data in zip(code_example.code, value):
                            for code_key, code_value in new_code_data.items():
                                if hasattr(code, code_key):
                                    setattr(code, code_key, code_value)
                    setattr(code_example, key, value)
                except Exception as e:
                    print(f"Error updating {key}: {e}")
                    raise e
                print(f"Updated {key}: {getattr(code_example, key)}")

        self.session.commit()
        return code_example
