#!/usr/bin/env python3
"""
Main color manager class - orchestrates all color management functionality
"""

import libqtile
import os
import threading
import time
import traceback
from typing import Dict, Union, Optional, Any
from libqtile.log_utils import logger

from .utils import ColorDict, get_file_hash, ensure_directories
from .backup import BackupManager, ColorLoader
from .monitoring import FileWatcher, RestartTriggerChecker


class ColorManager:
    """Manages color loading and automatic reloading from pywal/wallust"""
    
    def __init__(self):
        # File paths
        self.colors_file = os.path.expanduser("~/.cache/wal/colors.json")
        self.backup_dir = os.path.expanduser("~/.cache/wal/backups")
        self.restart_trigger_file = os.path.expanduser("~/.config/qtile/restart_trigger")
        self.last_good_colors_file = os.path.expanduser("~/.cache/wal/last_good_colors.json")

        # Initialize directories
        ensure_directories(self.backup_dir, os.path.dirname(self.restart_trigger_file))

        # Initialize components
        self.backup_manager = BackupManager(self.backup_dir, self.last_good_colors_file)
        self.color_loader = ColorLoader(self.colors_file, self.backup_manager)

        # Load colors with validation
        self.colordict = self.color_loader.load_colors_safely()
        self.last_file_hash = get_file_hash(self.colors_file)

        # Threading and monitoring
        self.watcher_thread: Optional[threading.Thread] = None
        self.restart_checker_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()
        self._startup_time = time.time()

        # Create initial backup
        self.backup_manager.create_backup(self.colors_file)

    def load_colors(self) -> ColorDict:
        """Load colors from pywal colors.json file with validation"""
        return self.color_loader.load_colors_safely()

    def get_colors(self) -> ColorDict:
        """Get current color dictionary"""
        return self.colordict

    def update_colors(self):
        """Update colors and trigger qtile restart with validation"""
        logger.info("Reloading colors due to file change")
        try:
            # Check if file actually changed
            current_hash = get_file_hash(self.colors_file)
            if current_hash == self.last_file_hash:
                logger.debug("Colors file hash unchanged, skipping update")
                return

            logger.info("Loading new colors...")
            new_colors = self.color_loader.load_colors_safely()

            # Update colors if different
            if new_colors != self.colordict:
                self.colordict = new_colors
                self.last_file_hash = current_hash
                logger.info(f"Updated colors: background={new_colors['special']['background']}")

                # Create backup of new colors
                self.backup_manager.create_backup(self.colors_file)

                # Create restart trigger file only if Qtile has been running for a while
                if time.time() - self._startup_time > 30:  # Only restart after 30 seconds of runtime
                    self._create_restart_trigger()
                else:
                    logger.info("Colors updated without restart (too soon after startup)")
            else:
                logger.debug("Colors unchanged after reload")

        except Exception as e:
            logger.error(f"Error updating colors: {e}")
            logger.error(traceback.format_exc())

    def _create_restart_trigger(self):
        """Create restart trigger file"""
        try:
            logger.info("Creating restart trigger...")
            with open(self.restart_trigger_file, "w") as f:
                f.write(f"restart_{int(time.time())}")
        except Exception as e:
            logger.error(f"Error creating restart trigger: {e}")

    def check_restart_trigger(self) -> bool:
        """Check if qtile should restart due to color changes. Returns True if trigger was found."""
        try:
            if os.path.exists(self.restart_trigger_file):
                logger.info("Color change detected - restarting qtile")
                os.remove(self.restart_trigger_file)

                # Use qtile's built-in restart
                if hasattr(libqtile, 'qtile') and libqtile.qtile:
                    libqtile.qtile.restart()
                else:
                    # Fallback
                    os.system("qtile cmd-obj -o cmd -f restart")
                return True
            return False
        except Exception as e:
            logger.error(f"Error in restart check: {e}")
            return False

    def start_monitoring(self):
        """Start color file monitoring with improved error handling and resource management"""
        try:
            # Clear shutdown event
            self._shutdown_event.clear()

            # Check if monitoring is already active
            if self.is_monitoring():
                logger.info("Color monitoring is already active")
                return

            # Start color file watcher if not already running
            if self.watcher_thread is None or not self.watcher_thread.is_alive():
                logger.info("Starting optimized color file watcher...")
                file_watcher = FileWatcher(
                    self.colors_file, 
                    self.update_colors, 
                    self._shutdown_event
                )
                self.watcher_thread = threading.Thread(
                    target=file_watcher.start_watching, 
                    daemon=True,
                    name="ColorWatcher"
                )
                self.watcher_thread.start()
                logger.info("Optimized color file watcher started")

            # Start restart trigger checker if not already running
            if (not hasattr(self, 'restart_checker_thread') or 
                self.restart_checker_thread is None or 
                not self.restart_checker_thread.is_alive()):
                logger.info("Starting optimized restart trigger checker...")
                restart_checker = RestartTriggerChecker(
                    self.restart_trigger_file,
                    self.check_restart_trigger,
                    self._shutdown_event
                )
                self.restart_checker_thread = threading.Thread(
                    target=restart_checker.start_checking, 
                    daemon=True,
                    name="RestartChecker"
                )
                self.restart_checker_thread.start()
                logger.info("Optimized restart trigger checker started")

            # Verify threads started successfully
            time.sleep(0.1)  # Give threads a moment to start
            if not self.is_monitoring():
                logger.error("Failed to start color monitoring threads")
            else:
                logger.info("Color monitoring started successfully with performance optimizations")

        except Exception as e:
            logger.error(f"Error starting optimized color monitoring: {e}")
            logger.error(traceback.format_exc())

    def stop_monitoring(self):
        """Gracefully stop all monitoring threads"""
        logger.info("Stopping color monitoring...")
        self._shutdown_event.set()

        # Wait for threads to finish
        if self.watcher_thread and self.watcher_thread.is_alive():
            self.watcher_thread.join(timeout=10)
        if (hasattr(self, 'restart_checker_thread') and 
            self.restart_checker_thread and 
            self.restart_checker_thread.is_alive()):
            self.restart_checker_thread.join(timeout=5)

        logger.info("Color monitoring stopped")

    def restart_monitoring(self):
        """Restart color monitoring with performance optimizations"""
        logger.info("Restarting color monitoring with optimizations...")
        
        # Get current status for debugging
        old_status = self.get_monitoring_status()
        logger.debug(f"Pre-restart status: {old_status}")
        
        # Stop existing monitoring
        self.stop_monitoring()
        
        # Apply performance optimizations
        self.optimize_monitoring_performance()
        
        # Wait a bit longer to ensure clean shutdown
        time.sleep(3)
        
        # Start fresh monitoring
        self.start_monitoring()
        
        # Verify restart was successful
        time.sleep(1)
        new_status = self.get_monitoring_status()
        logger.info(f"Post-restart status: monitoring_active={new_status['monitoring_active']}")
        
        if new_status['monitoring_active']:
            logger.info("Color monitoring restarted successfully with performance optimizations")
        else:
            logger.error("Failed to restart color monitoring")

    def is_monitoring(self) -> bool:
        """Check if color monitoring is active"""
        watcher_running = self.watcher_thread is not None and self.watcher_thread.is_alive()
        checker_running = (hasattr(self, 'restart_checker_thread') and 
                          self.restart_checker_thread is not None and 
                          self.restart_checker_thread.is_alive())
        return watcher_running and checker_running

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get detailed monitoring status for diagnostics"""
        status = {
            'monitoring_active': self.is_monitoring(),
            'watcher_thread_alive': self.watcher_thread is not None and self.watcher_thread.is_alive(),
            'restart_checker_alive': (hasattr(self, 'restart_checker_thread') and 
                                     self.restart_checker_thread is not None and 
                                     self.restart_checker_thread.is_alive()),
            'shutdown_event_set': self._shutdown_event.is_set(),
            'startup_time': self._startup_time,
            'uptime_seconds': time.time() - self._startup_time,
        }
        
        # Add thread names if available
        if self.watcher_thread and self.watcher_thread.is_alive():
            status['watcher_thread_name'] = getattr(self.watcher_thread, 'name', 'Unknown')
        if (hasattr(self, 'restart_checker_thread') and 
            self.restart_checker_thread and 
            self.restart_checker_thread.is_alive()):
            status['restart_checker_name'] = getattr(self.restart_checker_thread, 'name', 'Unknown')
            
        return status
    
    def optimize_monitoring_performance(self):
        """Apply runtime performance optimizations"""
        try:
            # Force garbage collection to free memory
            import gc
            collected = gc.collect()
            if collected > 0:
                logger.debug(f"Garbage collected {collected} objects")
            
            # Check and log current resource usage
            try:
                import resource
                memory_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                logger.debug(f"Current memory usage: {memory_usage} KB")
            except ImportError:
                pass
                
        except Exception as e:
            logger.warning(f"Error in performance optimization: {e}")

    # Public interfaces for backward compatibility
    def validate_colors_public(self, colors: ColorDict) -> bool:
        """Public interface for color validation"""
        from .utils import validate_colors
        return validate_colors(colors)
        
    def get_file_hash_public(self, filepath: str) -> Optional[str]:
        """Public interface for getting file hash"""
        return get_file_hash(filepath)


# Singleton pattern to prevent multiple instances
_color_manager_instance: Optional[ColorManager] = None


def get_color_manager() -> ColorManager:
    """Get or create the singleton color manager instance"""
    global _color_manager_instance
    if _color_manager_instance is None:
        _color_manager_instance = ColorManager()
    return _color_manager_instance
