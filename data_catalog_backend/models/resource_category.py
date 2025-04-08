from sqlalchemy import ForeignKey, Column, Table

from data_catalog_backend.database import Base

ResourceCategory = Table(
    "resource_category",
    Base.metadata,
    Column("category_id", ForeignKey('categories.id'), primary_key=True),
    Column("resource_id", ForeignKey('resources.id'), primary_key=True)
)