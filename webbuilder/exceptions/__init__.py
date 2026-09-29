"""webbuilder.exceptions — Custom exception hierarchy for WebBuilder."""

from __future__ import annotations
from typing import Any, Dict, List, Optional


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
        self.details: Dict[str, Any] = {"field": field}
        super().__init__(f"Validation error [{field}]: {message}")


class ProjectPersistenceError(ProjectError):
    """Raised when project save/load fails."""
    def __init__(self, operation: str, path: str, reason: str):
        self.operation = operation
        self.path = path
        self.reason = reason
        self.details: Dict[str, Any] = {"operation": operation, "path": path}
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
        self.details: Dict[str, Any] = {"filename": filename}
        super().__init__(f"Asset validation error [{filename}]: {reason}")


class AssetStorageError(AssetError):
    """Raised when asset storage fails."""
    def __init__(self, operation: str, reason: str):
        self.operation = operation
        self.details: Dict[str, Any] = {"operation": operation}
        super().__init__(f"Asset storage error {operation}: {reason}")


class DeploymentError(WebBuilderException):
    """Base exception for deployment errors."""
    pass


class DeploymentPlatformNotSupportedError(DeploymentError):
    """Raised when a deployment platform is not supported."""
    def __init__(self, platform: str, supported: List[str]):
        self.platform = platform
        self.supported = supported
        self.details: Dict[str, Any] = {"platform": platform, "supported": supported}
        super().__init__(f"Platform '{platform}' not supported. Supported: {', '.join(supported)}")


class ExportError(WebBuilderException):
    """Base exception for export errors."""
    pass


class ExportFormatNotSupportedError(ExportError):
    """Raised when an export format is not supported."""
    def __init__(self, fmt: str, supported: List[str]):
        self.format = fmt
        self.supported = supported
        self.details: Dict[str, Any] = {"format": fmt, "supported": supported}
        super().__init__(f"Export format '{fmt}' not supported. Supported: {', '.join(supported)}")


class AIError(WebBuilderException):
    """Base exception for AI-related errors."""
    pass


class AIModelNotFoundError(AIError):
    """Raised when an AI model is not found."""
    def __init__(self, model_name: str, provider_id: Optional[str] = None):
        self.model_name = model_name
        self.provider_id = provider_id
        self.details: Dict[str, Any] = {"model_name": model_name}
        if provider_id:
            self.details["provider_id"] = provider_id
        msg = f"Model not found: {model_name}"
        if provider_id:
            msg += f" (provider: {provider_id})"
        super().__init__(msg)


class AIAPIError(AIError):
    """Raised when an AI API call fails."""
    def __init__(self, provider_id: str, reason: str, status_code: Optional[int] = None):
        self.provider_id = provider_id
        self.reason = reason
        self.status_code = status_code
        self.details: Dict[str, Any] = {"provider_id": provider_id, "reason": reason}
        if status_code is not None:
            self.details["status_code"] = status_code
        super().__init__(f"AI API error [{provider_id}]: {reason}")


class AIProviderNotFoundError(AIError):
    """Raised when an AI provider is not configured or found."""
    def __init__(self, provider_id: str):
        self.provider_id = provider_id
        super().__init__(f"AI provider not found or not configured: {provider_id}")


class AIRateLimitError(AIError):
    """Raised when an AI provider rate limit is exceeded."""
    def __init__(self, provider_id: str, retry_after: Optional[float] = None):
        self.provider_id = provider_id
        self.retry_after = retry_after
        self.details: Dict[str, Any] = {"provider_id": provider_id}
        if retry_after is not None:
            self.details["retry_after"] = retry_after
        super().__init__(f"Rate limit exceeded for {provider_id}")


class SecurityError(WebBuilderException):
    """Base exception for security-related errors."""
    pass


class PathTraversalError(SecurityError):
    """Raised when a path traversal attempt is detected."""
    def __init__(self, path: str):
        self.path = path
        self.details: Dict[str, Any] = {"path": path}
        super().__init__(f"Path traversal detected: {path}")


class InputSanitizationError(SecurityError):
    """Raised when input sanitization fails."""
    def __init__(self, field: str, reason: str):
        self.field = field
        self.details: Dict[str, Any] = {"field": field}
        super().__init__(f"Input sanitization error [{field}]: {reason}")


class SchemaValidationError(SecurityError):
    """Raised when schema validation fails."""
    def __init__(self, schema: str, data: Dict[str, Any], errors: List[str]):
        self.schema = schema
        self.data = data
        self.errors = errors
        self.details: Dict[str, Any] = {"schema": schema, "errors": errors}
        super().__init__(f"Schema validation failed for '{schema}': {len(errors)} error(s)")