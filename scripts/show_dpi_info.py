#!/usr/bin/env python3
"""
@brief Show DPI information and scaling factors for qtile configuration
@file show_dpi_info.py

Displays current DPI detection results, scaling factors, and provides
testing utilities for qtile's DPI-aware configuration system.

@author Qtile configuration system
@note This script follows Python 3.10+ standards and project guidelines
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.dpi_utils import get_dpi_manager


def main() -> None:
    """
    @brief Display comprehensive DPI information and scaling factors
    @throws ImportError if DPI utilities cannot be loaded
    """
    dpi_manager = get_dpi_manager()
    info = dpi_manager.get_scaling_info()

    print("🖥️  DPI Information for Qtile Configuration")
    print("=" * 50)
    print(f"Current DPI: {info['dpi']:.1f}")
    print(f"Scale Factor: {info['scale_factor']:.2f}x")
    print(f"Category: {info['category']}")
    print()
    print("📏 Scaled Sizes:")
    print(f"  Bar Height: {info['bar_height']}px (base: 28px)")
    print(f"  Icon Size: {info['icon_size']}px (base: 16px)")
    print(f"  Margin: {info['margin']}px (base: 4px)")
    print(f"  Font Size: {info['recommended_font_base']}px (base: 12px)")
    print()
    print("🔧 Manual overrides:")
    print("  Set QT_SCALE_FACTOR environment variable")
    print("  Add 'Xft.dpi: XXX' to ~/.Xresources")
    print()
    print("🧪 Test scaling:")
    print(f"  scale_size(10) = {dpi_manager.scale(10)}px")
    print(f"  scale_size(20) = {dpi_manager.scale(20)}px")
    print(f"  scale_font(12) = {dpi_manager.scale_font(12)}px")
    print(f"  scale_font(16) = {dpi_manager.scale_font(16)}px")


if __name__ == "__main__":
    main()
