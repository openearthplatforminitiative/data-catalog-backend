from sqlalchemy import Column, ForeignKey, Table

from data_catalog_backend.database import Base

ResourceProvider = Table(
    "resource_provider",
    Base.metadata,
    Column("provider_id", ForeignKey('providers.provider_id'), primary_key=True),
    Column("resource_id", ForeignKey('resources.resource_id'), primary_key=True)
)