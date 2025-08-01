#!/usr/bin/env python3
"""
Hotkey display module for qtile
Shows a popup window with all configured keybindings
Similar to AwesomeWM's Super+S functionality
Refactored for better maintainability while preserving backward compatibility
"""

# Import all functionality from the new modular structure
from .hotkey_management import (
    HotkeyDisplay,
    create_hotkey_display,
    HotkeyCategorizer,
    KeyFormatter,
    ThemeManager
)

# Maintain backward compatibility by exposing the same interface
__all__ = [
    'HotkeyDisplay',
    'create_hotkey_display',
    'HotkeyCategorizer',
    'KeyFormatter',
    'ThemeManager'
]
