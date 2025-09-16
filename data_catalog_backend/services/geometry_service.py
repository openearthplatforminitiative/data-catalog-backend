import logging

from sqlalchemy import select

from data_catalog_backend.models import Geometry
from data_catalog_backend.schemas.User import User

from shapely.geometry import shape, GeometryCollection
from geoalchemy2.shape import from_shape

logger = logging.getLogger(__name__)


class GeometryService:
    def __init__(self, session):
        self.session = session

    def get_geometries(self) -> list[Geometry]:
        stmt = select(Geometry)
        return self.session.scalars(stmt).all()

    def get_geometry(self, geometry_id) -> Geometry | None:
        stmt = select(Geometry).where(Geometry.id == geometry_id)
        return self.session.scalars(stmt).unique().one_or_none()

    def create_geometry(self, geometry_req: Geometry, user: User) -> Geometry:
        feature_collection = geometry_req.geometry

        if feature_collection["type"] != "FeatureCollection":
            raise ValueError("Invalid GeoJSON: must be a FeatureCollection")

        if not feature_collection["features"]:
            raise ValueError("FeatureCollection must contain at least one feature")

        geometries = [
            shape(feature["geometry"]) for feature in feature_collection["features"]
        ]

        geometry_collection = GeometryCollection(geometries)
        wkb_element = from_shape(geometry_collection, srid=4326)

        geometry = Geometry(
            name=geometry_req.name,
            geometry=wkb_element,
            created_by=user.email,
        )
        self.session.add(geometry)
        try:
            self.session.commit()
            return geometry
        except Exception as e:
            self.session.rollback()
            raise e

    def update_geometry(self, geometry_id, geometry: Geometry, user: User) -> Geometry:
        existing_geometry = self.get_geometry(geometry_id)
        if not existing_geometry:
            raise ValueError("Geometry not found")

        feature_collection = geometry.geometry

        if feature_collection["type"] != "FeatureCollection":
            raise ValueError("Invalid GeoJSON: must be a FeatureCollection")

        if not feature_collection["features"]:
            raise ValueError("FeatureCollection must contain at least one feature")

        geometries = [
            shape(feature["geometry"]) for feature in feature_collection["features"]
        ]

        geometry_collection = GeometryCollection(geometries)
        wkb_element = from_shape(geometry_collection, srid=4326)

        existing_geometry.name = geometry.name
        existing_geometry.geometry = wkb_element
        existing_geometry.updated_by = user.email

        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

        return geometry

    def get_geometry_by_name(self, name: str) -> Geometry:
        stmt = select(Geometry).where(Geometry.name == name)
        return self.session.scalars(stmt).unique().one_or_none()
