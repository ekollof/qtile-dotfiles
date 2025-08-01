#!/usr/bin/env python3
"""
Color management module for qtile
Handles pywal/wallust color loading and automatic reloading
Refactored for better maintainability while preserving backward compatibility
"""

# Import all functionality from the new modular structure
from .color_management import (
    # Core classes and instances
    ColorManager,
    color_manager,
    get_color_manager,
    
    # Public API functions
    get_colors,
    manual_color_reload,
    start_color_monitoring,
    setup_color_monitoring,
    restart_color_monitoring,
    validate_current_colors,
    get_color_file_status,
    get_monitoring_performance_status,
    optimize_color_monitoring,
    restart_color_monitoring_optimized
)

# Maintain backward compatibility by exposing the same interface
__all__ = [
    'ColorManager',
    'color_manager',
    'get_color_manager',
    'get_colors',
    'manual_color_reload',
    'start_color_monitoring',
    'setup_color_monitoring',
    'restart_color_monitoring',
    'validate_current_colors',
    'get_color_file_status',
    'get_monitoring_performance_status',
    'optimize_color_monitoring',
    'restart_color_monitoring_optimized'
]

# Load initial colors (maintain original behavior)
color_manager.colordict = color_manager.load_colors()
