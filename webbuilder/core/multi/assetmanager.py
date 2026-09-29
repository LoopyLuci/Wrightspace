"""webbuilder.core.multi.assetmanager — Asset manager."""
from __future__ import annotations
import hashlib
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class Asset:
    id: str
    source_path: str
    dest_path: str
    asset_type: str
    hash: str = ""


class AssetManager:
    def __init__(self, root: Optional[str] = None):
        self._assets: Dict[str, Asset] = {}
        self.root = Path(root) if root else Path.cwd() / "assets"
        self.root.mkdir(parents=True, exist_ok=True)

    def add(self, source_path: str, dest_path: str = "") -> Asset:
        src = Path(source_path)
        if not src.exists():
            raise FileNotFoundError(f"Asset not found: {source_path}")
        asset_id = dest_path or src.name
        h = hashlib.sha256()
        with open(src, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        file_hash = h.hexdigest()[:16]
        dest = self.root / asset_id
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        asset = Asset(id=asset_id, source_path=str(src), dest_path=str(dest),
                      asset_type=src.suffix.lstrip("."), hash=file_hash)
        self._assets[asset_id] = asset
        return asset

    def get(self, asset_id: str) -> Optional[Asset]:
        return self._assets.get(asset_id)

    def list(self) -> List[Asset]:
        return list(self._assets.values())

    def get_url(self, asset_id: str) -> str:
        if asset_id in self._assets:
            return f"/assets/{asset_id}"
        return ""

    def optimize(self) -> int:
        count = 0
        for asset in self._assets.values():
            if asset.asset_type in ("png", "jpg", "jpeg", "webp"):
                count += 1
        return count
