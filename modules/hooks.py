#!/usr/bin/env python3
"""
Hooks module for qtile
Handles qtile hooks and event management
Refactored for better maintainability while preserving backward compatibility
"""

from .client_hooks import ClientHooks

# Import all functionality from the new modular structure
from .hook_manager import HookManager, create_hook_manager
from .lifecycle_hooks import LifecycleHooks, create_lifecycle_hooks

# Maintain backward compatibility by exposing the same interface
__all__ = [
    "ClientHooks",
    "HookManager",
    "LifecycleHooks",
    "create_hook_manager",
    "create_lifecycle_hooks",
]
