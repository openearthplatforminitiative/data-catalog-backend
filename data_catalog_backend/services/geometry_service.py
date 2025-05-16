import logging

from sqlalchemy import select

from data_catalog_backend.models import Geometry
from data_catalog_backend.schemas.geometry import GeometryRequest

from shapely.geometry import shape, GeometryCollection
from geoalchemy2.shape import from_shape

logger = logging.getLogger(__name__)


class GeometryService:
    def __init__(self, session):
        self.session = session

    def create_geometry(self, geometry_req: GeometryRequest) -> None:
        features = geometry_req.geometry
        geometries = [shape(feature.geometry) for feature in features]
        combined_geometry = GeometryCollection(geometries)
        wkb_element = from_shape(combined_geometry, srid=4326)

        geometry = Geometry(
            name=geometry_req.name,
            geometry=wkb_element,
        )
        self.session.add(geometry)
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_geometry_by_name(self, name: str) -> Geometry:
        stmt = select(Geometry).where(Geometry.name == name)
        return self.session.scalars(stmt).unique().one_or_none()
