#!/usr/bin/env python3
"""
Screen management module for qtile
Handles automatic screen detection and configuration
"""

import json
import os
import subprocess

from libqtile.log_utils import logger


class ScreenManager:
    """Manages screen detection and configuration"""

    _instance = None

    def __init__(self) -> None:
        self.display_override: int = 0  # Set to 0 for auto-detection
        self.num_screens: int = 1
        self._detected: bool = False  # Track if detection has run

    def detect_screens(self):
        """Detect number of screens using system tools"""
        # Mark as detected to avoid redundant calls
        self._detected = True
        
        if self.display_override == 0:
            try:
                if self._is_xephyr_environment():
                    self.num_screens = 1
                    return

                if self._try_wayland_detection():
                    return

                self._try_x11_detection()

                if self.num_screens == 0:
                    self.num_screens = 1

            except Exception as e:
                logger.error(f"Screen detection error: {e}")
                self.num_screens = 1

            logger.info(f"Auto-detected {self.num_screens} screens")
        else:
            self.num_screens = self.display_override
            logger.info(f"Using override: {self.num_screens} screens")

    def refresh_screens(self):
        """Re-detect and update screen count"""
        old_count = self.num_screens
        self.detect_screens()
        if old_count != self.num_screens:
            logger.info(f"Screen count changed from {old_count} to {self.num_screens}")
            return True
        return False

    def get_screen_count(self) -> int:
        """Get detected screen count (triggers detection on first call)"""
        if not self._detected:
            self.detect_screens()
        return self.num_screens

    def set_override(self, count: int) -> None:
        """Set manual screen count override"""
        self.display_override = count
        self.detect_screens()

    def _is_xephyr_environment(self) -> bool:
        """Check if we're in Xephyr testing environment"""
        display = os.getenv("DISPLAY", "")
        if ":99" in display or any("Xephyr" in str(v) for v in os.environ.values()):
            logger.info("Detected Xephyr testing environment - using single screen")
            return True
        return False

    def _try_wayland_detection(self) -> bool:
        """Try Wayland screen detection using wlr-randr"""
        try:
            result = subprocess.run(
                ["wlr-randr", "--json"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                outputs = json.loads(result.stdout)
                connected_screens = [o for o in outputs if o.get("enabled", False)]
                self.num_screens = len(connected_screens)
                logger.info(f"Wayland: Found {self.num_screens} enabled outputs")
                return True
        except Exception:
            pass
        return False

    def _try_x11_detection(self):
        """Try X11 screen detection using xrandr"""
        try:
            if self._try_xrandr_query():
                return
            self._try_xrandr_listmonitors()
        except Exception as e:
            logger.warning(f"Screen detection failed: {e}")
            self.num_screens = 1

    def _try_xrandr_query(self) -> bool:
        """Try xrandr --query for screen detection"""
        result = subprocess.run(
            ["xrandr", "--query"], capture_output=True, text=True, timeout=3
        )
        if result.returncode == 0:
            lines = result.stdout.split("\n")
            connected_count = 0
            for line in lines:
                if (
                    " connected " in line
                    and not line.startswith(" ")
                    and any(
                        char.isdigit() and "x" in line.split("connected")[1]
                        for char in line.split("connected")[1]
                    )
                ):
                    connected_count += 1

            if connected_count > 0:
                self.num_screens = connected_count
                logger.info(f"X11: Found {self.num_screens} active displays")
                return True
        return False

    def _try_xrandr_listmonitors(self):
        """Try xrandr --listmonitors as fallback"""
        result = subprocess.run(
            ["xrandr", "--listmonitors"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            if lines and "Monitors:" in lines[0]:
                self.num_screens = int(lines[0].split(":")[1].strip())
            else:
                self.num_screens = max(
                    1, len([line for line in lines[1:] if line.strip()])
                )
            logger.info(f"X11 listmonitors: Found {self.num_screens} monitors")
        else:
            raise Exception("xrandr --listmonitors failed")


# Global screen manager instance (singleton)
_screen_manager = None


def _get_screen_manager() -> ScreenManager:
    """Get or create the singleton screen manager instance"""
    global _screen_manager
    if _screen_manager is None:
        _screen_manager = ScreenManager()
    return _screen_manager


def refresh_screens():
    """Refresh screen detection"""
    return _get_screen_manager().refresh_screens()


def get_screen_count() -> int:
    """Get the number of screens (triggers detection on first call)"""
    return _get_screen_manager().get_screen_count()


def set_screen_override(count: int) -> None:
    """Set manual screen count override"""
    _get_screen_manager().set_override(count)
