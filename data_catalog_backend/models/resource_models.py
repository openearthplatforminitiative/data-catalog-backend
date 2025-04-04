import resource
import uuid
from typing import List, Optional

from geoalchemy2 import Geometry, WKBElement
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry.geo import mapping, shape

from pydantic import ValidationError
from sqlalchemy import UUID, Column, ForeignKey, String, Date, Table, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from data_catalog_backend.database import Base

class License(Base):
    __tablename__ = 'licenses'

    license_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for License"
    )
    name: Mapped[str] = mapped_column(String, nullable=False, doc="Name")
    url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relations 
    resources: Mapped[List["Resource"]] = relationship(back_populates="license")

class SpatialExtent(Base):
    __tablename__ = 'spatialextents'

    spatial_extent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for Spatial extent"
    )
    type: Mapped[str] = mapped_column(String, nullable=False, doc="type")
    region: Mapped[Optional[str]] = mapped_column(String, nullable=True, doc="region")
    details: Mapped[Optional[str]] = mapped_column(String, nullable=True, doc="details")
    geometry: Mapped[Optional[WKBElement]] = mapped_column(Geometry(geometry_type="GEOMETRY", srid=4326), nullable=True, doc="geometry value")
    spatial_resolution: Mapped[Optional[str]] = mapped_column(String, nullable=True, doc="region")
    resource_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('resources.resource_id'), nullable=False)

    # Relations 
    resource: Mapped["Resource"] = relationship(back_populates="spatial_extent")


    # WKBElement to GeoJSON
    @property
    def geom(self):
        if isinstance(self.geometry, WKBElement):
            return mapping(to_shape(self.geometry))  
        return None

    # GeoJSON to WKBElement
    @geom.setter
    def geom(self, new_value):
        try:
            # Convert GeoJSON-like dictionary to a Shapely geometry object
            if new_value is not None:
                shapely_geometry = shape(new_value.model_dump())

                # Convert Shapely geometry to WKBElement
                self.geometry = from_shape(shapely_geometry, srid=4326)
        except (ValidationError, ValueError) as e:
            raise ValueError("Invalid geometry value.") from e



class TemporalExtent(Base): 
    __tablename__ = 'temporalextents'

    temporal_extent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for temporal extent"
    )
    start_date: Mapped[Date] = mapped_column(Date, nullable=False, doc="start date")
    end_date: Mapped[Date] = mapped_column(Date, nullable=False, doc="end date")
    resource_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('resources.resource_id'), nullable=False)

    #Relations
    resource: Mapped["Resource"] = relationship(back_populates="temporalextent")

linkedto = Table(
    "linkedto",
    Base.metadata,
    Column('usedby', ForeignKey('resources.resource_id'), primary_key=True),
    Column('basedon', ForeignKey('resources.resource_id'), primary_key=True)
)

class HasResources(Base): 
    __tablename__ = 'hasresources'
    has_resources_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for relation between resources and category"
    )
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('categories.category_id'))
    resource_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('resources.resource_id'))
    categories: Mapped["Categories"] = relationship()
    resources: Mapped["Resource"] = relationship()


class Categories(Base):
    __tablename__ = 'categories'
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for category"
    )
    title: Mapped[str] = mapped_column(String, nullable=True, doc="title")
    abstract: Mapped[str] = mapped_column(String, nullable=True, doc="abstract")
    
    # Relations 
    resources: Mapped[List["HasResources"]] = relationship(back_populates="categories")


provides = Table(
    "provides",
    Base.metadata,
    Column("provider_id", ForeignKey('providers.provider_id'), primary_key=True),
    Column("resource_id", ForeignKey('resources.resource_id'), primary_key=True)
)

class Providers(Base):
    __tablename__ = 'providers'

    provider_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for provider"
    )
    name: Mapped[str] = mapped_column(String, nullable=True, doc="name")
    provider_url: Mapped[str] = mapped_column(String, nullable=True, doc="provider url")
    description: Mapped[str] = mapped_column(String, nullable=True, doc="description")
    
    # Relations
    resources: Mapped[List["Resource"]] = relationship(secondary=provides, back_populates="providers")

class CodeExamples(Base):
    __tablename__ = 'codeexamples'
    
    examples_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for code"
    )
    title: Mapped[str] = mapped_column(String, nullable=False, doc="name")
    description: Mapped[str] = mapped_column(String, nullable=True, doc="description")
    resource_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('resources.resource_id'), nullable=True)
    #Relations
    code: Mapped[List["Code"]] = relationship(back_populates='codeexamples')
    resource: Mapped["Resource"] = relationship(back_populates='codeexamples')

class Code(Base): 
    __tablename__ = 'code'

    code_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for code"
    )
    language: Mapped[str] = mapped_column(String, nullable=True, doc="type")
    source: Mapped[str] = mapped_column(String, nullable=True, doc="code")
    examples_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('codeexamples.examples_id'), nullable=True)

    #Relations
    codeexamples: Mapped["CodeExamples"] = relationship(back_populates='code')

class Examples(Base):
    __tablename__ = 'examples'
    example_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for Resource"
    )
    type: Mapped[str] = mapped_column(String, nullable=True, doc="type of examples")
    description: Mapped[str] = mapped_column(String, nullable=True, doc="description")
    example_url: Mapped[str] = mapped_column(String, nullable=True, doc="link to example")
    favicon_url: Mapped[str] = mapped_column(String, nullable=True, doc="link to favicon")
    resource_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('resources.resource_id'), nullable=True)

    #Relations
    resource: Mapped["Resource"] = relationship(back_populates='examples')

class Resource(Base):
    __tablename__ = 'resources'

    resource_id: Mapped[uuid.UUID] = mapped_column(
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
    release_date: Mapped[Date] = mapped_column(Date, nullable=True, doc="release date")
    contact: Mapped[str] = mapped_column(String, nullable=True, doc="expanded description")
    keywords: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True, doc="keywords")
    version: Mapped[Optional[str]] = mapped_column(String, nullable=True, doc="resource version")
    type: Mapped[str] = mapped_column(String, nullable=True, doc="type")
    license_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("licenses.license_id"), nullable=False)


    # Relations     
    license: Mapped["License"] = relationship(back_populates="resources")
    spatial_extent: Mapped[List["SpatialExtent"]] = relationship(back_populates="resource")
    temporalextent: Mapped[List["TemporalExtent"]] = relationship(back_populates="resource")
    usedby: Mapped[List["Resource"]] = relationship("Resource", secondary=linkedto, primaryjoin=resource_id == linkedto.c.basedon, secondaryjoin=resource_id == linkedto.c.usedby, back_populates="basedon")
    basedon: Mapped[List["Resource"]] = relationship("Resource", secondary=linkedto, primaryjoin=resource_id == linkedto.c.usedby, secondaryjoin=resource_id == linkedto.c.basedon, back_populates="usedby")
    categories: Mapped[List["HasResources"]] = relationship(back_populates="resources")
    providers: Mapped[List["Providers"]] = relationship(secondary=provides, back_populates="resources")
    codeexamples: Mapped[List["CodeExamples"]] = relationship(back_populates="resource")
    examples: Mapped[List["Examples"]] = relationship(back_populates="resource")
