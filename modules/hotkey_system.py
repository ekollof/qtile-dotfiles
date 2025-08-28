#!/usr/bin/env python3
"""
@brief Consolidated hotkey system for qtile
@file hotkey_system.py

This module consolidates all hotkey-related functionality into a single,
well-organized system with improved maintainability and performance.

Features:
- Hotkey categorization and organization
- Key combination formatting and display
- Theme management for hotkey display
- Rofi/dmenu integration with fallback support
- Comprehensive error handling and validation

@author Qtile configuration system
@note This module follows Python 3.10+ standards and project guidelines
"""

import contextlib
import os
import subprocess
import tempfile
from typing import TYPE_CHECKING, Any, final

from libqtile.log_utils import logger

if TYPE_CHECKING:
    from modules.color_management import ColorManager
    from modules.dependency_container import ManagerDependencies


class KeyFormatter:
    """Handles formatting of key combinations and descriptions"""

    @staticmethod
    def format_key_combination(key_combo: str) -> str:
        """Format key combination for display"""
        # Replace modifier names with more readable versions
        formatted = key_combo.replace("mod4", "Super")
        formatted = formatted.replace("mod1", "Alt")
        formatted = formatted.replace("shift", "Shift")
        formatted = formatted.replace("control", "Ctrl")

        # Capitalize single keys
        parts = formatted.split("+")
        if len(parts) > 1:
            # Last part is the main key
            parts[-1] = parts[-1].capitalize()
        else:
            parts[0] = parts[0].capitalize()

        return "+".join(parts)

    @staticmethod
    def extract_key_combination(key: Any) -> str:
        """Extract key combination from key object"""
        # Extract modifiers and key
        modifiers = key.modifiers if key.modifiers else []
        key_name = key.key

        # Combine modifiers and key
        key_combo = "+".join(modifiers) + "+" + key_name if modifiers else key_name

        return key_combo

    @staticmethod
    def infer_description(key: Any) -> str:
        """Infer description from key command if not explicitly provided"""
        # Try to get explicit description first
        description = getattr(key, "desc", None)
        if description:
            return description

        # Try to infer from commands
        if hasattr(key, "commands") and key.commands:
            cmd = key.commands[0]

            if hasattr(cmd, "__name__"):
                return cmd.__name__.replace("_", " ").title()
            elif hasattr(cmd, "name"):
                return cmd.name.replace("_", " ").title()
            else:
                return KeyFormatter._parse_command_string(cmd)

        return "Custom action"

    @staticmethod
    def _parse_command_string(cmd: Any) -> str:
        """Parse command string to extract meaningful description"""
        cmd_str = str(cmd).lower()

        # Use match statement for cleaner pattern matching
        match True:
            case _ if "spawn" in cmd_str:
                # Extract spawn command
                if hasattr(cmd, "args") and cmd.args:
                    app_name = (
                        cmd.args[0].split("/")[-1]
                        if "/" in cmd.args[0]
                        else cmd.args[0]
                    )
                    return f"Launch {app_name}"
                else:
                    return "Launch application"
            case _ if "layout" in cmd_str:
                return "Change layout"
            case _ if "group" in cmd_str:
                return "Switch group"
            case _ if "window" in cmd_str:
                return "Window action"
            case _:
                return str(cmd)[:50]  # Truncate long descriptions

    @staticmethod
    def format_hotkey_line(key_combo: str, description: str, width: int = 25) -> str:
        """Format a single hotkey line for display"""
        formatted_combo = KeyFormatter.format_key_combination(key_combo)
        return f"{formatted_combo:<{width}} {description}"

    @staticmethod
    def create_instructions() -> list[str]:
        """Create instruction lines for the hotkey display"""
        return [
            "Press Escape or Enter to close this window",
            "Tip: Most actions use Super (Windows) key as modifier",
            "",
        ]


