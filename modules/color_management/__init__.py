"""
Color management package for qtile
Provides modular color loading and monitoring functionality
"""

from .manager import ColorManager, get_color_manager
from .api import (
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

# Global color manager instance
color_manager = get_color_manager()

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
