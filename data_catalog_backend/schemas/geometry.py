from typing import List

from geojson_pydantic import FeatureCollection
from pydantic import Field

from data_catalog_backend.schemas.basemodel import BaseModel


class GeometryRequest(BaseModel):
    name: str = Field(description="Unique name for geometry")
    geometry: FeatureCollection = Field(description="GeoJSON FeatureCollection")
