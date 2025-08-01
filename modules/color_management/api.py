#!/usr/bin/env python3
"""
Public API for color management functionality
"""

import os
from typing import Dict, Any
from libqtile.log_utils import logger

from .manager import get_color_manager
from .utils import ColorDict


def get_colors() -> ColorDict:
    """Get current color dictionary"""
    return get_color_manager().get_colors()


def manual_color_reload():
    """Manually trigger color reload"""
    get_color_manager().update_colors()


def start_color_monitoring():
    """Start automatic color monitoring"""
    get_color_manager().start_monitoring()


def setup_color_monitoring():
    """Setup color monitoring after qtile startup"""
    try:
        color_manager = get_color_manager()
        if color_manager.is_monitoring():
            logger.info("Color file watcher is running")
        else:
            logger.warning("Color file watcher is not running - restarting")
            color_manager.start_monitoring()
    except Exception as e:
        logger.error(f"Error in setup_color_monitoring: {e}")


def restart_color_monitoring():
    """Restart color monitoring (for recovery)"""
    get_color_manager().restart_monitoring()


def validate_current_colors() -> bool:
    """Validate current color configuration"""
    color_manager = get_color_manager()
    colors = color_manager.get_colors()
    is_valid = color_manager.validate_colors_public(colors)
    logger.info(f"Current colors validation: {'PASSED' if is_valid else 'FAILED'}")
    return is_valid


def get_color_file_status() -> Dict[str, Any]:
    """Get status information about color files"""
    color_manager = get_color_manager()
    
    status = {
        'colors_file_exists': os.path.exists(color_manager.colors_file),
        'last_good_colors_exists': os.path.exists(color_manager.last_good_colors_file),
        'backup_dir_exists': os.path.exists(color_manager.backup_dir),
        'monitoring_active': color_manager.is_monitoring(),
        'current_hash': color_manager.get_file_hash_public(color_manager.colors_file),
        'validation_passed': color_manager.validate_colors_public(color_manager.colordict)
    }

    if os.path.exists(color_manager.backup_dir):
        backups = [f for f in os.listdir(color_manager.backup_dir) if f.startswith('colors_')]
        status['backup_count'] = len(backups)
        status['latest_backup'] = max(backups) if backups else None
    else:
        status['backup_count'] = 0
        status['latest_backup'] = None

    return status


def get_monitoring_performance_status() -> Dict[str, Any]:
    """Get comprehensive monitoring performance status for debugging"""
    color_manager = get_color_manager()
    status = color_manager.get_monitoring_status()
    file_status = get_color_file_status()
    
    # Combine both status reports
    combined_status = {
        **status,
        **file_status,
        'performance_optimizations_active': True,
        'color_manager_type': type(color_manager).__name__,
    }
    
    return combined_status


def optimize_color_monitoring():
    """Manually trigger color monitoring performance optimizations"""
    get_color_manager().optimize_monitoring_performance()
    logger.info("Applied color monitoring performance optimizations")


def restart_color_monitoring_optimized():
    """Restart color monitoring with all performance optimizations"""
    get_color_manager().restart_monitoring()
