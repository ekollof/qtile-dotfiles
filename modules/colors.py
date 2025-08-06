#!/usr/bin/env python3
"""
Color management module for qtile - SIMPLIFIED VERSION
Handles pywal/wallust color loading and automatic reloading
"""

# Import simplified color management
from .simple_color_management import *

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
