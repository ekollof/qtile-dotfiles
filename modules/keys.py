#!/usr/bin/env python3
"""
Key bindings module for qtile
Handles keyboard shortcuts and window management
Refactored for better maintainability while preserving backward compatibility
"""

from .commands import LayoutAwareCommands, SystemCommands, WindowCommands
from .key_bindings import KeyBindings

# Import all functionality from the new modular structure
from .key_manager import KeyManager, create_key_manager

# Maintain backward compatibility by exposing the same interface
__all__ = [
    "KeyBindings",
    "KeyManager",
    "LayoutAwareCommands",
    "SystemCommands",
    "WindowCommands",
    "create_key_manager",
]
