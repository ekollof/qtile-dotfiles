#!/usr/bin/env python3
"""
@brief Color management module for qtile - SIMPLIFIED VERSION
@file colors.py

Handles pywal/wallust color loading and automatic reloading.
This module provides a simplified interface to the color management system.

@author Qtile configuration system
@note This module follows Python 3.10+ standards and project guidelines
"""

# Import simplified color management
from .simple_color_management import (
    ColorManager,
    color_manager,
    get_color_manager,
    get_colors,
    manual_color_reload,
    restart_color_monitoring,
    restart_color_monitoring_optimized,
    setup_color_monitoring,
    start_color_monitoring,
)

# Maintain backward compatibility
__all__ = [
    "ColorManager",
    "color_manager",
    "get_color_manager",
    "get_colors",
    "manual_color_reload",
    "restart_color_monitoring",
    "restart_color_monitoring_optimized",
    "setup_color_monitoring",
    "start_color_monitoring",
]

# Load initial colors (maintain original behavior)
color_manager.colordict = color_manager.load_colors()
