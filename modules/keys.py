#!/usr/bin/env python3
"""
Key bindings module for qtile
Handles keyboard shortcuts and window management
Refactored for better maintainability while preserving backward compatibility
"""

# Import all functionality from the new modular structure
from .key_management import (
    KeyManager,
    create_key_manager,
    LayoutAwareCommands,
    WindowCommands,
    SystemCommands,
    KeyBindings
)

# Maintain backward compatibility by exposing the same interface
__all__ = [
    'KeyManager',
    'create_key_manager',
    'LayoutAwareCommands',
    'WindowCommands',
    'SystemCommands',
    'KeyBindings'
]
