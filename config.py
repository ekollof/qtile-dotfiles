#!/usr/bin/env python3
"""
Qtile Configuration - Modular Design
Author: Andrath
Features: Automatic color reloading, Wayland compatibility, multi-screen support
"""

import importlib

import os
import sys
from pathlib import Path
from libqtile import qtile
from libqtile.config import Click, Drag
from libqtile.lazy import lazy
from libqtile.log_utils import logger

# Import our custom modules
from modules.bars import create_bar_manager
from modules.colors import color_manager
from modules.groups import create_group_manager
from modules.hooks import create_hook_manager
from modules.keys import create_key_manager
from modules.screens import get_screen_count, refresh_screens
from qtile_config import get_config

# System configuration
hostname = os.uname().nodename
homedir = str(Path.home())
terminal = "st"

# Fix QT apps
os.environ["QT_QPA_PLATFORMTHEME"] = "qt5ct"

# Initialize managers
qtile_config = get_config()
bar_manager = create_bar_manager(color_manager, qtile_config)
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
bring_front_click = "focus_and_warp"
cursor_warp = True
auto_fullscreen = True
focus_on_window_activation = "focus"
reconfigure_screens_setting = True

# Java app compatibility
wmname = "qtile"

# Setup hooks and monitoring
hook_manager.setup_hooks()

# Helper functions for custom functionality


def reload(module: str) -> None:
    """
    @brief Reload a Python module dynamically
    @param module The module name to reload
    """
    if module in sys.modules:
        _ = importlib.reload(sys.modules[module])


def remapkeys():
    """
    @brief Remap keys if needed (placeholder for custom key remapping)
    """
    pass


def manually_reconfigure_screens():
    """
    @brief Manually reconfigure screens after monitor changes
    @throws Exception if screen reconfiguration fails
    """
    if qtile is not None:
        logger.info("Manual screen reconfiguration requested")
        _ = refresh_screens()
        new_screen_count = get_screen_count()
        logger.info(f"Detected {new_screen_count} screens")

        # Recreate screens
        qtile_config = get_config()
        bar_manager = create_bar_manager(color_manager, qtile_config)
        new_screens = bar_manager.create_screens(new_screen_count)
        qtile.config.screens = new_screens

        # Restart to apply changes
        qtile.restart()
