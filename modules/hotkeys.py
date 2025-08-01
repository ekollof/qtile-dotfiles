#!/usr/bin/env python3
"""
Hotkey display module for qtile
Shows a popup window with all configured keybindings
Similar to AwesomeWM's Super+S functionality
"""

import subprocess
from libqtile.log_utils import logger


class HotkeyDisplay:
    """Manages hotkey display functionality"""

    def __init__(self, key_manager, color_manager=None):
        self.key_manager = key_manager
        self.color_manager = color_manager
        self.rofi_theme = self._get_rofi_theme()

    def _get_colors(self):
        """Get current colors from color manager"""
        if self.color_manager:
            colors = self.color_manager.get_colors()
            return {
                'background': colors['special']['background'],
                'foreground': colors['special']['foreground'],
                'accent': colors['colors']['color4'],  # Usually blue
                'secondary': colors['colors']['color8'],  # Usually gray
                'highlight': colors['colors']['color3']  # Usually yellow/orange
            }
        else:
            # Fallback colors
            return {
                'background': '#1e1e1e',
                'foreground': '#d4d4d4',
                'accent': '#569cd6',
                'secondary': '#666666',
                'highlight': '#dcdcaa'
            }

    def _get_rofi_theme(self):
        """Get rofi theme configuration for hotkey display"""
        colors = self._get_colors()

        return f"""
configuration {{
    show-icons: false;
    location: 0;
    disable-history: true;
    hide-scrollbar: true;
    display-keys: "Qtile Hotkeys";
}}

* {{
    background-color: {colors['background']};
    text-color: {colors['foreground']};
    border-color: {colors['accent']};
    width: 1200;
    font: "Monospace 11";
}}

window {{
    transparency: "real";
    background-color: {colors['background']}ee;
    border: 2px;
    border-radius: 8px;
    padding: 20px;
}}

inputbar {{
    background-color: {colors['secondary']};
    text-color: {colors['foreground']};
    border: 1px;
    border-radius: 4px;
    padding: 8px;
    margin: 0px 0px 10px 0px;
}}

prompt {{
    background-color: transparent;
    text-color: {colors['highlight']};
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
    text-color: {colors['foreground']};
    orientation: horizontal;
    border-radius: 4px;
    padding: 6px;
}}

element selected {{
    background-color: {colors['accent']};
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

    def _format_key_combination(self, key_combo):
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

    def _get_hotkey_list(self):
        """Generate list of hotkeys with descriptions"""
        # Categories for organizing hotkeys
        categories = {
            "Window Management": [],
            "Layout Control": [],
            "Group/Workspace": [],
            "System": [],
            "Applications": [],
            "Screen/Display": [],
            "Other": []
        }

        # Get keys from key manager
        keys = self.key_manager.get_keys()

        for key in keys:
            # Extract modifiers and key
            modifiers = key.modifiers if key.modifiers else []
            key_name = key.key

            # Combine modifiers and key
            if modifiers:
                key_combo = "+".join(modifiers) + "+" + key_name
            else:
                key_combo = key_name

            # Format the key combination
            formatted_combo = self._format_key_combination(key_combo)

            # Get description
            description = getattr(key, 'desc', None)
            if not description:
                # Try to infer description from the command
                if hasattr(key, 'commands') and key.commands:
                    cmd = key.commands[0]
                    if hasattr(cmd, '__name__'):
                        description = cmd.__name__.replace('_', ' ').title()
                    elif hasattr(cmd, 'name'):
                        description = cmd.name.replace('_', ' ').title()
                    else:
                        cmd_str = str(cmd)
                        if 'spawn' in cmd_str.lower():
                            # Extract spawn command
                            if hasattr(cmd, 'args') and cmd.args:
                                app_name = cmd.args[0].split(
                                    '/')[-1] if '/' in cmd.args[0] else cmd.args[0]
                                description = f"Launch {app_name}"
                            else:
                                description = "Launch application"
                        elif 'layout' in cmd_str.lower():
                            description = "Change layout"
                        elif 'group' in cmd_str.lower():
                            description = "Switch group"
                        elif 'window' in cmd_str.lower():
                            description = "Window action"
                        else:
                            description = cmd_str[:50]
                else:
                    description = "Custom action"

            # Categorize the hotkey
            category = "Other"
            desc_lower = description.lower()

            if any(
                word in desc_lower for word in [
                    'window',
                    'focus',
                    'move',
                    'close',
                    'kill',
                    'floating']):
                category = "Window Management"
            elif any(word in desc_lower for word in ['layout', 'tile', 'max', 'split']):
                category = "Layout Control"
            elif any(word in desc_lower for word in ['group', 'workspace']) or key_name.isdigit():
                category = "Group/Workspace"
            elif any(word in desc_lower for word in ['restart', 'quit', 'shutdown', 'reload', 'screen', 'color']):
                category = "System"
            elif any(word in desc_lower for word in ['launch', 'spawn', 'browser', 'terminal']):
                category = "Applications"
            elif any(word in desc_lower for word in ['screen', 'monitor', 'display']):
                category = "Screen/Display"

            # Format for display
            hotkey_line = f"{formatted_combo:<25} {description}"
            categories[category].append(hotkey_line)

        # Build the final hotkey list with categories
        final_hotkeys = []

        for category_name, category_hotkeys in categories.items():
            if category_hotkeys:  # Only show categories that have hotkeys
                final_hotkeys.append("")  # Empty line
                final_hotkeys.append(f"=== {category_name} ===")
                # Sort hotkeys within category
                category_hotkeys.sort()
                final_hotkeys.extend(category_hotkeys)

        # Add instructions at the top
        instructions = [
            "Press Escape or Enter to close this window",
            "Tip: Most actions use Super (Windows) key as modifier",
            ""
        ]

        return instructions + final_hotkeys

    def show_hotkeys(self):
        """Display hotkeys using rofi"""
        try:
            # Get hotkey list
            hotkeys = self._get_hotkey_list()

            # Create input for rofi
            rofi_input = "\n".join(hotkeys)

            # Create temporary theme file
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(mode='w', suffix='.rasi', delete=False) as theme_file:
                theme_file.write(self.rofi_theme)
                theme_file_path = theme_file.name

            try:
                # Run rofi with hotkey list
                cmd = [
                    "rofi",
                    "-dmenu",
                    "-theme", theme_file_path,
                    "-p", "Qtile Hotkeys (press Escape to close)",
                    "-mesg", "Available keyboard shortcuts - Press Enter to close",
                    "-no-custom",
                    "-format", "i",
                    "-i"
                ]

                logger.info("Showing hotkey display")

                # Run rofi
                subprocess.run(
                    cmd,
                    input=rofi_input,
                    text=True,
                    capture_output=True,
                    timeout=30
                )

                # Don't need to handle the output since this is just for display
                logger.debug("Hotkey display closed")

            finally:
                # Clean up temporary theme file
                try:
                    os.unlink(theme_file_path)
                except BaseException:
                    pass

        except subprocess.TimeoutExpired:
            logger.warning("Hotkey display timed out")
        except FileNotFoundError:
            logger.error("rofi not found - please install rofi to use hotkey display")
            # Fallback to simple notification
            try:
                subprocess.run([
                    "notify-send",
                    "Qtile Hotkeys",
                    "Install 'rofi' to see hotkey display\nPress Super+S to show hotkeys",
                    "-t", "3000"
                ], check=False)
            except BaseException:
                pass
        except Exception as e:
            logger.error(f"Error showing hotkeys: {e}")

    def show_hotkeys_simple(self):
        """Fallback method using dmenu if rofi is not available"""
        try:
            hotkeys = self._get_hotkey_list()
            dmenu_input = "\n".join(hotkeys)

            # Get colors for dmenu
            colors = self._get_colors()

            cmd = [
                "dmenu",
                "-l", "25",  # Show 25 lines
                "-p", "Qtile Hotkeys (ESC to close):",
                "-fn", "Monospace-11",
                "-nb", colors['background'],  # Normal background
                "-nf", colors['foreground'],  # Normal foreground
                "-sb", colors['accent'],      # Selected background
                "-sf", "#ffffff"              # Selected foreground
            ]

            subprocess.run(
                cmd,
                input=dmenu_input,
                text=True,
                capture_output=True,
                timeout=30
            )

        except FileNotFoundError:
            logger.error("Neither rofi nor dmenu found - cannot show hotkeys")
            # Try with notification as final fallback
            try:
                subprocess.run([
                    "notify-send",
                    "Qtile Hotkeys",
                    "Super+S: Show hotkeys (install rofi/dmenu)\nSuper+Shift+R: Restart\nSuper+Q: Close window\nSuper+Return: Terminal",
                    "-t", "5000"
                ], check=False)
            except BaseException:
                pass
        except Exception as e:
            logger.error(f"Error showing hotkeys with dmenu: {e}")


def create_hotkey_display(key_manager, color_manager=None):
    """Create and return a hotkey display instance"""
    return HotkeyDisplay(key_manager, color_manager)
