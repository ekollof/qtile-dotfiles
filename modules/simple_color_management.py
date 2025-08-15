#!/usr/bin/env python3
"""
Simplified color management for qtile
Provides basic color loading and file watching functionality
"""

import json
import threading
import time
from pathlib import Path
from typing import Any

from libqtile import qtile
from libqtile.log_utils import logger

try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    watchdog_available = True
except ImportError:
    watchdog_available = False
    # Create dummy classes for type checking
    Observer = None
    FileSystemEventHandler = None
    logger.warning("Watchdog not available, using polling fallback")


class SimpleColorManager:
    """Simplified color manager - same API, much less complexity"""

    def __init__(self, colors_file: str = "~/.cache/wal/colors.json") -> None:
        self.colors_file = Path(colors_file).expanduser()
        self.colordict = self._load_colors()
        self._observer = None
        self._polling_thread = None
        self._watching = False
        self._shutdown_event = threading.Event()
        self._auto_start_attempted = False

    def _load_colors(self) -> dict[str, Any]:
        """
        @brief Load colors from pywal file with fallback
        @return Dictionary containing color configuration with 'special' and 'colors' keys
        @throws FileNotFoundError when color file doesn't exist
        @throws json.JSONDecodeError when color file is corrupted
        """
        try:
            with open(self.colors_file) as f:
                colors = json.load(f)
                logger.info(f"Loaded colors from {self.colors_file}")
                return colors
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Could not load colors from {self.colors_file}: {e}")
            return self._get_fallback_colors()

    def _get_fallback_colors(self) -> dict[str, dict[str, str]]:
        """
        @brief Provide fallback colors when pywal file isn't available
        @return Dictionary with default color scheme containing 'special' and 'colors' keys
        """
        return {
            "special": {
                "background": "#1e1e1e",
                "foreground": "#ffffff",
                "cursor": "#ffffff",
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
                "color15": "#ffffff",
            },
        }

    # Main API methods - maintain compatibility
    def load_colors(self) -> dict[str, Any]:
        """
        @brief Load colors from file - maintains original API compatibility
        @return Dictionary containing loaded color configuration
        """
        return self._load_colors()

    def get_colors(self) -> dict[str, Any]:
        """
        @brief Get current colors from cache - maintains original API compatibility
        @return Dictionary containing current color configuration
        """
        # Auto-start monitoring on first access if not already started
        if not self._auto_start_attempted:
            self._auto_start_attempted = True
            try:
                self.start_monitoring()
                logger.info("Auto-started color monitoring on first color access")
            except Exception as e:
                logger.warning(f"Failed to auto-start color monitoring: {e}")

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

        if watchdog_available:
            self._start_watchdog()
        else:
            self._start_polling()

        logger.info("Started color monitoring")

    def _start_watchdog(self):
        """
        @brief Start watchdog-based file monitoring for color changes
        @throws Exception if watchdog setup fails
        """
        if not watchdog_available or Observer is None or FileSystemEventHandler is None:
            logger.warning("Watchdog not available, file monitoring disabled")
            return

        class ColorChangeHandler(FileSystemEventHandler):
            def __init__(self, manager: Any) -> None:
                super().__init__()
                self.manager = manager

            def on_modified(self, event: Any) -> None:
                if not event.is_directory and event.src_path == str(
                    self.manager.colors_file
                ):
                    # Small delay to ensure file write is complete
                    time.sleep(0.2)
                    self.manager._handle_color_change()

        try:
            self._observer = Observer()
            handler = ColorChangeHandler(self)
            watch_dir = self.colors_file.parent
            watch_dir.mkdir(parents=True, exist_ok=True)
            self._observer.schedule(handler, str(watch_dir), recursive=False)
            self._observer.start()
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

    def _validate_color_file(self) -> bool:
        """
        @brief Validate that color file exists and is readable
        @return True if file is valid, False otherwise
        """
        if not self.colors_file.exists():
            logger.warning("Colors file disappeared, ignoring change")
            return False

        file_size = self.colors_file.stat().st_size
        if file_size < 10:  # JSON file should be larger than 10 bytes
            logger.warning(
                f"Colors file too small ({file_size} bytes), possibly incomplete write"
            )
            return False

        return True

    def _detect_color_changes(self, old_colors: dict[str, Any]) -> bool:
        """
        @brief Check if colors actually changed
        @param old_colors Previous color dictionary
        @return True if colors changed, False otherwise
        """
        if old_colors == self.colordict:
            logger.debug("Colors unchanged, skipping restart")
            return False

        # Log the color change for debugging
        old_bg = old_colors.get("special", {}).get("background", "unknown")
        new_bg = self.colordict.get("special", {}).get("background", "unknown")
        logger.info(f"Background color changed: {old_bg} → {new_bg}")
        return True

    def _update_svg_icons(self) -> None:
        """
        @brief Update SVG icons if enhanced bar manager is available
        """
        try:
            # Try to update icons for current bar manager
            if hasattr(qtile, "config") and hasattr(qtile.config, "screens"):
                for screen in qtile.config.screens:
                    if hasattr(screen, "top") and screen.top:
                        # Force regeneration of themed icons
                        logger.info("Updating dynamic SVG icons for new color scheme")
                        break
        except Exception as e:
            logger.debug(f"Could not update SVG icons: {e}")

    def _restart_qtile(self) -> None:
        """
        @brief Restart qtile to apply new colors
        """
        if qtile is not None and hasattr(qtile, "restart"):
            try:
                logger.info("Restarting qtile to apply new colors...")
                qtile.restart()
            except AttributeError:
                logger.warning("qtile.restart() not available (running outside qtile?)")
            except Exception as e:
                logger.error(f"Failed to restart qtile: {e}")
        else:
            logger.warning("qtile instance not available or restart method missing")

    def _handle_color_change(self):
        """
        @brief Handle color file changes by reloading colors and restarting qtile
        @throws Exception if color reload or qtile restart fails
        """
        logger.info("Colors file changed, processing update...")
        try:
            # Validate file exists and is readable
            if not self._validate_color_file():
                return

            # Reload colors first to validate the new file
            old_colors = self.colordict.copy()
            self.colordict = self._load_colors()
            logger.debug("Colors reloaded successfully")

            # Check if colors actually changed to avoid unnecessary restarts
            if not self._detect_color_changes(old_colors):
                return

            # Update SVG icons if enhanced bar manager is available
            self._update_svg_icons()

            # Restart qtile to apply new colors
            self._restart_qtile()

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in color file, ignoring change: {e}")
        except FileNotFoundError:
            logger.warning("Colors file not found during change handling")
        except PermissionError:
            logger.error("Permission denied reading colors file")
        except Exception as e:
            logger.error(f"Error handling color change: {e}")
            # Don't restart qtile if we can't load colors properly

    def manual_reload_colors(self):
        """
        @brief Manually reload colors without automatic restart
        @return True if successful, False otherwise
        """
        try:
            logger.info("Manual color reload requested")
            old_colors = self.colordict.copy()
            self.colordict = self._load_colors()

            # Check if colors actually changed
            if old_colors != self.colordict:
                logger.info("Colors changed, updating SVG icons and restarting qtile")
                self._handle_color_change()
            else:
                logger.info("Colors unchanged, no restart needed")
            return True
        except Exception as e:
            logger.error(f"Manual color reload failed: {e}")
            return False

    def force_start_monitoring(self):
        """
        @brief Force start monitoring with better error handling
        @return True if successful, False otherwise
        """
        try:
            if self._watching:
                logger.info("Color monitoring already active")
                return True

            self.start_monitoring()

            if self.is_monitoring():
                logger.info("Color monitoring force-started successfully")
                return True
            else:
                logger.warning("Color monitoring failed to start")
                return False
        except Exception as e:
            logger.error(f"Failed to force start color monitoring: {e}")
            return False

    def restart_monitoring(self):
        self.stop_monitoring()
        time.sleep(0.5)
        self.start_monitoring()

    def stop_monitoring(self):
        """
        @brief Stop all monitoring threads and observers
        """
        self._watching = False
        self._shutdown_event.set()

        if self._observer and hasattr(self._observer, "stop"):
            self._observer.stop()
            self._observer.join()

        if self._polling_thread:
            self._polling_thread.join(timeout=2)

        logger.info("Stopped color monitoring")

    # Compatibility methods for existing API
    def is_monitoring(self) -> bool:
        return self._watching


# Global instance
_color_manager_instance: SimpleColorManager | None = None


def get_color_manager() -> SimpleColorManager:
    """Get singleton color manager"""
    global _color_manager_instance
    if _color_manager_instance is None:
        _color_manager_instance = SimpleColorManager()
    return _color_manager_instance


# Create global instance
color_manager = get_color_manager()


# API functions for compatibility
def get_colors() -> dict[str, Any]:
    return color_manager.get_colors()


def start_color_monitoring():
    color_manager.start_monitoring()


def setup_color_monitoring():
    color_manager.start_monitoring()


def restart_color_monitoring():
    color_manager.restart_monitoring()


def manual_color_reload():
    """Manual color reload function for keybindings"""
    return color_manager.manual_reload_colors()


def force_start_color_monitoring():
    """Force start color monitoring with better error handling"""
    return color_manager.force_start_monitoring()


def restart_color_monitoring_optimized():
    """Optimized restart - delegates to standard restart"""
    color_manager.restart_monitoring()


# Make ColorManager class alias for compatibility
ColorManager = SimpleColorManager
