#!/usr/bin/env python3
"""
Color backup and file management functionality
"""

import json
import os
import shutil
import time
from typing import List, Optional
from libqtile.log_utils import logger

from .utils import ColorDict, validate_colors, load_colors_from_file


class BackupManager:
    """Manages color file backups and recovery"""
    
    def __init__(self, backup_dir: str, last_good_colors_file: str):
        self.backup_dir = backup_dir
        self.last_good_colors_file = last_good_colors_file
        self._ensure_backup_directory()

    def _ensure_backup_directory(self):
        """Ensure backup directory exists"""
        try:
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating backup directory: {e}")

    def create_backup(self, colors_file: str) -> bool:
        """Create timestamped backup of current colors"""
        try:
            if not os.path.exists(colors_file):
                return False

            # Validate colors before backing up
            colors = load_colors_from_file(colors_file)
            if not colors:
                logger.warning("Skipping backup of invalid colors file")
                return False

            # Create timestamped backup
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_dir, f"colors_{timestamp}.json")
            shutil.copy2(colors_file, backup_file)

            # Clean up old backups
            self._cleanup_old_backups()

            # Update last good colors file
            shutil.copy2(colors_file, self.last_good_colors_file)
            logger.debug(f"Created color backup: {backup_file}")
            return True

        except Exception as e:
            logger.error(f"Error creating color backup: {e}")
            return False

    def _cleanup_old_backups(self, max_backups: int = 10):
        """Keep only the most recent backups"""
        try:
            backups = sorted([f for f in os.listdir(self.backup_dir) 
                            if f.startswith('colors_')])
            while len(backups) > max_backups:
                old_backup = backups.pop(0)
                os.remove(os.path.join(self.backup_dir, old_backup))
                logger.debug(f"Removed old backup: {old_backup}")
        except Exception as e:
            logger.error(f"Error cleaning up backups: {e}")

    def get_backup_list(self) -> List[str]:
        """Get list of available backups"""
        try:
            if not os.path.exists(self.backup_dir):
                return []
            return sorted([f for f in os.listdir(self.backup_dir) 
                          if f.startswith('colors_')])
        except Exception as e:
            logger.error(f"Error getting backup list: {e}")
            return []

    def restore_from_backup(self, backup_name: str, target_file: str) -> bool:
        """Restore colors from a specific backup"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_name)
            if not os.path.exists(backup_path):
                logger.error(f"Backup file not found: {backup_name}")
                return False

            # Validate backup before restoring
            colors = load_colors_from_file(backup_path)
            if not colors:
                logger.error(f"Invalid backup file: {backup_name}")
                return False

            shutil.copy2(backup_path, target_file)
            logger.info(f"Restored colors from backup: {backup_name}")
            return True

        except Exception as e:
            logger.error(f"Error restoring from backup: {e}")
            return False

    def restore_last_good(self, target_file: str) -> bool:
        """Restore from last known good colors"""
        try:
            if not os.path.exists(self.last_good_colors_file):
                logger.warning("No last good colors file found")
                return False

            colors = load_colors_from_file(self.last_good_colors_file)
            if not colors:
                logger.error("Last good colors file is invalid")
                return False

            shutil.copy2(self.last_good_colors_file, target_file)
            logger.info("Restored last good colors")
            return True

        except Exception as e:
            logger.error(f"Error restoring last good colors: {e}")
            return False

    def restore_latest_backup(self, target_file: str) -> bool:
        """Restore from most recent backup"""
        try:
            backups = self.get_backup_list()
            if not backups:
                logger.warning("No backups available")
                return False

            latest_backup = backups[-1]
            return self.restore_from_backup(latest_backup, target_file)

        except Exception as e:
            logger.error(f"Error restoring latest backup: {e}")
            return False


class ColorLoader:
    """Handles loading colors with fallback mechanisms"""
    
    def __init__(self, colors_file: str, backup_manager: BackupManager):
        self.colors_file = colors_file
        self.backup_manager = backup_manager

    def load_colors_safely(self) -> ColorDict:
        """Load colors with validation and fallback"""
        # Try to load current colors file
        colors = load_colors_from_file(self.colors_file)
        if colors:
            logger.info("Loaded colors from wal cache")
            return colors

        logger.warning("Invalid colors in wal cache, trying backup")

        # Try to load last good colors
        colors = load_colors_from_file(self.backup_manager.last_good_colors_file)
        if colors:
            logger.info("Loaded colors from last good backup")
            return colors

        # Try to load from most recent backup
        backups = self.backup_manager.get_backup_list()
        if backups:
            latest_backup_path = os.path.join(
                self.backup_manager.backup_dir, 
                backups[-1]
            )
            colors = load_colors_from_file(latest_backup_path)
            if colors:
                logger.info(f"Loaded colors from backup: {backups[-1]}")
                return colors

        # Fall back to default colors
        logger.warning("Using default colors due to validation failures")
        from .utils import load_default_colors
        return load_default_colors()

    def reload_colors(self) -> ColorDict:
        """Reload colors and return the new color dictionary"""
        return self.load_colors_safely()
