#!/usr/bin/env python3
"""
DPI awareness utilities for qtile configuration
Automatically scales fonts, bars, and widgets based on display DPI
"""

import subprocess
import os
from pathlib import Path
from libqtile.log_utils import logger


class DPIManager:
    """Manages DPI detection and scaling calculations"""

    def __init__(self):
        self._dpi = None
        self._scale_factor = None
        self.detect_dpi()

    def detect_dpi(self) -> float:
        """Detect current display DPI using multiple methods"""
        if self._dpi is not None:
            return self._dpi

        # Try methods in order of preference
        dpi = (self._try_xdpyinfo() or
               self._try_xrandr() or
               self._try_xresources() or
               self._try_environment() or
               self._use_fallback())

        self._dpi = dpi
        return self._dpi

    def _try_xdpyinfo(self) -> float | None:
        """Try to get DPI from xdpyinfo"""
        try:
            result = subprocess.run(['xdpyinfo'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'dots per inch' in line.lower():
                        # Parse: "resolution:    96x96 dots per inch"
                        dpi_part = line.split('resolution:')[1].strip()
                        x_dpi = float(dpi_part.split('x')[0].strip())
                        logger.info(f"Detected DPI via xdpyinfo: {x_dpi}")
                        return x_dpi
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError, IndexError):
            pass
        return None

    def _try_xrandr(self) -> float | None:
        """Try to get DPI from xrandr physical dimensions"""
        try:
            result = subprocess.run(['xrandr', '--query'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if (' connected primary ' in line or ' connected ' in line) and 'mm x ' in line:
                        dpi = self._parse_xrandr_line(line)
                        if dpi:
                            logger.info(f"Detected DPI via xrandr: {dpi}")
                            return dpi
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return None

    def _parse_xrandr_line(self, line: str) -> float | None:
        """Parse xrandr output line to extract DPI"""
        parts = line.split()
        resolution_part = None
        mm_part = None

        for i, part in enumerate(parts):
            if 'x' in part and part.replace('x', '').replace('+', '').replace('-', '').isdigit():
                resolution_part = part.split('+')[0]  # Get resolution before position
            if part.endswith('mm'):
                mm_part = parts[i-2:i+1]  # Get "597mm x 336mm"
                break

        if resolution_part and mm_part and len(mm_part) >= 3:
            try:
                width_px = int(resolution_part.split('x')[0])
                width_mm = float(mm_part[0].replace('mm', ''))
                # Calculate DPI: pixels / (mm / 25.4)
                return round(width_px / (width_mm / 25.4))
            except (ValueError, IndexError):
                pass
        return None

    def _try_xresources(self) -> float | None:
        """Try to get DPI from .Xresources"""
        try:
            xresources_path = Path('~/.Xresources').expanduser()
            if xresources_path.exists():
                with open(xresources_path, 'r') as f:
                    for line in f:
                        if line.strip().startswith('Xft.dpi:'):
                            dpi = float(line.split(':')[1].strip())
                            logger.info(f"Detected DPI via .Xresources: {dpi}")
                            return dpi
        except (FileNotFoundError, ValueError, IndexError):
            pass
        return None

    def _try_environment(self) -> float | None:
        """Try to get DPI from environment variables"""
        env_dpi = os.getenv('QT_SCALE_FACTOR')
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
        """Scale a size value based on current DPI"""
        return max(1, round(base_size * self.scale_factor))

    def scale_font(self, base_font_size: int | float) -> int:
        """Scale font size with better rounding for readability"""
        scaled = base_font_size * self.scale_factor
        # Round to nearest reasonable font size
        if scaled < 8:
            return 8
        elif scaled < 12:
            return int(scaled)
        else:
            return round(scaled)

    def get_scaling_info(self) -> dict[str, str | float | int]:
        """Get comprehensive scaling information"""
        return {
            'dpi': self.dpi,
            'scale_factor': self.scale_factor,
            'category': self._get_dpi_category(),
            'recommended_font_base': self._get_recommended_base_font(),
            'bar_height': self.scale(28),
            'icon_size': self.scale(16),
            'margin': self.scale(4),
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
    """Get the global DPI manager instance"""
    global _dpi_manager
    if _dpi_manager is None:
        _dpi_manager = DPIManager()
    return _dpi_manager

def scale_size(size: int | float) -> int:
    """Convenience function to scale a size"""
    return get_dpi_manager().scale(size)

def scale_font(font_size: int | float) -> int:
    """Convenience function to scale a font size"""
    return get_dpi_manager().scale_font(font_size)

def get_dpi() -> float:
    """Convenience function to get current DPI"""
    return get_dpi_manager().dpi

def get_scale_factor() -> float:
    """Convenience function to get scale factor"""
    return get_dpi_manager().scale_factor
