import uuid

from sqlalchemy import UUID, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from data_catalog_backend.database import Base
from enum import StrEnum as PyStrEnum

class CodeType(PyStrEnum):
    Java = "java"
    Javascript = "javascript"
    Python = "python"
    Curl = "curl"
    Go = "go"
    Bash = "bash"

class Code(Base):
    __tablename__ = 'code'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for code"
    )
    language: Mapped[str] = mapped_column(String, nullable=True, doc="type")
    source: Mapped[str] = mapped_column(String, nullable=True, doc="code")
    examples_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('code_examples.id'), nullable=True)

    #Relations
    code_examples: Mapped["CodeExamples"] = relationship(back_populates='code')