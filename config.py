#!/usr/bin/env python3
"""
Qtile Configuration - Modular Design
Author: Andrath
Features: Automatic color reloading, Wayland compatibility, multi-screen support
"""

import importlib
import libqtile.notify
import os
import sys
from libqtile import qtile
from libqtile.config import Click, Drag, Key
from libqtile.lazy import lazy
from libqtile.log_utils import logger

# Import our custom modules
from modules.bars import create_bar_manager
from modules.colors import color_manager
from modules.groups import create_group_manager
from modules.hooks import create_hook_manager
from modules.keys import create_key_manager
from modules.screens import get_screen_count, refresh_screens

# System configuration
hostname = os.uname().nodename
homedir = os.getenv("HOME")
terminal = "st"

# Fix QT apps
os.environ["QT_QPA_PLATFORMTHEME"] = "qt5ct"

# Initialize managers
bar_manager = create_bar_manager(color_manager)
key_manager = create_key_manager(color_manager)
group_manager = create_group_manager(color_manager)
hook_manager = create_hook_manager(color_manager)

# Get configuration components
keys = key_manager.get_keys()
keys.extend(group_manager.get_group_keys())

groups, _ = group_manager.get_groups()
layouts = group_manager.get_layouts()
floating_layout = group_manager.get_floating_layout()

# Widget and screen configuration
widget_defaults = bar_manager.get_widget_defaults()
extension_defaults = bar_manager.get_extension_defaults()

# Create screens based on detected count
screen_count = get_screen_count()
screens = bar_manager.create_screens(screen_count)

# Mouse configuration
mod = "mod4"
mouse = [
    Drag(
        [mod],
        "Button1",
        lazy.window.set_position_floating(),
        start=lazy.window.get_position(),
    ),
    Drag(
        [mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()
    ),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

# Additional qtile settings
dgroups_key_binder = None
dgroups_app_rules = []
main = None  # WARNING: this is deprecated and will be removed soon
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens_setting = True

# Java app compatibility
wmname = "LG3D"

# Setup hooks and monitoring
hook_manager.setup_hooks()

# Helper functions for custom functionality


def reload(module: str) -> None:
    """Reload a Python module"""
    if module in sys.modules:
        _ = importlib.reload(sys.modules[module])


def remapkeys():
    """Remap keys if needed"""
    pass


def manually_reconfigure_screens():
    """Manually reconfigure screens after monitor changes"""
    if qtile is not None:
        logger.info("Manual screen reconfiguration requested")
        _ = refresh_screens()
        new_screen_count = get_screen_count()
        logger.info(f"Detected {new_screen_count} screens")

        # Recreate screens
        bar_manager = create_bar_manager(color_manager)
        new_screens = bar_manager.create_screens(new_screen_count)
        qtile.config.screens = new_screens

        # Restart to apply changes
        qtile.restart()

        