class HotkeyCategorizer:
    """Handles categorization and organization of hotkeys"""

    def __init__(self) -> None:
        self.categories = {
            "Window Management": [],
            "Layout Control": [],
            "Group/Workspace": [],
            "System": [],
            "Applications": [],
            "Screen/Display": [],
            "Other": [],
        }

    def clear_categories(self):
        """Clear all categories"""
        for category in self.categories.values():
            category.clear()

    def categorize_key(self, key: Any) -> str:
        """Determine the appropriate category for a key"""
        key_name = key.key
        description = KeyFormatter.infer_description(key).lower()

        # Check if it's a number key (likely group/workspace)
        if key_name.isdigit():
            return "Group/Workspace"

        # Define keyword categories
        window_words = ["window", "focus", "move", "close", "kill", "floating"]
        layout_words = ["layout", "tile", "max", "split"]
        group_words = ["group", "workspace"]
        system_words = [
            "restart",
            "quit",
            "shutdown",
            "reload",
            "screen",
            "color",
        ]
        app_words = ["launch", "spawn", "browser", "terminal"]
        display_words = ["screen", "monitor", "display"]

        # Categorize based on description content using match statements
        match True:
            case _ if any(word in description for word in window_words):
                return "Window Management"
            case _ if any(word in description for word in layout_words):
                return "Layout Control"
            case _ if any(word in description for word in group_words):
                return "Group/Workspace"
            case _ if any(word in description for word in system_words):
                return "System"
            case _ if any(word in description for word in app_words):
                return "Applications"
            case _ if any(word in description for word in display_words):
                return "Screen/Display"
            case _:
                return "Other"

    def add_key_to_category(self, key: Any, category: str | None = None):
        """Add a key to the appropriate category"""
        if category is None:
            category = self.categorize_key(key)

        # Extract key combination and description
        key_combo = KeyFormatter.extract_key_combination(key)
        description = KeyFormatter.infer_description(key)

        # Format the hotkey line
        hotkey_line = KeyFormatter.format_hotkey_line(key_combo, description)

        # Add to category
        if category in self.categories:
            self.categories[category].append(hotkey_line)
        else:
            self.categories["Other"].append(hotkey_line)

    def process_keys(self, keys: list[Any]) -> dict[str, list[str]]:
        """Process a list of keys and categorize them"""
        self.clear_categories()

        for key in keys:
            self.add_key_to_category(key)

        # Sort hotkeys within each category
        for category_hotkeys in self.categories.values():
            category_hotkeys.sort()

        return self.categories

    def build_formatted_list(self, include_instructions: bool = True) -> list[str]:
        """Build the final formatted hotkey list with categories"""
        final_hotkeys = []

        # Add instructions if requested
        if include_instructions:
            final_hotkeys.extend(KeyFormatter.create_instructions())

        # Add categories with hotkeys
        for category_name, category_hotkeys in self.categories.items():
            if category_hotkeys:  # Only show categories that have hotkeys
                final_hotkeys.append("")  # Empty line for separation
                final_hotkeys.append(f"=== {category_name} ===")
                final_hotkeys.extend(category_hotkeys)

        return final_hotkeys

    def get_category_summary(self) -> dict[str, int]:
        """Get a summary of hotkeys per category"""
        return {
            category: len(hotkeys)
            for category, hotkeys in self.categories.items()
            if hotkeys
        }

    def search_hotkeys(self, search_term: str) -> list[str]:
        """Search for hotkeys containing the search term"""
        search_term = search_term.lower()
        results = []

        for category_name, category_hotkeys in self.categories.items():
            for hotkey in category_hotkeys:
                if search_term in hotkey.lower():
                    results.append(f"[{category_name}] {hotkey}")

        return results


