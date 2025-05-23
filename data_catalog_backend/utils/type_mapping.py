import uuid
from datetime import date
from geojson_pydantic.geometries import Geometry

type_mapping = {
    "STRING": str,
    "INTEGER": int,
    "FLOAT": float,
    "BOOLEAN": bool,
    "DATE": date,
    "ENUM": str,
    "UUID": uuid.UUID,
    "GEOMETRY": Geometry,
}
