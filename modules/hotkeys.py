#!/usr/bin/env python3
"""
Hotkey display module for qtile
Shows a popup window with all configured keybindings
Similar to AwesomeWM's Super+S functionality
Refactored for better maintainability while preserving backward compatibility
"""

# Import all functionality from the modular structure
from .hotkey_display import HotkeyDisplay, create_hotkey_display
from .hotkey_categorizer import HotkeyCategorizer
from .hotkey_formatter import KeyFormatter
from .hotkey_themes import ThemeManager

# Maintain backward compatibility by exposing the same interface
__all__ = [
    'HotkeyDisplay',
    'create_hotkey_display',
    'HotkeyCategorizer',
    'KeyFormatter',
    'ThemeManager'
]
