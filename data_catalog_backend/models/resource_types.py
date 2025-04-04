from enum import StrEnum as PyStrEnum

class ResourceType(PyStrEnum):
    Dataset = "DATASET"
    ML_Model = "ML_MODEL"
    API = "API"
    File = "FILE"

class SpatialExtentType(PyStrEnum):
    Region = "REGION"
    Global = "GLOBAL"

class CodeType(PyStrEnum):
    Java = "java"
    Javascript = "javascript"
    Python = "python"
    Curl = "curl"
    Go = "go"
    Bash = "bash"
