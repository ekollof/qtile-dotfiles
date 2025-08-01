#!/usr/bin/env python3
"""
Enhanced layout-aware keys module for qtile
Provides consistent key bindings that adapt to the current layout
"""

import os
from libqtile.config import Key
from libqtile.lazy import lazy
from libqtile.log_utils import logger

# Module imports  
from modules.bars import create_bar_manager
from modules.hotkeys import create_hotkey_display
from modules.screens import refresh_screens, get_screen_count


class LayoutAwareKeyManager:
    """Enhanced key manager with layout-aware bindings"""

    def __init__(self, color_manager):
        self.color_manager = color_manager
        self.mod = "mod4"
        self.alt = "mod1"
        self.homedir = os.getenv("HOME")
        self.terminal = "st"
        self.wallpapercmd = str(self.homedir) + "/bin/wallpaper.ksh -r"

    def window_to_previous_screen(self, qtile):
        """Move window to previous screen"""
        i = qtile.screens.index(qtile.current_screen)
        if i != 0:
            group = qtile.screens[i - 1].group.name
            qtile.current_window.togroup(group)

    def window_to_next_screen(self, qtile):
        """Move window to next screen"""
        i = qtile.screens.index(qtile.current_screen)
        if i + 1 != len(qtile.screens):
            group = qtile.screens[i + 1].group.name
            qtile.current_window.togroup(group)

    def manual_color_reload(self, qtile):
        """Manually reload colors"""
        self.color_manager.update_colors()

    def manual_screen_reconfigure(self, qtile):
        """Manually reconfigure screens after monitor changes"""
        logger.info("Manual screen reconfiguration requested")
        refresh_screens()
        new_screen_count = get_screen_count()
        logger.info(f"Detected {new_screen_count} screens")

        # Recreate screens
        bar_manager = create_bar_manager(self.color_manager)
        new_screens = bar_manager.create_screens(new_screen_count)
        qtile.config.screens = new_screens

        # Restart to apply changes
        qtile.restart()

    def show_hotkeys(self, qtile):
        """Show hotkey display window"""
        try:
            logger.info("Showing hotkey display")
            hotkey_display = create_hotkey_display(self, self.color_manager)
            hotkey_display.show_hotkeys()
        except Exception as e:
            logger.error(f"Error showing hotkeys: {e}")
            try:
                hotkey_display = create_hotkey_display(self, self.color_manager)
                hotkey_display.show_hotkeys_simple()
            except Exception as e2:
                logger.error(f"Fallback hotkey display also failed: {e2}")

    def smart_grow(self, qtile):
        """Smart grow that works with different layouts"""
        layout_name = qtile.current_group.layout.name.lower()

        if layout_name in ['monadtall', 'monadwide']:
            # MonadTall/Wide: grow main window
            qtile.current_group.layout.grow()
        elif layout_name in ['tile']:
            # Tile: increase ratio or grow
            qtile.current_group.layout.increase_ratio()
        elif layout_name in ['bsp']:
            # BSP: grow in current direction
            qtile.current_group.layout.grow_right()
        elif layout_name == 'matrix':
            # Matrix: add column
            qtile.current_group.layout.add()
        # Max and Floating layouts: no-op (but don't error)

    def smart_shrink(self, qtile):
        """Smart shrink that works with different layouts"""
        layout_name = qtile.current_group.layout.name.lower()

        if layout_name in ['monadtall', 'monadwide']:
            # MonadTall/Wide: shrink main window
            qtile.current_group.layout.shrink()
        elif layout_name in ['tile']:
            # Tile: decrease ratio or shrink
            qtile.current_group.layout.decrease_ratio()
        elif layout_name in ['bsp']:
            # BSP: shrink in current direction
            qtile.current_group.layout.grow_left()
        elif layout_name == 'matrix':
            # Matrix: remove column if possible
            try:
                qtile.current_group.layout.remove()
            except BaseException:
                pass
        # Max and Floating layouts: no-op

    def smart_normalize(self, qtile):
        """Smart normalize that works with different layouts"""
        if hasattr(qtile.current_group.layout, 'normalize'):
            qtile.current_group.layout.normalize()
        elif hasattr(qtile.current_group.layout, 'reset'):
            qtile.current_group.layout.reset()

    def get_keys(self):
        """Get all keyboard bindings with layout awareness"""
        return [
            # === UNIVERSAL NAVIGATION (works with all layouts) ===
            Key([self.mod], "j", lazy.layout.up(), desc="Move focus up"),
            Key([self.mod], "k", lazy.layout.down(), desc="Move focus down"),
            Key([self.mod], "h", lazy.layout.left(), desc="Move focus left"),
            Key([self.mod], "l", lazy.layout.right(), desc="Move focus right"),

            # === UNIVERSAL WINDOW MOVEMENT ===
            Key([self.mod, "shift"], "j", lazy.layout.shuffle_up(), desc="Move window up"),
            Key([self.mod, "shift"], "k", lazy.layout.shuffle_down(), desc="Move window down"),
            Key([self.mod, "shift"], "h", lazy.layout.shuffle_left(), desc="Move window left"),
            Key([self.mod, "shift"], "l", lazy.layout.shuffle_right(), desc="Move window right"),

            # === SMART RESIZING (layout-aware) ===
            Key([self.mod, "control"], "l", lazy.function(
                self.smart_grow), desc="Smart grow window"),
            Key([self.mod, "control"], "h", lazy.function(
                self.smart_shrink), desc="Smart shrink window"),
            Key([self.mod], "n", lazy.function(self.smart_normalize), desc="Smart normalize layout"),

            # === LAYOUT-SPECIFIC OPERATIONS ===
            # These will only work with compatible layouts
            Key([self.mod], "x", lazy.layout.maximize(),
                desc="Maximize window (compatible layouts)"),
            Key([self.mod, "shift"], "space", lazy.layout.rotate(), desc="Rotate layout (tile/bsp)"),
            Key([self.mod, "shift"], "Return", lazy.layout.toggle_split(), desc="Toggle split (tile)"),

            # === UNIVERSAL LAYOUT NAVIGATION ===
            Key([self.mod], "space", lazy.layout.next(), desc="Switch window focus"),
            Key([self.mod, "shift"], "Tab", lazy.layout.previous(), desc="Switch to previous window"),

            # === SCREEN MANAGEMENT ===
            Key([self.mod], "comma", lazy.prev_screen(), desc="Previous screen"),
            Key([self.mod], "period", lazy.next_screen(), desc="Next screen"),
            Key([self.mod, "shift"], "comma", lazy.function(
                self.window_to_previous_screen), desc="Move window to previous screen"),
            Key([self.mod, "shift"], "period", lazy.function(
                self.window_to_next_screen), desc="Move window to next screen"),

            # === LAYOUT SWITCHING ===
            Key([self.mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
            Key([self.mod], "t", lazy.group.setlayout("tile"), desc="Set tile layout"),
            Key([self.mod], "m", lazy.group.setlayout("max"), desc="Set max layout"),
            Key([self.mod], "b", lazy.group.setlayout("bsp"), desc="Set BSP layout"),
            Key([self.mod, "shift"], "t", lazy.group.setlayout(
                "monadtall"), desc="Set MonadTall layout"),
            Key([self.mod, "shift"], "x", lazy.group.setlayout("matrix"), desc="Set Matrix layout"),

            # === WINDOW MANAGEMENT ===
            Key([self.mod], "q", lazy.window.kill(), desc="Close focused window"),
            Key([self.mod], "f", lazy.window.toggle_floating(), desc="Toggle floating"),
            Key([self.mod, "shift"], "f", lazy.window.toggle_fullscreen(), desc="Toggle fullscreen"),

            # === APPLICATIONS ===
            Key([self.mod], "Return", lazy.spawn(self.terminal), desc="Launch terminal"),
            Key([self.mod], "w", lazy.spawn("brave"), desc="Launch browser"),
            Key([self.mod], "p", lazy.spawn("rofi -show run"), desc="Application launcher"),
            Key([self.mod, "shift"], "p", lazy.spawn(
                str(self.homedir) + "/bin/getpass"), desc="Password manager"),
            Key([self.mod, "shift"], "o", lazy.spawn(
                str(self.homedir) + "/bin/getpass --totp"), desc="TOTP codes"),
            Key([self.mod, "shift"], "c", lazy.spawn("clipmenu"), desc="Clipboard manager"),

            # === SYSTEM COMMANDS ===
            Key([self.mod, "shift"], "r", lazy.restart(), desc="Restart qtile"),
            Key([self.mod, "shift"], "q", lazy.shutdown(), desc="Shutdown qtile"),
            Key([self.mod], "r", lazy.spawncmd(), desc="Run command prompt"),
            Key([self.alt, "control"], "l", lazy.spawn("loginctl lock-session"), desc="Lock session"),

            # === QTILE SPECIFIC ===
            Key([self.mod, "control"], "c", lazy.function(
                self.manual_color_reload), desc="Reload colors"),
            Key([self.mod, "control"], "s", lazy.function(
                self.manual_screen_reconfigure), desc="Reconfigure screens"),
            Key([self.mod], "s", lazy.function(self.show_hotkeys), desc="Show hotkeys"),
            Key([self.mod, "control"], "r", lazy.restart(), desc="Quick restart qtile"),

            # === SCRATCHPADS ===
            Key([self.mod], "grave", lazy.group["scratch"].dropdown_toggle(
                "notepad"), desc="Toggle notepad"),
            Key([self.mod, "shift"], "grave", lazy.group["scratch"].dropdown_toggle(
                "ncmpcpp"), desc="Toggle music player"),

            # === WALLPAPER ===
            Key([self.mod, "control"], "w", lazy.spawn(
                str(self.homedir) + "/bin/pickwall.sh"), desc="Pick wallpaper"),
            Key([self.alt, "control"], "w", lazy.spawn(self.wallpapercmd), desc="Random wallpaper"),
        ]


def create_layout_aware_key_manager(color_manager):
    """Create and return a layout-aware key manager instance"""
    return LayoutAwareKeyManager(color_manager)
