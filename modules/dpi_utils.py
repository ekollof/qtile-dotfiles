#!/usr/bin/env python3
"""
DPI awareness utilities for qtile configuration
Automatically scales fonts, bars, and widgets based on display DPI
"""

import subprocess
import os
import math
from typing import Dict, Union
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
            
        # Method 1: Try xdpyinfo (most accurate)
        try:
            result = subprocess.run(['xdpyinfo'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'dots per inch' in line.lower():
                        # Parse: "resolution:    96x96 dots per inch"
                        dpi_part = line.split('resolution:')[1].strip()
                        x_dpi = float(dpi_part.split('x')[0].strip())
                        self._dpi = x_dpi
                        logger.info(f"Detected DPI via xdpyinfo: {self._dpi}")
                        return self._dpi
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError, IndexError):
            pass
    
        # Method 2: Try xrandr with physical dimensions
        try:
            result = subprocess.run(['xrandr', '--query'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if ' connected primary ' in line or ' connected ' in line:
                        # Parse: "DP-1 connected primary 2560x1440+0+0 (normal left inverted right x axis y axis) 597mm x 336mm"
                        if 'mm x ' in line:
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
                                    dpi = width_px / (width_mm / 25.4)
                                    self._dpi = round(dpi)
                                    logger.info(f"Detected DPI via xrandr: {self._dpi} (calculated from {width_px}px / {width_mm}mm)")
                                    return self._dpi
                                except (ValueError, IndexError):
                                    continue
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
    
        # Method 3: Check .Xresources
        try:
            xresources_path = os.path.expanduser('~/.Xresources')
            if os.path.exists(xresources_path):
                with open(xresources_path, 'r') as f:
                    for line in f:
                        if line.strip().startswith('Xft.dpi:'):
                            dpi = float(line.split(':')[1].strip())
                            self._dpi = dpi
                            logger.info(f"Detected DPI via .Xresources: {self._dpi}")
                            return self._dpi
        except (FileNotFoundError, ValueError, IndexError):
            pass
    
        # Method 4: Environment variable
        env_dpi = os.environ.get('QT_SCALE_FACTOR')
        if env_dpi:
            try:
                scale = float(env_dpi)
                self._dpi = 96 * scale  # Assume base 96 DPI
                logger.info(f"Detected DPI via QT_SCALE_FACTOR: {self._dpi}")
                return self._dpi
            except ValueError:
                pass
    
        # Fallback: Standard desktop DPI
        self._dpi = 96.0
        logger.info(f"Using fallback DPI: {self._dpi}")
        return self._dpi
    
    @property
    def dpi(self) -> float:
        """Get current DPI"""
        if self._dpi is None:
            self.detect_dpi()
        return self._dpi
    
    @property
    def scale_factor(self) -> float:
        """Get scale factor relative to 96 DPI"""
        if self._scale_factor is None:
            self._scale_factor = self.dpi / 96.0
        return self._scale_factor
    
    def scale(self, base_size: Union[int, float]) -> int:
        """Scale a size value based on current DPI"""
        return max(1, round(base_size * self.scale_factor))
    
    def scale_font(self, base_font_size: Union[int, float]) -> int:
        """Scale font size with better rounding for readability"""
        scaled = base_font_size * self.scale_factor
        # Round to nearest reasonable font size
        if scaled < 8:
            return 8
        elif scaled < 12:
            return int(scaled)
        else:
            return round(scaled)
    
    def get_scaling_info(self) -> Dict[str, Union[str, float, int]]:
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

def scale_size(size: Union[int, float]) -> int:
    """Convenience function to scale a size"""
    return get_dpi_manager().scale(size)

def scale_font(font_size: Union[int, float]) -> int:
    """Convenience function to scale a font size"""
    return get_dpi_manager().scale_font(font_size)

def get_dpi() -> float:
    """Convenience function to get current DPI"""
    return get_dpi_manager().dpi

def get_scale_factor() -> float:
    """Convenience function to get scale factor"""
    return get_dpi_manager().scale_factor
