#!/usr/bin/env python3
"""
Hooks module for qtile
Handles qtile hooks and event management
Refactored for better maintainability while preserving backward compatibility
"""

# Import all functionality from the new modular structure
from .hook_management import (
    HookManager,
    create_hook_manager,
    StartupHooks,
    ClientHooks,
    ScreenHooks,
    WindowManager
)

# Maintain backward compatibility by exposing the same interface
__all__ = [
    'HookManager',
    'create_hook_manager',
    'StartupHooks',
    'ClientHooks',
    'ScreenHooks',
    'WindowManager'
]
