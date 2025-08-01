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

    def __init__(self):
        self.display_override = 0  # Set to 0 for auto-detection
        self.num_screens = 1
        self.detect_screens()

    def detect_screens(self):
        """Detect number of screens using system tools"""
        if self.display_override == 0:
            try:
                # Check if we're in Xephyr (testing environment)
                display = os.environ.get('DISPLAY', '')
                if ':99' in display or 'Xephyr' in str(os.environ):
                    logger.info("Detected Xephyr testing environment - using single screen")
                    self.num_screens = 1
                    return

                # Try using wlr-randr for Wayland or xrandr for X11
                try:
                    # First try wlr-randr (Wayland)
                    result = subprocess.run(['wlr-randr', '--json'],
                                            capture_output=True, text=True, timeout=2)
                    if result.returncode == 0:
                        outputs = json.loads(result.stdout)
                        connected_screens = [o for o in outputs if o.get('enabled', False)]
                        self.num_screens = len(connected_screens)
                        logger.info(f"Wayland: Found {self.num_screens} enabled outputs")
                    else:
                        raise Exception("wlr-randr failed")
                except BaseException:
                    # Fall back to xrandr (X11) with more robust detection
                    try:
                        # First try to query connected outputs
                        result = subprocess.run(['xrandr', '--query'],
                                                capture_output=True, text=True, timeout=3)
                        if result.returncode == 0:
                            # Count connected displays
                            lines = result.stdout.split('\n')
                            connected_count = 0
                            for line in lines:
                                if ' connected ' in line and not line.startswith(' '):
                                    # Check if it has a resolution (is active)
                                    if any(char.isdigit() and 'x' in line.split('connected')
                                           [1] for char in line.split('connected')[1]):
                                        connected_count += 1

                            if connected_count > 0:
                                self.num_screens = connected_count
                                logger.info(f"X11: Found {self.num_screens} active displays")
                            else:
                                # Fallback to --listmonitors
                                result = subprocess.run(['xrandr', '--listmonitors'],
                                                        capture_output=True, text=True, timeout=2)
                                if result.returncode == 0:
                                    lines = result.stdout.strip().split('\n')
                                    if lines and 'Monitors:' in lines[0]:
                                        self.num_screens = int(lines[0].split(':')[1].strip())
                                    else:
                                        self.num_screens = max(
                                            1, len([line for line in lines[1:] if line.strip()]))
                                    logger.info(
                                        f"X11 listmonitors: Found {
                                            self.num_screens} monitors")
                                else:
                                    raise Exception("xrandr --listmonitors failed")
                        else:
                            raise Exception("xrandr --query failed")
                    except Exception as e:
                        logger.warning(f"Screen detection failed: {e}")
                        # Final fallback
                        self.num_screens = 1

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

    def get_screen_count(self):
        """Get the number of detected screens"""
        return self.num_screens

    def set_override(self, count):
        """Set manual screen count override"""
        self.display_override = count
        self.detect_screens()


# Global screen manager instance
screen_manager = ScreenManager()


def refresh_screens():
    """Refresh screen detection"""
    return screen_manager.refresh_screens()


def get_screen_count():
    """Get the number of screens"""
    return screen_manager.get_screen_count()


def set_screen_override(count):
    """Set manual screen count override"""
    screen_manager.set_override(count)
