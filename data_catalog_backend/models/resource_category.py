from sqlalchemy import ForeignKey, Column, Table, Boolean, Index

from data_catalog_backend.database import Base

ResourceCategory = Table(
    "resource_category",
    Base.metadata,
    Column("category_id", ForeignKey('categories.id'), primary_key=True),
    Column("resource_id", ForeignKey('resources.id'), primary_key=True),
    Column("is_main_category", Boolean, nullable=False, default=False),
    Index(
        'only_one_main_category_per_resource',
        'resource_id',
        unique=True,
        postgresql_where=(Column("is_main_category") == True)
    )
)