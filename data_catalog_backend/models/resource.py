import uuid
from typing import List, Optional
from sqlalchemy import (
    UUID,
    ForeignKey,
    String,
    Date,
    case,
    literal_column,
    ARRAY,
    Index,
    Boolean,
    select,
    func,
    exists,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, column_property
from data_catalog_backend.database import Base
from enum import StrEnum as PyStrEnum

from data_catalog_backend.models import ResourceCategory, Category
from data_catalog_backend.models.spatial_extent import SpatialExtent
from data_catalog_backend.models.resource_resource import (
    resource_relation,
)


class ResourceType(PyStrEnum):
    Dataset = "DATASET"
    DatasetCollection = "DATASET_COLLECTION"
    ML_Model = "ML_MODEL"
    API = "API"


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for Resource",
    )
    title: Mapped[str] = mapped_column(String, nullable=False, doc="Name")
    abstract: Mapped[str] = mapped_column(String, nullable=False, doc="Description")
    html_content: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="expanded description"
    )
    resource_url: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="Resource url"
    )
    documentation_url: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="documentation url"
    )
    download_url: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="download url"
    )
    openapi_url: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="open api url"
    )
    api_authentication_url: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="api authentication url"
    )
    git_url: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="url github"
    )
    client_library: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, doc="can be used by our client libraries"
    )
    data_hub_url: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="data hub url"
    )
    research_paper_url: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="research paper url"
    )
    maintenance_and_update_frequency: Mapped[str] = mapped_column(
        String, nullable=True, doc="how often it updates"
    )
    release_date: Mapped[Optional[Date]] = mapped_column(
        Date, nullable=True, doc="release date"
    )
    contact: Mapped[str] = mapped_column(
        String, nullable=True, doc="expanded description"
    )
    keywords: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String), nullable=True, doc="keywords"
    )
    version: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="resource version"
    )
    type: Mapped[str] = mapped_column(String, nullable=True, doc="type")
    license_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("licenses.id"), nullable=True
    )

    # Computed properties
    has_spatial_extent: Mapped[bool] = column_property(
        select(exists().where(SpatialExtent.resource_id == id))
        .correlate_except(SpatialExtent)
        .scalar_subquery()
    )

    spatial_extent_type: Mapped[Optional[str]] = column_property(
        select(
            case(
                (
                    func.bool_or(SpatialExtent.type == "GLOBAL"),
                    literal_column("'GLOBAL'"),
                ),
                (func.count(SpatialExtent.id) > 0, literal_column("'REGION'")),
            )
        )
        .where(SpatialExtent.resource_id == id)
        .correlate_except(SpatialExtent)
        .scalar_subquery()
    )

    icon: Mapped[Optional[str]] = column_property(
        select(Category.icon)
        .join(ResourceCategory, Category.id == ResourceCategory.category_id)
        .where(
            ResourceCategory.resource_id == id,
            ResourceCategory.is_main_category.is_(True),
        )
        .correlate_except(ResourceCategory)
        .scalar_subquery()
    )

    # Relations
    license: Mapped["License"] = relationship(back_populates="resources")
    spatial_extent: Mapped[List["SpatialExtent"]] = relationship(
        back_populates="resource"
    )
    temporal_extent: Mapped[List["TemporalExtent"]] = relationship(
        back_populates="resource"
    )
    parents: Mapped[List["Resource"]] = relationship(
        "Resource",
        secondary=resource_relation,
        primaryjoin=id == resource_relation.c.child_id,
        secondaryjoin=id == resource_relation.c.parent_id,
        back_populates="children",
    )
    children: Mapped[List["Resource"]] = relationship(
        "Resource",
        secondary=resource_relation,
        primaryjoin=id == resource_relation.c.parent_id,
        secondaryjoin=id == resource_relation.c.child_id,
        back_populates="parents",
    )
    categories: Mapped[List["ResourceCategory"]] = relationship(
        "ResourceCategory", back_populates="resource"
    )
    providers: Mapped[List["ResourceProvider"]] = relationship(
        "ResourceProvider", back_populates="resource"
    )
    code_examples: Mapped[List["CodeExamples"]] = relationship(
        back_populates="resource"
    )
    examples: Mapped[List["Examples"]] = relationship(back_populates="resource")

    __table_args__ = (
        Index("unique_resource_title_type", "title", "type", unique=True),
    )
