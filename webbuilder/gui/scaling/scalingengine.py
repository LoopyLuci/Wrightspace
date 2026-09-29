"""webbuilder.gui.scaling.scalingengine — Scaling engine for adaptive WebBuilder UI.

Provides device-aware scaling that maintains layout fidelity across
screen sizes, DPI settings, and display densities.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import sys


@dataclass
class ScalingMetrics:
    """Runtime scaling metrics used by all widgets."""
    scale_factor: float = 1.0
    base_dpi: int = 96
    effective_dpi: int = 96
    pixel_ratio: float = 1.0
    font_scale: float = 1.0
    icon_scale: float = 1.0
    min_width: int = 320
    min_height: int = 240
    target_width: int = 1280
    target_height: int = 720
    is_touch: bool = False
    is_high_dpi: bool = False
    sidebar_width: int = 0
    right_panel_width: int = 0


@dataclass
class WindowConstraints:
    """Window size constraints."""
    min_width: int = 800
    min_height: int = 600
    max_width: int = 3840
    max_height: int = 2160
    preferred_width: int = 1280
    preferred_height: int = 720


class ScalingEngine:
    """Adaptive scaling engine for cross-device UI fidelity.

    Reads system DPI, pixel ratio, and monitor geometry to compute
    per-widget scaling factors. Persists user overrides.
    """

    _instance: Optional[ScalingEngine] = None

    def __init__(self):
        self._metrics = ScalingMetrics()
        self._constraints = WindowConstraints()
        self._scale_factor = 1.0
        self._load_preferences()

    @classmethod
    def instance(cls) -> ScalingEngine:
        """Get or create the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_preferences(self) -> None:
        """Load user scaling preferences from config."""
        pass

    @classmethod
    def reset_singleton(cls) -> None:
        """Reset for testing only."""
        cls._instance = None

    def calculate_metrics(self, width: int, height: int) -> ScalingMetrics:
        """Calculate scaling metrics for given screen dimensions."""
        width_ratio = width / self._metrics.target_width
        height_ratio = height / self._metrics.target_height
        raw = min(width_ratio, height_ratio)
        self._scale_factor = max(min(raw, 2.5), 0.4)
        self._metrics.scale_factor = self._scale_factor
        self._metrics.sidebar_width = max(150, round(200 * self._scale_factor))
        self._metrics.right_panel_width = max(200, round(280 * self._scale_factor))
        return self._metrics

    def compute_scale(self, available_width: int, available_height: int) -> float:
        if available_width <= 0 or available_height <= 0:
            return 1.0
        width_ratio = available_width / self._metrics.target_width
        height_ratio = available_height / self._metrics.target_height
        raw = min(width_ratio, height_ratio)
        scaled = max(raw, 0.4)
        return min(scaled, 2.5)

    def compute_dpi_aware_scale(self) -> float:
        """Compute scale factor derived from system DPI."""
        if sys.platform == "win32":
            try:
                import ctypes
                user32 = ctypes.windll.user32
                dpi = user32.GetDpiForSystem()
                base = 96
                return dpi / base
            except Exception:
                pass
        return 1.0

    def scale_value(self, value: float) -> float:
        """Scale a value by the current scale factor."""
        return round(value * self._scale_factor, 2)

    def scale_font(self, point_size: int) -> int:
        """Return a DPI-scaled point size, snapped to integer."""
        scaled = point_size * self._metrics.font_scale
        return max(8, min(72, round(scaled)))

    def scale_icon_size(self, base_size: int) -> int:
        """Return an icon size scaled by the icon scale factor."""
        return max(12, round(base_size * self._metrics.icon_scale))

    def fit_canvas(self, widget_width: int, widget_height: int,
                   available_width: int, available_height: int) -> tuple[float, float, float]:
        scale = min(
            available_width / max(1, widget_width),
            available_height / max(1, widget_height),
            1.5,
        )
        scale = max(scale, 0.25)
        offset_x = (available_width - widget_width * scale) / 2
        offset_y = (available_height - widget_height * scale) / 2
        return scale, offset_x, offset_y

    def apply_constraints(self, width: int, height: int) -> tuple[int, int]:
        w = max(self._constraints.min_width, min(width, self._constraints.max_width))
        h = max(self._constraints.min_height, min(height, self._constraints.max_height))
        return w, h

    def update_metrics(self) -> None:
        dpi_scale = self.compute_dpi_aware_scale()
        self._metrics.effective_dpi = round(96 * dpi_scale)
        self._metrics.pixel_ratio = dpi_scale
        self._metrics.font_scale = dpi_scale
        self._metrics.icon_scale = min(dpi_scale, 1.5)
        self._metrics.is_high_dpi = dpi_scale >= 1.25

    def get_stylesheet(self) -> str:
        sf = self._scale_factor
        sidebar = max(150, round(200 * sf))
        right_panel = max(200, round(280 * sf))
        font_size = max(10, round(12 * sf))
        btn_padding = max(6, round(10 * sf))
        return (
            f"QMainWindow {{ background: #1e1e2e; }}\n"
            f"QPushButton {{ padding: {btn_padding}px; font-size: {font_size}px; "
            f"background: #313244; color: #cdd6f4; border-radius: 4px; }}\n"
            f"QPushButton:hover {{ background: #45475a; }}\n"
            f"QWidget#sidebar {{ min-width: {sidebar}px; max-width: {sidebar}px; "
            f"background: #181825; }}\n"
            f"QWidget#rightPanel {{ min-width: {right_panel}px; max-width: {right_panel}px; "
            f"background: #181825; }}\n"
        )

    @property
    def metrics(self) -> ScalingMetrics:
        return self._metrics

    @property
    def constraints(self) -> WindowConstraints:
        return self._constraints
