"""webbuilder.core.multi — Multi-page project management."""
from __future__ import annotations
from webbuilder.core.multi.multipageproject import MultiPageProject
from webbuilder.core.multi.assetmanager import AssetManager, Asset
from webbuilder.core.multi.deploymentmanager import DeploymentManager, DeploymentConfig
__all__ = ["MultiPageProject", "AssetManager", "Asset", "DeploymentManager", "DeploymentConfig"]
