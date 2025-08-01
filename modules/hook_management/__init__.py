"""
Hook management package for qtile
Provides modular hook handling and event management functionality
"""

from .manager import HookManager, create_hook_manager
from .startup_hooks import StartupHooks
from .client_hooks import ClientHooks
from .screen_hooks import ScreenHooks
from .window_manager import WindowManager

__all__ = [
    'HookManager',
    'create_hook_manager',
    'StartupHooks',
    'ClientHooks',
    'ScreenHooks',
    'WindowManager'
]
