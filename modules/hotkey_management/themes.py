#!/usr/bin/env python3
"""
Theme management for hotkey display
"""

from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from modules.simple_color_management import ColorManager


class ThemeManager:
    """Manages themes for hotkey display applications"""

    def __init__(self, color_manager: "ColorManager | None" = None):
        self.color_manager = color_manager

    def get_colors(self) -> Dict[str, str]:
        """Get current colors from color manager or fallback"""
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

    def get_rofi_theme(self) -> str:
        """Get rofi theme configuration for hotkey display"""
        colors = self.get_colors()

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

    def get_dmenu_args(self) -> Dict[str, str]:
        """Get dmenu arguments for styling"""
        colors = self.get_colors()

        return {
            'nb': colors['background'],   # Normal background
            'nf': colors['foreground'],   # Normal foreground
            'sb': colors['accent'],       # Selected background
            'sf': '#ffffff'               # Selected foreground
        }

    def get_rofi_command_args(self, theme_file_path: str) -> list[str]:
        """Get rofi command arguments with theme"""
        return [
            "rofi",
            "-dmenu",
            "-theme", theme_file_path,
            "-p", "Qtile Hotkeys (press Escape to close)",
            "-mesg", "Available keyboard shortcuts - Press Enter to close",
            "-no-custom",
            "-format", "i",
            "-i"
        ]

    def get_dmenu_command_args(self) -> list[str]:
        """Get dmenu command arguments with styling"""
        colors = self.get_colors()

        return [
            "dmenu",
            "-l", "25",  # Show 25 lines
            "-p", "Qtile Hotkeys (ESC to close):",
            "-fn", "Monospace-11",
            "-nb", colors['background'],
            "-nf", colors['foreground'],
            "-sb", colors['accent'],
            "-sf", "#ffffff"
        ]

    def create_notification_fallback_args(self) -> list[str]:
        """Create notification as ultimate fallback"""
        return [
            "notify-send",
            "Qtile Hotkeys",
            "Super+S: Show hotkeys (install rofi/dmenu)\nSuper+Shift+R: Restart\nSuper+Q: Close window\nSuper+Return: Terminal",
            "-t", "5000"
        ]

    def update_color_manager(self, color_manager: "ColorManager | None"):
        """Update the color manager reference"""
        self.color_manager = color_manager
