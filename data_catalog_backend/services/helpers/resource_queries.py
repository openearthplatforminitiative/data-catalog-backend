import logging

from geoalchemy2.functions import ST_Covers, ST_Intersects
from geoalchemy2.shape import from_shape
from shapely.geometry.geo import shape
from sqlalchemy import or_, case, and_, func, select, literal_column, exists
from sqlalchemy.orm import aliased

from data_catalog_backend.models import (
    Resource,
    SpatialExtent,
    SpatialExtentRequestType,
    Category,
    ResourceCategory,
    Provider,
    ResourceProvider,
)


class ResourceQuery:
    def apply_tag_filters(self, stmt, resources_req):
        if not resources_req.tags:
            return stmt

        logging.info("Filtering by tags")
        tag_filters = []
        for tag in resources_req.tags:
            tag_filters.append(
                or_(
                    Resource.title.ilike(f"%{tag}%"),
                    Resource.abstract.ilike(f"%{tag}%"),
                    exists( # search for tag in keywords, case-insensitive
                        select(literal_column("1"))
                        .select_from(func.unnest(Resource.keywords).alias("keyword"))
                        .where(func.lower(literal_column("keyword")) == func.lower(tag))
                    ),
                    Resource.html_content.ilike(f"%{tag}%"),
                    Resource.spatial_extent.any(
                        SpatialExtent.details.ilike(f"%{tag}%")
                    ),
                    Resource.spatial_extent.any(SpatialExtent.region.ilike(f"%{tag}%")),
                )
            )
        return stmt.where(or_(*tag_filters))

    def apply_type_filters(self, stmt, resources_req):
        if not resources_req.types:
            return stmt

        logging.info("Filtering by types")
        return stmt.where(Resource.type.in_(resources_req.types))

    def apply_category_filters(self, stmt, resources_req):
        if not resources_req.categories:
            return stmt

        logging.info("Filtering by categories")
        FilterResourceCategory = aliased(ResourceCategory)
        return stmt.outerjoin(
            FilterResourceCategory, FilterResourceCategory.resource_id == Resource.id
        ).where(FilterResourceCategory.category_id.in_(resources_req.categories))

    def apply_provider_filters(self, stmt, resources_req):
        if not resources_req.providers:
            return stmt

        logging.info("Filtering by providers")
        return stmt.outerjoin(
            Resource.providers,
        ).where(ResourceProvider.provider_id.in_(resources_req.providers))

    def apply_spatial_filters(self, stmt, resources_req):
        if not resources_req.spatial:
            return stmt

        logging.info("Filtering by spatial extent")
        conditions = []
        if SpatialExtentRequestType.NonSpatial in resources_req.spatial:
            conditions.append(Resource.spatial_extent == None)
        other_types = [
            stype
            for stype in resources_req.spatial
            if stype != SpatialExtentRequestType.NonSpatial
        ]
        if other_types:
            conditions.append(SpatialExtent.type.in_(other_types))
        if conditions:
            stmt = stmt.where(or_(*conditions))
        return stmt

    def apply_features_filters(self, stmt, resources_req):
        if not resources_req.features:
            return stmt

        logging.info("Filtering by features")

        shapely_geoms = [
            from_shape(shape(feature.geometry), srid=4326)
            for feature in resources_req.features
        ]
        covers_conditions = [
            ST_Covers(SpatialExtent.geometry, geom) for geom in shapely_geoms
        ]
        intersects_conditions = [
            ST_Intersects(SpatialExtent.geometry, geom) for geom in shapely_geoms
        ]

        stmt = stmt.add_columns(
            case(
                (SpatialExtent.type == SpatialExtentRequestType.Global, True),
                (or_(*covers_conditions), True),
                else_=False,
            ).label("covers_some"),
            case(
                (SpatialExtent.type == SpatialExtentRequestType.Global, True),
                (and_(*covers_conditions), True),
                else_=False,
            ).label("covers_all"),
            case(
                (SpatialExtent.type == SpatialExtentRequestType.Global, True),
                (or_(*intersects_conditions), True),
                else_=False,
            ).label("intersects_some"),
            case(
                (SpatialExtent.type == SpatialExtentRequestType.Global, True),
                (and_(*intersects_conditions), True),
                else_=False,
            ).label("intersects_all"),
        )

        return stmt.where(
            or_(
                (SpatialExtent.type == SpatialExtentRequestType.Global),
                *intersects_conditions,
                *covers_conditions,
            )
        )
