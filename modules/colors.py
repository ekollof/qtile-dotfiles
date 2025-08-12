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
    start_color_monitoring,
    setup_color_monitoring,
    restart_color_monitoring,
    manual_color_reload,
    validate_current_colors,
    get_color_file_status,
    get_monitoring_performance_status,
    optimize_color_monitoring,
    restart_color_monitoring_optimized
)

# Maintain backward compatibility
__all__ = [
    'ColorManager',
    'color_manager',
    'get_color_manager',
    'get_colors',
    'start_color_monitoring',
    'setup_color_monitoring',
    'restart_color_monitoring',
    # Compatibility stubs
    'manual_color_reload',
    'validate_current_colors',
    'get_color_file_status',
    'get_monitoring_performance_status',
    'optimize_color_monitoring',
    'restart_color_monitoring_optimized'
]

# Load initial colors (maintain original behavior)
color_manager.colordict = color_manager.load_colors()
