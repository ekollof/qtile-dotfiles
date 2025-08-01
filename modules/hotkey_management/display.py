#!/usr/bin/env python3
"""
Main hotkey display class - orchestrates all hotkey display functionality
"""

import os
import subprocess
import tempfile
from typing import final, TYPE_CHECKING
from libqtile.log_utils import logger

from .categorizer import HotkeyCategorizer
from .themes import ThemeManager

if TYPE_CHECKING:
    from modules.color_management import ColorManager


@final
class HotkeyDisplay:
    """Manages hotkey display functionality"""

    def __init__(self, key_manager, color_manager: "ColorManager | None" = None) -> None:
        self.key_manager = key_manager
        self.color_manager = color_manager
        
        # Initialize components
        self.categorizer = HotkeyCategorizer()
        self.theme_manager = ThemeManager(color_manager)

    def _get_hotkey_list(self):
        """Generate list of hotkeys with descriptions"""
        # Get keys from key manager
        keys = self.key_manager.get_keys()
        
        # Process and categorize keys
        self.categorizer.process_keys(keys)
        
        # Build formatted list
        return self.categorizer.build_formatted_list(include_instructions=True)

    def show_hotkeys(self):
        """Display hotkeys using rofi"""
        try:
            # Get hotkey list
            hotkeys = self._get_hotkey_list()
            rofi_input = "\n".join(hotkeys)

            # Create temporary theme file
            rofi_theme = self.theme_manager.get_rofi_theme()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.rasi', delete=False) as theme_file:
                theme_file.write(rofi_theme)
                theme_file_path = theme_file.name

            try:
                # Get rofi command
                cmd = self.theme_manager.get_rofi_command_args(theme_file_path)
                
                logger.info("Showing hotkey display")

                # Run rofi
                subprocess.run(
                    cmd,
                    input=rofi_input,
                    text=True,
                    capture_output=True,
                    timeout=30
                )

                logger.debug("Hotkey display closed")

            finally:
                # Clean up temporary theme file
                try:
                    os.unlink(theme_file_path)
                except Exception:
                    pass

        except subprocess.TimeoutExpired:
            logger.warning("Hotkey display timed out")
        except FileNotFoundError:
            logger.error("rofi not found - please install rofi to use hotkey display")
            self._show_fallback_notification()
        except Exception as e:
            logger.error(f"Error showing hotkeys: {e}")

    def show_hotkeys_simple(self):
        """Fallback method using dmenu if rofi is not available"""
        try:
            hotkeys = self._get_hotkey_list()
            dmenu_input = "\n".join(hotkeys)

            # Get dmenu command
            cmd = self.theme_manager.get_dmenu_command_args()

            subprocess.run(
                cmd,
                input=dmenu_input,
                text=True,
                capture_output=True,
                timeout=30
            )

        except FileNotFoundError:
            logger.error("Neither rofi nor dmenu found - cannot show hotkeys")
            self._show_fallback_notification()
        except Exception as e:
            logger.error(f"Error showing hotkeys with dmenu: {e}")

    def _show_fallback_notification(self):
        """Show notification as final fallback"""
        try:
            cmd = self.theme_manager.create_notification_fallback_args()
            subprocess.run(cmd, check=False)
        except Exception:
            pass  # Silent failure for notification fallback

    def search_hotkeys(self, search_term: str):
        """Search for specific hotkeys"""
        keys = self.key_manager.get_keys()
        self.categorizer.process_keys(keys)
        return self.categorizer.search_hotkeys(search_term)

    def get_hotkey_summary(self):
        """Get summary of hotkeys by category"""
        keys = self.key_manager.get_keys()
        self.categorizer.process_keys(keys)
        return self.categorizer.get_category_summary()

    def update_color_manager(self, color_manager: "ColorManager | None"):
        """Update color manager for all components"""
        self.color_manager = color_manager
        self.theme_manager.update_color_manager(color_manager)


def create_hotkey_display(key_manager, color_manager: "ColorManager | None" = None) -> HotkeyDisplay:
    """Create and return a hotkey display instance"""
    return HotkeyDisplay(key_manager, color_manager)
