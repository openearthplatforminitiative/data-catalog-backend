from sqlalchemy import ForeignKey, Table, Column
from data_catalog_backend.database import Base

resource_relation = Table(
    "resource_relation",
    Base.metadata,
    Column("child_id", ForeignKey("resources.id"), primary_key=True),
    Column("parent_id", ForeignKey("resources.id"), primary_key=True),
)
