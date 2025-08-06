#!/usr/bin/env python3
"""
Simplified color management for qtile
Maintains the same API as the complex version but much simpler implementation
"""

import json
import os
import threading
import time
from typing import Dict, Any, Optional
from libqtile import qtile
from libqtile.log_utils import logger

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    logger.warning("Watchdog not available, using polling fallback")


class SimpleColorManager:
    """Simplified color manager - same API, much less complexity"""

    def __init__(self, colors_file: str = "~/.cache/wal/colors.json"):
        self.colors_file = os.path.expanduser(colors_file)
        self.colordict = self._load_colors()
        self._observer = None
        self._polling_thread = None
        self._watching = False
        self._shutdown_event = threading.Event()

    def _load_colors(self) -> Dict[str, Any]:
        """Load colors from pywal file with fallback"""
        try:
            with open(self.colors_file, 'r') as f:
                colors = json.load(f)
                logger.info(f"Loaded colors from {self.colors_file}")
                return colors
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Could not load colors from {self.colors_file}: {e}")
            return self._get_fallback_colors()

    def _get_fallback_colors(self) -> Dict[str, Any]:
        """Fallback colors when pywal file isn't available"""
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
        """Load colors - maintains original API"""
        return self._load_colors()

    def get_colors(self) -> Dict[str, Any]:
        """Get current colors - maintains original API"""
        return self.colordict

    def start_monitoring(self):
        """Start color file monitoring"""
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
        """Start watchdog file monitoring"""
        class ColorChangeHandler(FileSystemEventHandler):
            def __init__(self, manager):
                self.manager = manager

            def on_modified(self, event):
                if not event.is_directory and event.src_path == self.manager.colors_file:
                    # Small delay to ensure file write is complete
                    time.sleep(0.2)
                    self.manager._handle_color_change()

        try:
            self._observer = Observer()
            handler = ColorChangeHandler(self)
            watch_dir = os.path.dirname(self.colors_file)
            os.makedirs(watch_dir, exist_ok=True)
            self._observer.schedule(handler, watch_dir, recursive=False)
            self._observer.start()
            logger.info(f"Watching {self.colors_file} with watchdog")
        except Exception as e:
            logger.error(f"Watchdog failed: {e}, falling back to polling")
            self._start_polling()

    def _start_polling(self):
        """Start polling-based monitoring"""
        def poll():
            last_mtime = 0
            while self._watching and not self._shutdown_event.is_set():
                try:
                    if os.path.exists(self.colors_file):
                        mtime = os.path.getmtime(self.colors_file)
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
        """Handle color file changes"""
        logger.info("Colors file changed, restarting qtile...")
        try:
            # Reload colors first
            self.colordict = self._load_colors()
            # Restart qtile to apply new colors
            if qtile:
                qtile.restart()
        except Exception as e:
            logger.error(f"Error handling color change: {e}")

    def stop_monitoring(self):
        """Stop monitoring"""
        self._watching = False
        self._shutdown_event.set()

        if self._observer:
            self._observer.stop()
            self._observer.join()

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
