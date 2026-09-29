"""webbuilder.core.multi.deploymentmanager — Deployment management."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from webbuilder.core import Project


@dataclass
class DeploymentConfig:
    platform: str = "vercel"
    output_dir: str = "./dist"
    build_command: str = "npm run build"
    environment: Dict[str, str] = field(default_factory=dict)


class DeploymentManager:
    def __init__(self, project: Optional[Any] = None):
        self.project = project
        self.configs: Dict[str, DeploymentConfig] = {}
        self._register_defaults()

    def _register_defaults(self):
        for platform in ["vercel", "netlify", "github-pages", "cloudflare", "firebase"]:
            self.configs[platform] = DeploymentConfig(platform=platform)

    def get_supported_platforms(self) -> List[str]:
        return list(self.configs.keys())

    def deploy(self, project: Any, platform: str, output_dir: Optional[Any] = None) -> Dict[str, Any]:
        config = self.configs.get(platform)
        if not config:
            raise ValueError(f"Unsupported platform: {platform}")
        import tempfile
        import json as _json
        config_path = Path(tempfile.mktemp(suffix=".json"))
        config_data = {
            "platform": platform,
            "project": getattr(project, "name", "unknown"),
            "output_dir": config.output_dir,
            "environment": config.environment,
        }
        config_path.write_text(_json.dumps(config_data, indent=2), encoding="utf-8")
        return {
            "status": "ready",
            "config_path": str(config_path),
        }

    def list_platforms(self) -> List[str]:
        return list(self.configs.keys())

    @staticmethod
    def supports(platform: str) -> bool:
        return platform in ["vercel", "netlify", "github-pages", "cloudflare", "firebase"]
