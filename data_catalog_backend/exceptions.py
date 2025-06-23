# Python
class ResourceError(Exception):
    """Base exception for resource-related errors."""

    def __init__(self, message: str):
        super().__init__(message)


class LicenseNotFoundError(ResourceError):
    """Raised when a required license is not found."""

    def __init__(self, resource_type: str):
        super().__init__(
            f"License not found and required for resource type: {resource_type}"
        )


class CategoryNotFoundError(ResourceError):
    """Raised when a category is not found."""

    def __init__(self, category_title: str):
        super().__init__(f"Category with title '{category_title}' not found.")


class ProviderNotFoundError(ResourceError):
    """Raised when a provider is not found."""

    def __init__(self, provider_name: str):
        super().__init__(f"Provider with name '{provider_name}' not found.")


class TemporalExtentError(ResourceError):
    """Raised for invalid temporal extent data."""

    def __init__(self, message: str = "Invalid temporal extent data"):
        super().__init__(message)


class SpatialExtentError(ResourceError):
    """Raised for invalid spatial extent data."""

    def __init__(self, message: str = "Invalid spatial extent data"):
        super().__init__(message)
