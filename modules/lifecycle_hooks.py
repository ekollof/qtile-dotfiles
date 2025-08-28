#!/usr/bin/env python3
"""
@brief Consolidated lifecycle hooks for qtile
@file lifecycle_hooks.py

This module consolidates all lifecycle-related hooks into a single,
well-organized system with improved maintainability and error handling.

Features:
- Screen change detection and handling
- Startup and shutdown hooks
- Monitor hotplug support
- Window retiling after restart
- Comprehensive error handling and validation

@author Qtile configuration system
@note This module follows Python 3.10+ standards and project guidelines
"""

import os
import subprocess
import time
import traceback
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any

from libqtile import hook, qtile
from libqtile.log_utils import logger

if TYPE_CHECKING:
    from modules.color_management import ColorManager
    from modules.window_manager import WindowManager

from modules.notifications import show_popup_notification


class LifecycleHooks:
    """Consolidated lifecycle hooks manager for qtile"""

    def __init__(
        self,
        config: Any,
        color_manager: "ColorManager | None" = None,
        window_manager: "WindowManager | None" = None,
    ) -> None:
        self.config = config
        self.color_manager = color_manager
        self.window_manager = window_manager

    def setup_all_hooks(self):
        """
        @brief Setup all lifecycle-related hooks
        """
        logger.debug("Setting up consolidated lifecycle hooks")

        # Screen-related hooks
        self._setup_screen_hooks()

        # Startup-related hooks
        self._setup_startup_hooks()

    def _setup_screen_hooks(self):
        """
        @brief Setup screen-related hooks
        """
        logger.debug("Setting up screen hooks")

        @hook.subscribe.screen_change
        def handle_screen_change(*args: Any, **kwargs: Any) -> None:
            """Handle screen configuration changes (monitor hotplug/unplug)"""
            # Some qtile versions don't pass event parameter
            event = args[0] if args else None
            self._handle_screen_change_event(event)

        @hook.subscribe.current_screen_change
        def handle_current_screen_change(*args: Any, **kwargs: Any) -> None:
            """Handle changes to the current screen focus"""
            # Some qtile versions don't pass event parameter
            event = args[0] if args else None
            self._handle_current_screen_change_event(event)

    def _setup_startup_hooks(self):
        """
        @brief Setup startup-related hooks
        """
        logger.debug("Setting up startup hooks")

        @hook.subscribe.startup_once
        def start_color_watcher():  # Used by qtile hook system
            """Start the color file watcher when qtile starts"""
            logger.info("Qtile startup_once hook called")

        @hook.subscribe.startup_once
        def run_autostart():  # Used by qtile hook system
            """Run autostart script when qtile starts"""
            self.run_autostart_script()

        @hook.subscribe.startup_complete
        def setup_color_watching():  # Used by qtile hook system
            """Additional setup after qtile is fully loaded"""
            logger.info("Qtile startup completed - starting color monitoring")

            # Initialize notification system
            try:
                show_popup_notification(
                    "Qtile Startup", "Notification system initialized", "normal"
                )
                logger.info("✅ Notification system initialized successfully")
            except Exception as e:
                logger.warning(f"❌ Failed to initialize notification system: {e}")

            try:
                # Check if already monitoring
                if self.color_manager and self.color_manager.is_monitoring():
                    logger.info("Color monitoring already active")
                    return

                # Attempt to start monitoring
                logger.info("Starting color file monitoring...")
                if self.color_manager:
                    self.color_manager.start_monitoring()

                    # Verify it started successfully
                    if self.color_manager.is_monitoring():
                        logger.info("✅ Color monitoring started successfully")
                        logger.info(f"Watching: {self.color_manager.colors_file}")
                    else:
                        logger.warning("❌ Color monitoring failed to start")
                        # Try force start as fallback
                        logger.info("Attempting force start...")
                        if hasattr(self.color_manager, "force_start_monitoring"):
                            result = self.color_manager.force_start_monitoring()
                            logger.info(f"Force start result: {result}")

            except Exception as e:
                logger.error(f"Failed to start color monitoring: {e}")
                logger.error("Color changes won't trigger automatic qtile restart")
                logger.error("Use Super + Ctrl + C for manual color reload")

        @hook.subscribe.startup_complete
        def enforce_tiling_on_restart():  # Used by qtile hook system
            """Force all windows to tile after qtile restart (except explicitly floating ones)"""
            self._schedule_window_retiling()

    def _safe_execute(
        self, operation: str, func: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> bool:
        """
        @brief Safely execute an operation with error handling
        @param operation Description of the operation for logging
        @param func Function to execute
        @param args Positional arguments for the function
        @param kwargs Keyword arguments for the function
        @return True if successful, False otherwise
        """
        try:
            func(*args, **kwargs)
            logger.info(f"✅ {operation} completed successfully")
            return True
        except Exception as e:
            logger.error(f"❌ {operation} failed: {e}")
            if operation.startswith(("Color monitoring", "Screen")):
                logger.error(traceback.format_exc())
            return False

    def _validate_setting(
        self,
        setting_name: str,
        value: Any,
        min_val: float = 0,
        max_val: float | None = None,
        warning_threshold: float | None = None,
    ) -> tuple[bool, str | None]:
        """
        @brief Validate a numeric setting and return (is_valid, error_message)
        @param setting_name Name of the setting for error messages
        @param value Value to validate
        @param min_val Minimum allowed value
        @param max_val Maximum allowed value (optional)
        @param warning_threshold Value that triggers a warning (optional)
        @return Tuple of (is_valid, error_message)
        """
        if not isinstance(value, int | float) or value < min_val:
            return False, f"{setting_name} must be a number ≥ {min_val}"

        if max_val and value > max_val:
            return False, f"{setting_name} is too high (>{max_val})"

        if warning_threshold and value > warning_threshold:
            logger.warning(f"{setting_name} is quite high (>{warning_threshold})")

        return True, None

    def _handle_screen_change_event(self, event: Any = None) -> None:
        """
        @brief Handle screen configuration changes with proper timing and validation
        @param event Screen change event (optional)
        """
        time.sleep(self.config.screen_settings["detection_delay"])

        startup_time = (
            getattr(self.color_manager, "_startup_time", time.time())
            if self.color_manager
            else time.time()
        )
        current_time = time.time()

        if current_time - startup_time > self.config.screen_settings["startup_delay"]:
            logger.info("Screen change detected - checking for monitor changes")
            if event is not None:
                logger.debug(f"Screen change event data: {event}")

            if self._refresh_and_check_screens():
                logger.info("Monitor configuration changed - updating screens")
                self._reconfigure_screens()
            else:
                logger.info("Screen change detected but count unchanged")
        else:
            logger.info("Screen change detected but ignored (too soon after startup)")

    def _handle_current_screen_change_event(self, event: Any = None) -> None:
        """
        @brief Handle changes to current screen focus
        @param event Screen change event (optional)
        """
        try:
            if qtile and qtile.current_screen:
                screen_index = qtile.screens.index(qtile.current_screen)
                logger.debug(f"Current screen changed to: {screen_index}")
                if event is not None:
                    logger.debug(f"Screen change event data: {event}")
        except Exception as e:
            logger.debug(f"Error handling current screen change: {e}")

    def _refresh_and_check_screens(self) -> bool:
        """
        @brief Refresh screen detection and check if configuration changed
        @return True if screens changed, False otherwise
        """
        try:
            from modules.screens import refresh_screens

            return refresh_screens()
        except Exception as e:
            logger.error(f"Error refreshing screens: {e}")
            return False

    def _reconfigure_screens(self):
        """
        @brief Reconfigure screens with new monitor setup
        """
        try:
            if qtile is not None:
                from modules.bars import EnhancedBarManager
                from modules.screens import get_screen_count
                from qtile_config import QtileConfig

                new_screen_count = get_screen_count()
                config = QtileConfig()
                bar_manager = EnhancedBarManager(self.color_manager, config)
                new_screens = bar_manager.create_screens(new_screen_count)

                qtile.config.screens = new_screens
                logger.info(f"Restarting qtile with {new_screen_count} screens")
                qtile.restart()
            else:
                logger.warning(
                    "Could not get qtile instance for screen reconfiguration"
                )
        except Exception as e:
            logger.error(f"Error reconfiguring screens: {e}")
            logger.error(traceback.format_exc())

    def run_autostart_script(self):
        """
        @brief Run the autostart script
        """
        try:
            autostart_script = Path(self.config.autostart_script)
            if autostart_script.exists() and os.access(autostart_script, os.X_OK):
                logger.info(f"Running autostart script: {autostart_script}")
                subprocess.Popen(
                    [str(autostart_script)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True,
                )
                logger.info("Autostart script launched successfully")
        except Exception as e:
            logger.error(f"Failed to launch autostart script: {e}")

    def _schedule_window_retiling(self):
        """
        @brief Schedule window retiling with a delay
        """

        def retile_windows():
            if qtile and self.window_manager:
                try:
                    retiled_count = self.window_manager.retile_windows_after_startup(
                        qtile
                    )
                    logger.info(
                        f"Startup retiling completed - {retiled_count} windows processed"
                    )
                except Exception as e:
                    logger.error(f"Error during startup window retiling: {e}")

        # Schedule retiling with a small delay to ensure all windows are restored
        if qtile:
            qtile.call_later(1.0, retile_windows)

    def get_screen_status(self) -> dict[str, Any]:
        """
        @brief Get current screen configuration status
        @return Dictionary containing screen status information
        """
        try:
            from modules.screens import get_screen_count

            status = {
                "screen_count": get_screen_count(),
                "detection_delay": self.config.screen_settings["detection_delay"],
                "startup_delay": self.config.screen_settings["startup_delay"],
                "qtile_screens": len(qtile.screens) if qtile else 0,
                "current_screen": (
                    qtile.screens.index(qtile.current_screen)
                    if qtile and qtile.current_screen
                    else None
                ),
            }

            if qtile:
                status["screen_details"] = [
                    {
                        "index": i,
                        "width": screen.width,
                        "height": screen.height,
                        "x": screen.x,
                        "y": screen.y,
                        "group": screen.group.name if screen.group else None,
                    }
                    for i, screen in enumerate(qtile.screens)
                ]

            return status
        except Exception as e:
            logger.error(f"Error getting screen status: {e}")
            return {"error": str(e)}

    def validate_screen_configuration(self) -> dict[str, Any]:
        """
        @brief Validate the screen configuration settings
        @return Validation results dictionary
        """
        validation: dict[str, Any] = {"valid": True, "warnings": [], "errors": []}

        try:
            delay = self.config.screen_settings["detection_delay"]
            is_valid, error = self._validate_setting(
                "Detection delay", delay, 0, None, 5
            )
            if not is_valid:
                validation["errors"].append(error)
                validation["valid"] = False

            startup_delay = self.config.screen_settings["startup_delay"]
            is_valid, error = self._validate_setting(
                "Startup delay", startup_delay, 0, None, 60
            )
            if not is_valid:
                validation["errors"].append(error)
                validation["valid"] = False

        except (AttributeError, KeyError, TypeError) as e:
            validation["errors"].append(f"Missing or invalid screen settings: {e}")
            validation["valid"] = False

        return validation

    def validate_autostart_script(self) -> dict[str, Any]:
        """
        @brief Validate the autostart script configuration
        @return Validation results dictionary
        """
        try:
            script_path = self.config.autostart_script
            script_path_obj = Path(script_path)
            return {
                "valid": script_path_obj.exists() and os.access(script_path, os.X_OK),
                "exists": script_path_obj.exists(),
                "executable": os.access(script_path, os.X_OK),
                "path": script_path,
                "errors": [],
            }
        except Exception:
            return {
                "valid": False,
                "errors": ["No autostart script configured"],
            }

    def get_lifecycle_status(self) -> dict[str, Any]:
        """
        @brief Get status of all lifecycle components
        @return Status information dictionary
        """
        return {
            "color_monitoring": (
                self.color_manager.is_monitoring() if self.color_manager else False
            ),
            "autostart_validation": self.validate_autostart_script(),
            "screen_validation": self.validate_screen_configuration(),
            "screen_status": self.get_screen_status(),
        }

    def force_screen_refresh(self):
        """
        @brief Manually force a screen refresh (for testing/debugging)
        """
        logger.info("Forcing screen refresh")
        try:
            if self._refresh_and_check_screens():
                logger.info("Screen configuration changed during manual refresh")
                self._reconfigure_screens()
            else:
                logger.info(
                    "No screen configuration change detected during manual refresh"
                )
        except Exception as e:
            logger.error(f"Error during forced screen refresh: {e}")

    def get_screen_change_history(self) -> list[Any]:
        """
        @brief Get history of screen changes (placeholder for future implementation)
        @return List of screen change events
        """
        # This could be implemented to track screen change events over time
        # Useful for debugging monitor hotplug issues
        return []

    def _count_registered_hooks(self) -> dict[str, int]:
        """
        @brief Count registered lifecycle hooks
        @return Dictionary with hook counts by type
        """
        return {
            "screen_change": 1,  # handle_screen_change
            "current_screen_change": 1,  # handle_current_screen_change
            "startup_once": 2,  # start_color_watcher, run_autostart
            "startup_complete": 2,  # setup_color_watching, enforce_tiling_on_restart
        }


# Factory function for backward compatibility
def create_lifecycle_hooks(
    config: Any,
    color_manager: "ColorManager | None" = None,
    window_manager: "WindowManager | None" = None,
) -> LifecycleHooks:
    """
    @brief Create and return a lifecycle hooks instance
    @param config Qtile configuration object
    @param color_manager Color manager instance (optional)
    @param window_manager Window manager instance (optional)
    @return Configured LifecycleHooks instance
    """
    return LifecycleHooks(config, color_manager, window_manager)


# Maintain backward compatibility
__all__ = [
    "LifecycleHooks",
    "create_lifecycle_hooks",
]