class ThemeManager:
    """Manages themes for hotkey display applications"""

    def __init__(self, color_manager: "ColorManager | None" = None) -> None:
        self.color_manager = color_manager

    def get_colors(self) -> dict[str, str]:
        """Get current colors from color manager or fallback"""
        if self.color_manager:
            colors = self.color_manager.get_colors()
            return {
                "background": colors["special"]["background"],
                "foreground": colors["special"]["foreground"],
                "accent": colors["colors"]["color4"],  # Usually blue
                "secondary": colors["colors"]["color8"],  # Usually gray
                "highlight": colors["colors"]["color3"],  # Usually yellow/orange
            }
        else:
            # Fallback colors
            return {
                "background": "#1e1e1e",
                "foreground": "#d4d4d4",
                "accent": "#569cd6",
                "secondary": "#666666",
                "highlight": "#dcdcaa",
            }

    def get_rofi_theme(self) -> str:
        """Get rofi theme configuration for hotkey display"""
        colors = self.get_colors()

        theme_config = f"""
configuration {{
    show-icons: false;
    location: 0;
    disable-history: true;
    hide-scrollbar: true;
    display-keys: "Qtile Hotkeys";
}}

* {{
    background-color: {colors["background"]};
    text-color: {colors["foreground"]};
    border-color: {colors["accent"]};
    width: 1200;
    font: "Monospace 11";
}}

window {{
    transparency: "real";
    background-color: {colors["background"]}ee;
    border: 2px;
    border-radius: 8px;
    padding: 20px;
}}

inputbar {{
    background-color: {colors["secondary"]};
    text-color: {colors["foreground"]};
    border: 1px;
    border-radius: 4px;
    padding: 8px;
    margin: 0px 0px 10px 0px;
}}

prompt {{
    background-color: transparent;
    text-color: {colors["highlight"]};
    padding: 0px 8px 0px 0px;
}}

listview {{
    background-color: transparent;
    spacing: 2px;
    cycle: false;
    dynamic: true;
    layout: vertical;
}}

element {{
    background-color: transparent;
    text-color: {colors["foreground"]};
    orientation: horizontal;
    border-radius: 4px;
    padding: 6px;
}}

element selected {{
    background-color: {colors["accent"]};
    text-color: #ffffff;
}}

element-text {{
    background-color: inherit;
    text-color: inherit;
    expand: true;
    horizontal-align: 0;
    vertical-align: 0.5;
    margin: 0px 4px 0px 0px;
}}
"""
        return theme_config

    def get_dmenu_args(self) -> dict[str, str]:
        """Get dmenu arguments for styling"""
        colors = self.get_colors()

        return {
            "nb": colors["background"],  # Normal background
            "nf": colors["foreground"],  # Normal foreground
            "sb": colors["accent"],  # Selected background
            "sf": "#ffffff",  # Selected foreground
        }

    def get_rofi_command_args(self, theme_file_path: str) -> list[str]:
        """Get rofi command arguments with theme"""
        return [
            "rofi",
            "-dmenu",
            "-theme",
            theme_file_path,
            "-p",
            "Qtile Hotkeys (press Escape to close)",
            "-mesg",
            "Available keyboard shortcuts - Press Enter to close",
            "-no-custom",
            "-format",
            "i",
            "-i",
        ]

    def get_dmenu_command_args(self) -> list[str]:
        """Get dmenu command arguments with styling"""
        colors = self.get_colors()

        return [
            "dmenu",
            "-l",
            "25",  # Show 25 lines
            "-p",
            "Qtile Hotkeys (ESC to close):",
            "-fn",
            "Monospace-11",
            "-nb",
            colors["background"],
            "-nf",
            colors["foreground"],
            "-sb",
            colors["accent"],
            "-sf",
            "#ffffff",
        ]

    def create_notification_fallback_args(self) -> list[str]:
        """Create notification as ultimate fallback"""
        return [
            "notify-send",
            "Qtile Hotkeys",
            "Super+S: Show hotkeys (install rofi/dmenu)\nSuper+Shift+R: Restart\nSuper+Q: Close window\nSuper+Return: Terminal",
            "-t",
            "5000",
        ]

    def update_color_manager(self, color_manager: "ColorManager | None"):
        """Update the color manager reference"""
        self.color_manager = color_manager


@final
class HotkeyDisplay:
    """Manages hotkey display functionality"""

    def __init__(
        self, key_manager: Any, color_manager: "ColorManager | None" = None
    ) -> None:
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

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".rasi", delete=False
            ) as theme_file:
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
                    timeout=30,
                )

                logger.debug("Hotkey display closed")

            finally:
                # Clean up temporary theme file
                with contextlib.suppress(Exception):
                    os.unlink(theme_file_path)

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
                timeout=30,
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


def create_hotkey_display(
    key_manager: Any, color_manager: "ColorManager | None" = None
) -> HotkeyDisplay:
    """Create and return a hotkey display instance"""
    return HotkeyDisplay(key_manager, color_manager)


def create_hotkey_display_with_deps(
    key_manager: Any, deps: "ManagerDependencies"
) -> HotkeyDisplay:
    """
    @brief Create hotkey display using dependency injection
    @param key_manager Key manager instance
    @param deps ManagerDependencies container
    @return Configured HotkeyDisplay instance
    """
    return HotkeyDisplay(key_manager, deps.color_manager)


# Maintain backward compatibility
__all__ = [
    "HotkeyCategorizer",
    "HotkeyDisplay",
    "KeyFormatter",
    "ThemeManager",
    "create_hotkey_display",
    "create_hotkey_display_with_deps",
]
