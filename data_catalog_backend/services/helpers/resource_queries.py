import logging

from geoalchemy2.functions import ST_Covers, ST_Intersects
from geoalchemy2.shape import from_shape
from shapely.geometry.geo import shape
from sqlalchemy import or_, case, and_, func, select, literal_column, exists
from sqlalchemy.orm import aliased
from datetime import datetime

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
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def apply_tag_filters(self, stmt, resources_req):
        if not resources_req.tags:
            return stmt

        self.logger.info("Filtering by tags")
        tag_filters = []
        for tag in resources_req.tags:
            tag_filters.append(
                or_(
                    Resource.title.ilike(f"%{tag}%"),
                    Resource.abstract.ilike(f"%{tag}%"),
                    exists(  # search for tag in keywords, case-insensitive
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
        return stmt.where(and_(*tag_filters))

    def apply_type_filters(self, stmt, resources_req):
        if not resources_req.types:
            return stmt

        self.logger.info("Filtering by types")
        return stmt.where(Resource.type.in_(resources_req.types))

    def apply_category_filters(self, stmt, resources_req):
        if not resources_req.categories:
            return stmt

        self.logger.info("Filtering by categories")
        FilterResourceCategory = aliased(ResourceCategory)
        return stmt.outerjoin(
            FilterResourceCategory, FilterResourceCategory.resource_id == Resource.id
        ).where(FilterResourceCategory.category_id.in_(resources_req.categories))

    def apply_provider_filters(self, stmt, resources_req):
        if not resources_req.providers:
            return stmt

        self.logger.info("Filtering by providers")
        return stmt.outerjoin(
            Resource.providers,
        ).where(ResourceProvider.provider_id.in_(resources_req.providers))

    def apply_spatial_filters(self, stmt, resources_req):
        if not resources_req.spatial:
            return stmt

        self.logger.info("Filtering by spatial extent")

        stmt = stmt.outerjoin(SpatialExtent)

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

        self.logger.info("Filtering by features")

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

        stmt = stmt.outerjoin(SpatialExtent)

        is_global = Resource.spatial_extent_type == SpatialExtentRequestType.Global

        stmt = stmt.add_columns(
            or_(is_global, *covers_conditions).label("covers_some"),
            or_(is_global, and_(*covers_conditions)).label("covers_all"),
            or_(is_global, *intersects_conditions).label("intersects_some"),
            or_(is_global, and_(*intersects_conditions)).label("intersects_all"),
        )

        return stmt.where(
            or_(
                is_global,
                *intersects_conditions,
                *covers_conditions,
            )
        )

    def apply_temporal_filters(self, stmt, resources_req):
        if not resources_req.years:
            return stmt

        logging.info("Filtering by temporal extent")

        from data_catalog_backend.models import TemporalExtent

        TemporalExtentAlias = aliased(TemporalExtent)

        dates = []
        for year in resources_req.years:
            dates.append(datetime.strptime(year, "%Y"))

        current_year = datetime.today().year

        # Outer join TemporalExtent to Resource
        stmt = stmt.outerjoin(
            TemporalExtentAlias, TemporalExtentAlias.resource_id == Resource.id
        )

        # Extract years from request
        request_years = [date.year for date in dates]

        # Build a list of year range checks
        year_within_extent_conditions = []
        for year in request_years:
            start_check = func.extract("year", TemporalExtentAlias.start_date) <= year
            end_check = (
                func.extract(
                    "year",
                    func.coalesce(
                        TemporalExtentAlias.end_date, datetime(current_year, 1, 1)
                    ),
                )
                >= year
            )
            year_within_extent_conditions.append(and_(start_check, end_check))

        # Filter resources where any of the extents match at least one year
        stmt = stmt.where(or_(*year_within_extent_conditions))

        return stmt
