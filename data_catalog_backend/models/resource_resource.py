from sqlalchemy import Column, ForeignKey, Table

from data_catalog_backend.database import Base

ResourceResource = Table(
    "resource_resource",
    Base.metadata,
    Column('used_by', ForeignKey('resources.id'), primary_key=True),
    Column('based_on', ForeignKey('resources.id'), primary_key=True)
)