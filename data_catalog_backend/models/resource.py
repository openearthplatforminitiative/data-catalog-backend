import uuid
from typing import List, Optional
from sqlalchemy import UUID, ForeignKey, String, Date, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from data_catalog_backend.database import Base
from enum import StrEnum as PyStrEnum

from data_catalog_backend.models.resource_resource import ResourceResource


class ResourceType(PyStrEnum):
    Dataset = "DATASET"
    ML_Model = "ML_MODEL"
    API = "API"
    File = "FILE"

class Resource(Base):
    __tablename__ = 'resources'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for Resource"
    )
    title: Mapped[str] = mapped_column(String, nullable=False, doc="Name")
    abstract:  Mapped[str] = mapped_column(String, nullable=False, doc="Description")
    html_content: Mapped[Optional[str]] = mapped_column(String, nullable=True, doc="expanded description")
    resource_url: Mapped[Optional[str]] = mapped_column(String, nullable=True, doc="Resource url")
    documentation_url: Mapped[Optional[str]] = mapped_column(String, nullable=True, doc="documentation url")
    git_url: Mapped[Optional[str]] = mapped_column(String, nullable=True, doc="url github")
    maintenance_and_update_frequency: Mapped[str] = mapped_column(String, nullable=True, doc="how often it updates")
    release_date: Mapped[Optional[Date]] = mapped_column(Date, nullable=True, doc="release date")
    contact: Mapped[str] = mapped_column(String, nullable=True, doc="expanded description")
    keywords: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True, doc="keywords")
    version: Mapped[Optional[str]] = mapped_column(String, nullable=True, doc="resource version")
    type: Mapped[str] = mapped_column(String, nullable=True, doc="type")
    license_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("licenses.id"), nullable=False)

    # Relations
    license: Mapped["License"] = relationship(back_populates="resources")
    spatial_extent: Mapped[List["SpatialExtent"]] = relationship(back_populates="resource")
    temporal_extent: Mapped[List["TemporalExtent"]] = relationship(back_populates="resource")
    used_by: Mapped[List["Resource"]] = relationship("Resource", secondary="resource_resource", primaryjoin=id == ResourceResource.c.based_on, secondaryjoin=id == ResourceResource.c.used_by, back_populates="based_on")
    based_on: Mapped[List["Resource"]] = relationship("Resource", secondary="resource_resource", primaryjoin=id == ResourceResource.c.used_by, secondaryjoin=id == ResourceResource.c.based_on, back_populates="used_by")
    categories: Mapped[List["ResourceCategory"]] = relationship(back_populates="resources")
    providers: Mapped[List["Provider"]] = relationship("Provider", secondary="resource_provider", back_populates="resources")
    code_examples: Mapped[List["CodeExamples"]] = relationship(back_populates="resource")
    examples: Mapped[List["Examples"]] = relationship(back_populates="resource")
