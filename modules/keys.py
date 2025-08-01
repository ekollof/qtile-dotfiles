#!/usr/bin/env python3
"""
Keys and bindings module for qtile
Handles keyboard shortcuts and window management
"""

import os
from libqtile.config import Key
from libqtile.lazy import lazy


class KeyManager:
    """Manages keyboard bindings and shortcuts"""

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
        from modules.screens import refresh_screens, get_screen_count
        from modules.bars import create_bar_manager
        from libqtile.log_utils import logger
        
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
        from modules.hotkeys import create_hotkey_display
        from libqtile.log_utils import logger
        
        try:
            logger.info("Showing hotkey display")
            hotkey_display = create_hotkey_display(self, self.color_manager)
            hotkey_display.show_hotkeys()
        except Exception as e:
            logger.error(f"Error showing hotkeys: {e}")
            # Fallback to simple dmenu
            try:
                hotkey_display = create_hotkey_display(self, self.color_manager)
                hotkey_display.show_hotkeys_simple()
            except Exception as e2:
                logger.error(f"Fallback hotkey display also failed: {e2}")

    def get_keys(self):
        """Get all keyboard bindings"""
        return [
            # Switch between windows in current stack pane
            Key([self.mod], "k", lazy.layout.down(), desc="Move focus down in stack pane"),
            Key([self.mod], "j", lazy.layout.up(), desc="Move focus up in stack pane"),
            Key(
                [self.mod, "shift"],
                "k",
                lazy.layout.shuffle_down(),
                desc="Move windows down in current stack",
            ),
            Key(
                [self.mod, "shift"],
                "j",
                lazy.layout.shuffle_up(),
                desc="windows up in current stack",
            ),
            Key(
                [self.mod, "shift"],
                "l",
                lazy.layout.grow(),
                lazy.layout.increase_ratio(),
                desc="Grow size of current window",
            ),
            Key(
                [self.mod, "shift"],
                "h",
                lazy.layout.shrink(),
                lazy.layout.decrease_ratio(),
                desc="Shrink size of current window",
            ),
            Key([self.mod, "shift"], "comma", lazy.function(self.window_to_previous_screen)),
            Key([self.mod, "shift"], "period", lazy.function(self.window_to_next_screen)),
            Key([self.mod], "comma", lazy.prev_screen()),
            Key([self.mod], "period", lazy.next_screen()),
            # Restore all windows to default size ratios
            Key([self.mod], "n", lazy.layout.normalize()),
            Key([self.mod], "x", lazy.layout.maximize()),
            # Switch window focus to other pane(s) of stack
            Key(
                [self.mod],
                "space",
                lazy.layout.next(),
                desc="Switch window focus to other pane(s) of stack",
            ),
            # Swap panes of split stack
            Key(
                [self.mod, "shift"],
                "space",
                lazy.layout.rotate(),
                desc="Swap panes of split stack",
            ),
            # Toggle between split and unsplit sides of stack.
            # Split = all windows displayed
            # Unsplit = 1 window displayed, like Max layout, but still with
            # multiple stack panes
            Key(
                [self.mod, "shift"],
                "Return",
                lazy.layout.toggle_split(),
                desc="Toggle between split and unsplit sides of stack",
            ),
            Key([self.mod], "Return", lazy.spawn(self.terminal), desc="Launch terminal"),
            # Toggle between different layouts as defined below
            Key([self.mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
            Key([self.mod], "q", lazy.window.kill(), desc="Kill focused window"),
            Key([self.mod, "shift"], "r", lazy.restart(), desc="Restart qtile"),
            Key([self.mod, "shift"], "q", lazy.shutdown(), desc="Shutdown qtile"),
            Key([self.mod], "r", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),
            Key([self.mod], "p", lazy.spawn("rofi -show run")),
            Key([self.mod, "shift"], "p", lazy.spawn(str(self.homedir) + "/bin/getpass")),
            Key([self.mod, "shift"], "o", lazy.spawn(str(self.homedir) + "/bin/getpass --totp")),
            Key([self.mod, "control"], "w", lazy.spawn(str(self.homedir) + "/bin/pickwall.sh")),
            Key([self.mod, "shift"], "c", lazy.spawn("clipmenu")),
            Key([self.alt, "control"], "l", lazy.spawn("loginctl lock-session")),
            Key([self.alt, "control"], "w", lazy.spawn(self.wallpapercmd.format(self.homedir))),
            Key([self.mod], "w", lazy.spawn("brave"), desc="Start browser"),
            Key([self.mod], "f", lazy.window.toggle_floating(), desc="Toggle floating"),
            Key([self.mod], "t", lazy.group.setlayout("tile"), desc="Go to tiling layout"),
            Key([self.mod], "m", lazy.group.setlayout("max"), desc="Go to max layout"),
            Key([self.mod], "grave", lazy.group["scratch"].dropdown_toggle("notepad")),
            Key([self.mod, "shift"], "m", lazy.group["scratch"].dropdown_toggle("ncmpcpp")),
            Key([self.mod, "control"], "c", lazy.function(self.manual_color_reload), desc="Reload colors"),
            Key([self.mod, "control"], "s", lazy.function(self.manual_screen_reconfigure), desc="Reconfigure screens"),
            Key([self.mod], "s", lazy.function(self.show_hotkeys), desc="Show hotkeys"),
            Key([self.mod, "control"], "r", lazy.restart(), desc="Quick restart qtile"),
        ]


def create_key_manager(color_manager):
    """Create and return a key manager instance"""
    return KeyManager(color_manager)
