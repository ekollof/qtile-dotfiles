#!/usr/bin/env python3
"""
Startup hooks for qtile - SIMPLIFIED VERSION
"""

import os
import subprocess
from pathlib import Path
from typing import Any

from libqtile import hook, qtile
from libqtile.log_utils import logger
from .simple_popup_notifications import show_popup_notification


class StartupHooks:
    """Handles startup-related hooks and autostart functionality"""

    def __init__(self, config: Any, color_manager: Any, window_manager: Any) -> None:
        self.config = config
        self.color_manager = color_manager
        self.window_manager = window_manager

    def setup_startup_hooks(self):
        """Setup all startup-related hooks"""
        logger.debug("Setting up simplified startup hooks")

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
            logger.info(
                "Qtile startup completed - starting simplified color monitoring"
            )

            # Initialize notification system
            try:
                show_popup_notification("Qtile Startup", "Notification system initialized", "normal")
                logger.info("✅ Notification system initialized successfully")
            except Exception as e:
                logger.warning(f"❌ Failed to initialize notification system: {e}")
            try:
                # Check if already monitoring
                if self.color_manager.is_monitoring():
                    logger.info("Color monitoring already active")
                    return

                # Attempt to start monitoring
                logger.info("Starting color file monitoring...")
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

    def run_autostart_script(self):
        """Run the autostart script"""
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
        """Schedule window retiling with a delay"""

        def retile_windows():
            if qtile:
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

    # Simplified compatibility methods
    def validate_autostart_script(self) -> dict[str, Any]:
        """Validate the autostart script configuration"""
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
        except:
            return {
                "valid": False,
                "errors": ["No autostart script configured"],
            }

    def get_startup_status(self) -> dict[str, Any]:
        """Get status of startup components"""
        return {
            "color_monitoring": (
                self.color_manager.is_monitoring() if self.color_manager else False
            ),
            "autostart_validation": self.validate_autostart_script(),
        }
