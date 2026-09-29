"""webbuilder.exceptions — Custom exception hierarchy for WebBuilder."""

from __future__ import annotations


class WebBuilderException(Exception):
    """Base exception for all WebBuilder errors."""
    pass


class ProjectError(WebBuilderException):
    """Base exception for project-related errors."""
    pass


class ProjectNotFoundError(ProjectError):
    """Raised when a project is not found."""
    def __init__(self, project_id: str, message: str = ""):
        self.project_id = project_id
        super().__init__(message or f"Project not found: {project_id}")


class ProjectValidationError(ProjectError):
    """Raised when project validation fails."""
    def __init__(self, field: str, message: str):
        self.field = field
        self.details = {"field": field}
        super().__init__(f"Validation error [{field}]: {message}")


class ProjectPersistenceError(ProjectError):
    """Raised when project save/load fails."""
    def __init__(self, operation: str, path: str, reason: str):
        self.operation = operation
        self.path = path
        self.reason = reason
        self.details = {"operation": operation, "path": path}
        super().__init__(f"Persistence error {operation} at {path}: {reason}")


class AssetError(WebBuilderException):
    """Base exception for asset-related errors."""
    pass


class AssetNotFoundError(AssetError):
    """Raised when an asset is not found."""
    def __init__(self, asset_id: str):
        self.asset_id = asset_id
        super().__init__(f"Asset not found: {asset_id}")


class AssetValidationError(AssetError):
    """Raised when asset validation fails."""
    def __init__(self, filename: str, reason: str):
        self.filename = filename
        self.details = {"filename": filename}
        super().__init__(f"Asset validation error [{filename}]: {reason}")


class AssetStorageError(AssetError):
    """Raised when asset storage fails."""
    def __init__(self, operation: str, reason: str):
        self.operation = operation
        self.details = {"operation": operation}
        super().__init__(f"Asset storage error {operation}: {reason}")


class DeploymentError(WebBuilderException):
    """Base exception for deployment errors."""
    pass


class DeploymentPlatformNotSupportedError(DeploymentError):
    """Raised when a deployment platform is not supported."""
    def __init__(self, platform: str, supported: list[str]):
        self.platform = platform
        self.supported = supported
        self.details = {"platform": platform, "supported": supported}
        super().__init__(f"Platform '{platform}' not supported. Supported: {', '.join(supported)}")


class ExportError(WebBuilderException):
    """Base exception for export errors."""
    pass


class ExportFormatNotSupportedError(ExportError):
    """Raised when an export format is not supported."""
    def __init__(self, fmt: str, supported: list[str]):
        self.format = fmt
        self.supported = supported
        self.details = {"format": fmt, "supported": supported}
        super().__init__(f"Export format '{fmt}' not supported. Supported: {', '.join(supported)}")


class AIError(WebBuilderException):
    """Base exception for AI-related errors."""
    pass


class AIModelNotFoundError(AIError):
    """Raised when an AI model is not found."""
    def __init__(self, model_name: str, provider_id: str | None = None):
        self.model_name = model_name
        self.provider_id = provider_id
        self.details = {"model_name": model_name}
        if provider_id:
            self.details["provider_id"] = provider_id
        msg = f"Model not found: {model_name}"
        if provider_id:
            msg += f" (provider: {provider_id})"
        super().__init__(msg)


class SecurityError(WebBuilderException):
    """Base exception for security-related errors."""
    pass


class PathTraversalError(SecurityError):
    """Raised when a path traversal attempt is detected."""
    def __init__(self, path: str):
        self.path = path
        self.details = {"path": path}
        super().__init__(f"Path traversal detected: {path}")


class InputSanitizationError(SecurityError):
    """Raised when input sanitization fails."""
    def __init__(self, field: str, reason: str):
        self.field = field
        self.details = {"field": field}
        super().__init__(f"Input sanitization error [{field}]: {reason}")


class SchemaValidationError(SecurityError):
    """Raised when schema validation fails."""
    def __init__(self, schema: str, data: dict, errors: list[str]):
        self.schema = schema
        self.data = data
        self.errors = errors
        self.details = {"schema": schema, "errors": errors}
        super().__init__(f"Schema validation failed for '{schema}': {len(errors)} error(s)")
