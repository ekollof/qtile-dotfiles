#!/usr/bin/env python3
"""
DPI awareness utilities for qtile configuration
Automatically scales fonts, bars, and widgets based on display DPI
"""

import os
import subprocess
from pathlib import Path

from libqtile.log_utils import logger


class DPIManager:
    """Manages DPI detection and scaling calculations"""

    def __init__(self) -> None:
        self._dpi = None
        self._scale_factor = None
        # Don't call detect_dpi() in __init__ to make testing easier

    def detect_dpi(self) -> float:
        """
        @brief Detect current display DPI using multiple fallback methods
        @return Detected DPI value, or fallback value if detection fails
        """
        if self._dpi is not None:
            return self._dpi

        # Try methods in order of preference
        self._dpi = self._detect_with_fallbacks()
        return self._dpi

    def _detect_with_fallbacks(self) -> float:
        """
        @brief Try multiple DPI detection methods with fallbacks
        @return DPI value from first successful method or fallback
        """
        detection_methods = [
            self._try_xdpyinfo,
            self._try_xrandr,
            self._try_xresources,
            self._try_environment,
            self._use_fallback,
        ]

        for method in detection_methods:
            dpi = method()
            if dpi is not None:
                return dpi

        # This should never happen since _use_fallback always returns a value
        return 96.0

    def _try_xdpyinfo(self) -> float | None:
        """
        @brief Try to get DPI from xdpyinfo command
        @return DPI value if successful, None otherwise
        @throws subprocess.TimeoutExpired if command times out
        """
        try:
            result = subprocess.run(
                ["xdpyinfo"], capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "dots per inch" in line.lower():
                        # Parse: "resolution:    96x96 dots per inch"
                        dpi_part = line.split("resolution:")[1].strip()
                        x_dpi = float(dpi_part.split("x")[0].strip())
                        logger.info(f"Detected DPI via xdpyinfo: {x_dpi}")
                        return x_dpi
        except (
            subprocess.TimeoutExpired,
            FileNotFoundError,
            ValueError,
            IndexError,
        ):
            pass
        return None

    def _try_xrandr(self) -> float | None:
        """
        @brief Try to get DPI from xrandr physical dimensions
        @return Calculated DPI based on screen resolution and physical size, None if unavailable
        @throws subprocess.TimeoutExpired if xrandr command times out
        """
        try:
            result = subprocess.run(
                ["xrandr", "--query"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if (
                        " connected primary " in line or " connected " in line
                    ) and "mm x " in line:
                        dpi = self._parse_xrandr_line(line)
                        if dpi:
                            logger.info(f"Detected DPI via xrandr: {dpi}")
                            return dpi
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return None

    def _parse_xrandr_line(self, line: str) -> float | None:
        """
        @brief Parse xrandr output line to extract DPI from resolution and dimensions
        @param line Single line of xrandr output containing monitor information
        @return Calculated DPI value, None if parsing fails
        """
        parts = line.split()
        resolution_part = None
        mm_part = None

        # Find resolution part (e.g., "1920x1080+0+0" -> "1920x1080")
        for _i, part in enumerate(parts):
            if (
                "x" in part
                and part.replace("x", "").replace("+", "").replace("-", "").isdigit()
            ):
                resolution_part = part.split("+")[0]  # Get resolution before position
                break

        # Find physical dimensions (e.g., "597mm x 336mm")
        for i, part in enumerate(parts):
            if (
                part.endswith("mm")
                and i + 2 < len(parts)
                and parts[i + 1] == "x"
                and parts[i + 2].endswith("mm")
            ):
                mm_part = [parts[i], parts[i + 1], parts[i + 2]]
                break

        if resolution_part and mm_part and len(mm_part) >= 3:
            try:
                # Extract pixel width and physical width in millimeters
                width_px = int(resolution_part.split("x")[0])
                width_mm = float(mm_part[0].replace("mm", ""))
                # Calculate DPI: pixels per inch = pixels / (mm / 25.4 mm/inch)
                return round(width_px / (width_mm / 25.4))
            except (ValueError, IndexError):
                pass
        return None

    def _try_xresources(self) -> float | None:
        """Try to get DPI from .Xresources"""
        try:
            xresources_path = Path("~/.Xresources").expanduser()
            if xresources_path.exists():
                with open(xresources_path) as f:
                    for line in f:
                        if line.strip().startswith("Xft.dpi:"):
                            parts = line.split(":")
                            if len(parts) >= 2:
                                dpi_str = parts[1].strip()
                                dpi = float(dpi_str)
                                logger.info(f"Detected DPI via .Xresources: {dpi}")
                                return dpi
        except (FileNotFoundError, ValueError, IndexError):
            pass
        return None

    def _try_environment(self) -> float | None:
        """Try to get DPI from environment variables"""
        env_dpi = os.getenv("QT_SCALE_FACTOR")
        if env_dpi:
            try:
                scale = float(env_dpi)
                dpi = 96 * scale  # Assume base 96 DPI
                logger.info(f"Detected DPI via QT_SCALE_FACTOR: {dpi}")
                return dpi
            except ValueError:
                pass
        return None

    def _use_fallback(self) -> float:
        """Use fallback DPI value"""
        logger.info("Using fallback DPI: 96.0")
        return 96.0

    @property
    def dpi(self) -> float:
        """Get current DPI"""
        if self._dpi is None:
            self.detect_dpi()
        return self._dpi or 96.0

    @property
    def scale_factor(self) -> float:
        """Get scale factor relative to 96 DPI"""
        if self._scale_factor is None:
            self._scale_factor = self.dpi / 96.0
        return self._scale_factor

    def scale(self, base_size: int | float) -> int:
        """
        @brief Scale a size value based on current DPI
        @param base_size The base size to scale (at 96 DPI)
        @return Scaled size rounded to nearest integer, minimum 1
        """
        return max(1, round(base_size * self.scale_factor))

    def scale_font(self, base_font_size: int | float) -> int:
        """
        @brief Scale font size with better rounding for readability
        @param base_font_size The base font size to scale
        @return Scaled font size with intelligent rounding for readability
        """
        scaled = base_font_size * self.scale_factor

        # Apply intelligent rounding based on size ranges for better readability
        if scaled < 8:
            return 8  # Minimum readable font size
        elif scaled < 12:
            return int(scaled)  # Small fonts: truncate for crispness
        else:
            return round(scaled)  # Larger fonts: round normally

    def get_scaling_info(self) -> dict[str, str | float | int]:
        """
        @brief Get comprehensive scaling information for debugging and configuration
        @return Dictionary containing DPI, scale factor, category, and recommended sizes
        """
        return {
            "dpi": self.dpi,
            "scale_factor": self.scale_factor,
            "category": self._get_dpi_category(),
            "recommended_font_base": self._get_recommended_base_font(),
            "bar_height": self.scale(28),
            "icon_size": self.scale(16),
            "margin": self.scale(4),
        }

    def _get_dpi_category(self) -> str:
        """Categorize DPI level"""
        if self.dpi < 120:
            return "Standard DPI"
        elif self.dpi < 180:
            return "High DPI"
        elif self.dpi < 240:
            return "Very High DPI"
        else:
            return "Ultra High DPI"

    def _get_recommended_base_font(self) -> int:
        """Get recommended base font size"""
        if self.dpi < 120:
            return 12
        elif self.dpi < 180:
            return 14
        else:
            return 16


# Global DPI manager instance
_dpi_manager = None


def get_dpi_manager() -> DPIManager:
    """
    @brief Get the global DPI manager instance
    @return Singleton DPIManager instance
    """
    global _dpi_manager
    if _dpi_manager is None:
        _dpi_manager = DPIManager()
    return _dpi_manager


def scale_size(size: int | float) -> int:
    """
    @brief Convenience function to scale a size
    @param size The base size to scale at 96 DPI
    @return DPI-scaled size as integer
    """
    return get_dpi_manager().scale(size)


def scale_font(font_size: int | float) -> int:
    """
    @brief Convenience function to scale a font size
    @param font_size The base font size to scale
    @return DPI-scaled font size with intelligent rounding
    """
    return get_dpi_manager().scale_font(font_size)


def get_dpi() -> float:
    """
    @brief Convenience function to get current DPI
    @return Current system DPI value
    """
    return get_dpi_manager().dpi


def get_scale_factor() -> float:
    """
    @brief Convenience function to get scale factor relative to 96 DPI
    @return Scale factor (1.0 = 96 DPI, 2.0 = 192 DPI, etc.)
    """
    return get_dpi_manager().scale_factor
