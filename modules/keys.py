#!/usr/bin/env python3
"""
Key bindings module for qtile
Handles keyboard shortcuts and window management
Refactored for better maintainability while preserving backward compatibility
"""

from .key_bindings import KeyBindings

# Import all functionality from the new modular structure
from .key_manager import KeyManager, create_key_manager
from .layout_aware import LayoutAwareCommands
from .system_commands import SystemCommands
from .window_commands import WindowCommands

# Maintain backward compatibility by exposing the same interface
__all__ = [
    "KeyManager",
    "create_key_manager",
    "LayoutAwareCommands",
    "WindowCommands",
    "SystemCommands",
    "KeyBindings",
]
