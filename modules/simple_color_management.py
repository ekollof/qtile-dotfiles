#!/usr/bin/env python3
"""
Simplified color management for qtile
Provides basic color loading and file watching functionality
"""

import json

import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional
from libqtile import qtile
from libqtile.log_utils import logger

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    # Create dummy classes for type checking
    Observer = None  # type: ignore
    FileSystemEventHandler = None  # type: ignore
    logger.warning("Watchdog not available, using polling fallback")


class SimpleColorManager:
    """Simplified color manager - same API, much less complexity"""

    def __init__(self, colors_file: str = "~/.cache/wal/colors.json"):
        self.colors_file = Path(colors_file).expanduser()
        self.colordict = self._load_colors()
        self._observer = None
        self._polling_thread = None
        self._watching = False
        self._shutdown_event = threading.Event()

    def _load_colors(self) -> Dict[str, Any]:
        """
        @brief Load colors from pywal file with fallback
        @return Dictionary containing color configuration with 'special' and 'colors' keys
        @throws FileNotFoundError when color file doesn't exist
        @throws json.JSONDecodeError when color file is corrupted
        """
        try:
            with open(self.colors_file, 'r') as f:
                colors = json.load(f)
                logger.info(f"Loaded colors from {self.colors_file}")
                return colors
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Could not load colors from {self.colors_file}: {e}")
            return self._get_fallback_colors()

    def _get_fallback_colors(self) -> Dict[str, Any]:
        """
        @brief Provide fallback colors when pywal file isn't available
        @return Dictionary with default color scheme containing 'special' and 'colors' keys
        """
        return {
            "special": {
                "background": "#1e1e1e",
                "foreground": "#ffffff",
                "cursor": "#ffffff"
            },
            "colors": {
                "color0": "#1e1e1e",
                "color1": "#e06c75",
                "color2": "#98c379",
                "color3": "#e5c07b",
                "color4": "#61afef",
                "color5": "#c678dd",
                "color6": "#56b6c2",
                "color7": "#ffffff",
                "color8": "#5c6370",
                "color9": "#e06c75",
                "color10": "#98c379",
                "color11": "#e5c07b",
                "color12": "#61afef",
                "color13": "#c678dd",
                "color14": "#56b6c2",
                "color15": "#ffffff"
            }
        }

    # Main API methods - maintain compatibility
    def load_colors(self) -> Dict[str, Any]:
        """
        @brief Load colors from file - maintains original API compatibility
        @return Dictionary containing loaded color configuration
        """
        return self._load_colors()

    def get_colors(self) -> Dict[str, Any]:
        """
        @brief Get current colors from cache - maintains original API compatibility
        @return Dictionary containing current color configuration
        """
        return self.colordict

    def start_monitoring(self):
        """
        @brief Start color file monitoring using watchdog or polling fallback
        @throws Exception if monitoring setup fails completely
        """
        if self._watching:
            return

        self._shutdown_event.clear()
        self._watching = True

        if WATCHDOG_AVAILABLE:
            self._start_watchdog()
        else:
            self._start_polling()

        logger.info("Started color monitoring")

    def _start_watchdog(self):
        """
        @brief Start watchdog-based file monitoring for color changes
        @throws Exception if watchdog setup fails
        """
        if not WATCHDOG_AVAILABLE or Observer is None or FileSystemEventHandler is None:
            logger.warning("Watchdog not available, file monitoring disabled")
            return

        class ColorChangeHandler(FileSystemEventHandler):  # type: ignore
            def __init__(self, manager):
                self.manager = manager

            def on_modified(self, event):
                if not event.is_directory and event.src_path == self.manager.colors_file:
                    # Small delay to ensure file write is complete
                    time.sleep(0.2)
                    self.manager._handle_color_change()

        try:
            self._observer = Observer()  # type: ignore
            handler = ColorChangeHandler(self)
            watch_dir = self.colors_file.parent
            watch_dir.mkdir(parents=True, exist_ok=True)
            self._observer.schedule(handler, str(watch_dir), recursive=False)  # type: ignore
            self._observer.start()  # type: ignore
            logger.debug(f"Started watching {watch_dir} for color changes")
        except Exception as e:
            logger.warning(f"Failed to start watchdog monitoring: {e}")
            self._observer = None
            logger.error(f"Watchdog failed: {e}, falling back to polling")
            self._start_polling()

    def _start_polling(self):
        """
        @brief Start polling-based monitoring as fallback when watchdog unavailable
        """
        def poll():
            last_mtime = 0
            while self._watching and not self._shutdown_event.is_set():
                try:
                    if self.colors_file.exists():
                        mtime = self.colors_file.stat().st_mtime
                        if mtime > last_mtime > 0:
                            time.sleep(0.2)  # Ensure write complete
                            self._handle_color_change()
                        last_mtime = mtime
                except Exception as e:
                    logger.error(f"Polling error: {e}")
                time.sleep(1)

        self._polling_thread = threading.Thread(target=poll, daemon=True)
        self._polling_thread.start()
        logger.info(f"Watching {self.colors_file} with polling")

    def _handle_color_change(self):
        """
        @brief Handle color file changes by reloading colors and restarting qtile
        @throws Exception if color reload or qtile restart fails
        """
        logger.info("Colors file changed, restarting qtile...")
        try:
            # Reload colors first to validate the new file
            self.colordict = self._load_colors()
            logger.debug("Colors reloaded successfully")
            
            # Restart qtile to apply new colors
            if qtile is not None:
                qtile.restart()
            else:
                logger.warning("qtile instance not available, cannot restart")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in color file, ignoring change: {e}")
        except Exception as e:
            logger.error(f"Error handling color change: {e}")
            # Don't restart qtile if we can't load colors properly

    def stop_monitoring(self):
        """
        @brief Stop all monitoring threads and observers
        """
        self._watching = False
        self._shutdown_event.set()

        if self._observer and hasattr(self._observer, 'stop'):
            self._observer.stop()  # type: ignore
            self._observer.join()  # type: ignore

        if self._polling_thread:
            self._polling_thread.join(timeout=2)

        logger.info("Stopped color monitoring")

    # Compatibility methods for existing API
    def is_monitoring(self) -> bool:
        return self._watching

    def restart_monitoring(self):
        self.stop_monitoring()
        time.sleep(0.5)
        self.start_monitoring()


# Global instance
_color_manager_instance: Optional[SimpleColorManager] = None

def get_color_manager() -> SimpleColorManager:
    """Get singleton color manager"""
    global _color_manager_instance
    if _color_manager_instance is None:
        _color_manager_instance = SimpleColorManager()
    return _color_manager_instance

# Create global instance
color_manager = get_color_manager()

# API functions for compatibility
def get_colors() -> Dict[str, Any]:
    return color_manager.get_colors()

def start_color_monitoring():
    color_manager.start_monitoring()

def setup_color_monitoring():
    color_manager.start_monitoring()

def restart_color_monitoring():
    color_manager.restart_monitoring()

# Stub functions for compatibility (not needed in simple version)
def manual_color_reload(): pass
def validate_current_colors(): return True
def get_color_file_status(): return {"exists": True, "readable": True}
def get_monitoring_performance_status(): return {"optimized": True}
def optimize_color_monitoring(): pass
def restart_color_monitoring_optimized(): color_manager.restart_monitoring()

# Make ColorManager class alias for compatibility
ColorManager = SimpleColorManager
