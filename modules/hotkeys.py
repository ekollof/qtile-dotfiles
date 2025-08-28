#!/usr/bin/env python3
"""
Hotkey display module for qtile
Shows a popup window with all configured keybindings
Similar to AwesomeWM's Super+S functionality
Refactored for better maintainability while preserving backward compatibility
"""

# Import all functionality from the consolidated hotkey system
from .hotkey_system import (
    HotkeyCategorizer,
    HotkeyDisplay,
    KeyFormatter,
    ThemeManager,
    create_hotkey_display,
)

# Maintain backward compatibility by exposing the same interface
__all__ = [
    "HotkeyCategorizer",
    "HotkeyDisplay",
    "KeyFormatter",
    "ThemeManager",
    "create_hotkey_display",
]
