#!/usr/bin/env python3
"""
Key binding definitions for qtile
"""

from libqtile.config import Key
from libqtile.lazy import lazy


class KeyBindings:
    """Defines all keyboard bindings for qtile"""

    def __init__(self, config, layout_commands, window_commands, system_commands):
        self.config = config
        self.layout_commands = layout_commands
        self.window_commands = window_commands
        self.system_commands = system_commands

        # Shortcuts for common modifiers
        self.mod = config.mod_key
        self.alt = config.alt_key
        self.terminal = config.terminal
        self.apps = config.applications

    def get_movement_keys(self):
        """Get window movement and focus keys"""
        return [
            # Switch between windows in current stack pane (with mouse warp)
            Key(
                [self.mod],
                "k",
                lazy.function(self.window_commands.focus_down_with_warp),
                desc="Move focus down and warp mouse",
            ),
            Key(
                [self.mod],
                "j",
                lazy.function(self.window_commands.focus_up_with_warp),
                desc="Move focus up and warp mouse",
            ),
            Key(
                [self.mod],
                "h",
                lazy.function(self.window_commands.focus_left_with_warp),
                desc="Move focus left and warp mouse",
            ),
            Key(
                [self.mod],
                "l",
                lazy.function(self.window_commands.focus_right_with_warp),
                desc="Move focus right and warp mouse",
            ),
            # Move windows around
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
                desc="Move windows up in current stack",
            ),
            Key(
                [self.mod, "shift"],
                "h",
                lazy.layout.shuffle_left(),
                desc="Move windows left in current stack",
            ),
            Key(
                [self.mod, "shift"],
                "l",
                lazy.layout.shuffle_right(),
                desc="Move windows right in current stack",
            ),
        ]

    def get_layout_keys(self):
        """Get layout manipulation keys"""
        return [
            # Smart layout-aware commands
            Key(
                [self.mod, "control"],
                "l",
                lazy.function(self.layout_commands.smart_grow),
                desc="Smart grow window horizontally (adapts to layout)",
            ),
            Key(
                [self.mod, "control"],
                "h",
                lazy.function(self.layout_commands.smart_shrink),
                desc="Smart shrink window horizontally (adapts to layout)",
            ),
            Key(
                [self.mod, "control"],
                "k",
                lazy.function(self.layout_commands.smart_grow_vertical),
                desc="Smart grow window vertically (adapts to layout)",
            ),
            Key(
                [self.mod, "control"],
                "j",
                lazy.function(self.layout_commands.smart_shrink_vertical),
                desc="Smart shrink window vertically (adapts to layout)",
            ),
            # Layout controls
            Key(
                [self.mod],
                "n",
                lazy.function(self.layout_commands.smart_normalize),
                desc="Smart normalize layout",
            ),
            Key(
                [self.mod],
                "x",
                lazy.function(self.window_commands.smart_maximize),
                desc="Smart maximize (hide other windows)",
            ),
            # Layout switching
            Key(
                [self.mod],
                "Tab",
                lazy.next_layout(),
                desc="Toggle between layouts",
            ),
            Key(
                [self.mod],
                "t",
                lazy.group.setlayout("tile"),
                desc="Go to tiling layout",
            ),
            Key(
                [self.mod],
                "m",
                lazy.group.setlayout("max"),
                desc="Go to max layout",
            ),
            Key(
                [self.mod],
                "b",
                lazy.group.setlayout("bsp"),
                desc="Go to BSP layout",
            ),
            Key(
                [self.mod, "control"],
                "t",
                lazy.group.setlayout("monadtall"),
                desc="Go to MonadTall layout",
            ),
            Key(
                [self.mod, "control"],
                "m",
                lazy.group.setlayout("matrix"),
                desc="Go to Matrix layout",
            ),
        ]

    def get_window_keys(self):
        """Get window management keys"""
        return [
            # Screen and window movement
            Key(
                [self.mod, "shift"],
                "comma",
                lazy.function(self.window_commands.window_to_previous_screen),
            ),
            Key(
                [self.mod, "shift"],
                "period",
                lazy.function(self.window_commands.window_to_next_screen),
            ),
            Key(
                [self.mod],
                "comma",
                lazy.function(self.window_commands.focus_next_screen_with_warp),
                desc="Focus next screen and warp mouse",
            ),
            Key(
                [self.mod],
                "period",
                lazy.function(self.window_commands.focus_prev_screen_with_warp),
                desc="Focus previous screen and warp mouse",
            ),
            # Window state toggles
            Key(
                [self.mod],
                "f",
                lazy.window.toggle_floating(),
                desc="Toggle floating",
            ),
            Key(
                [self.mod, "shift"],
                "f",
                lazy.window.toggle_fullscreen(),
                desc="Toggle fullscreen",
            ),
            Key([self.mod], "q", lazy.window.kill(), desc="Kill focused window"),
            # Window focus and arrangement
            Key(
                [self.mod],
                "space",
                lazy.layout.next(),
                desc="Switch window focus to other pane(s) of stack",
            ),
            Key(
                [self.mod, "shift"],
                "space",
                lazy.layout.rotate(),
                desc="Swap panes of split stack",
            ),
            Key(
                [self.mod, "shift"],
                "Return",
                lazy.layout.toggle_split(),
                desc="Toggle between split and unsplit sides of stack",
            ),
        ]

    def get_application_keys(self):
        """Get application launcher keys"""
        return [
            # Terminal and basic apps
            Key(
                [self.mod],
                "Return",
                lazy.spawn(self.terminal),
                desc="Launch terminal",
            ),
            Key(
                [self.mod],
                "w",
                lazy.spawn(self.config.browser),
                desc="Start browser",
            ),
            Key(
                [self.mod],
                "r",
                lazy.spawncmd(),
                desc="Spawn a command using a prompt widget",
            ),
            # Application launchers
            Key(
                [self.mod],
                "p",
                lazy.spawn(self.apps["launcher"]),
                desc="Launch application launcher",
            ),
            Key(
                [self.mod, "shift"],
                "p",
                lazy.spawn(self.apps["password_manager"]),
                desc="Launch password manager",
            ),
            Key(
                [self.mod, "shift"],
                "o",
                lazy.spawn(self.apps["totp_manager"]),
                desc="Launch TOTP manager",
            ),
            Key(
                [self.mod, "shift"],
                "c",
                lazy.spawn(self.apps["clipboard"]),
                desc="Launch clipboard manager",
            ),
            # Utility applications
            Key(
                [self.mod, "control"],
                "w",
                lazy.spawn(self.apps["wallpaper_picker"]),
                desc="Pick wallpaper",
            ),
            Key(
                [self.alt, "control"],
                "l",
                lazy.spawn(self.apps["lock_session"]),
                desc="Lock session",
            ),
            Key(
                [self.alt, "control"],
                "w",
                lazy.spawn(self.apps["wallpaper_random"]),
                desc="Set random wallpaper",
            ),
        ]

    def get_system_keys(self):
        """Get system control keys"""
        return [
            # Qtile system controls
            Key([self.mod, "shift"], "r", lazy.restart(), desc="Restart qtile"),
            Key(
                [self.mod, "shift"],
                "q",
                lazy.shutdown(),
                desc="Shutdown qtile",
            ),
            Key(
                [self.mod, "control"],
                "r",
                lazy.restart(),
                desc="Quick restart qtile",
            ),
            # Manual system operations
            Key(
                [self.mod, "control"],
                "c",
                lazy.function(self.system_commands.manual_color_reload),
                desc="Reload colors",
            ),
            Key(
                [self.mod, "control"],
                "s",
                lazy.function(self.system_commands.manual_screen_reconfigure),
                desc="Reconfigure screens",
            ),
            Key(
                [self.mod, "control"],
                "f",
                lazy.function(self.system_commands.manual_retile_all),
                desc="Force retile all windows",
            ),
        ]

    def get_special_keys(self):
        """Get special function keys"""

        def show_hotkeys_wrapper(qtile):
            # We need to pass the key manager to show_hotkeys
            # This will be set by the manager when it creates the bindings
            return self.system_commands.show_hotkeys(qtile, self.key_manager)

        return [
            # Hotkey display
            Key(
                [self.mod],
                "s",
                lazy.function(show_hotkeys_wrapper),
                desc="Show hotkeys",
            ),
            # Scratchpads
            Key(
                [self.mod],
                "grave",
                lazy.group["scratch"].dropdown_toggle("notepad"),
            ),
            Key(
                [self.mod, "shift"],
                "m",
                lazy.group["scratch"].dropdown_toggle("ncmpcpp"),
            ),
        ]

    def get_all_keys(self, key_manager=None):
        """Get all keyboard bindings"""
        # Store reference to key manager for hotkey display
        self.key_manager = key_manager

        all_keys = []
        all_keys.extend(self.get_movement_keys())
        all_keys.extend(self.get_layout_keys())
        all_keys.extend(self.get_window_keys())
        all_keys.extend(self.get_application_keys())
        all_keys.extend(self.get_system_keys())
        all_keys.extend(self.get_special_keys())
        # Note: Function keys (XF86) removed - qtile doesn't support XF86 keysyms

        return all_keys

    def get_keys_by_category(self, key_manager=None):
        """Get keys organized by category"""
        self.key_manager = key_manager

        return {
            "Movement": self.get_movement_keys(),
            "Layout": self.get_layout_keys(),
            "Window": self.get_window_keys(),
            "Applications": self.get_application_keys(),
            "System": self.get_system_keys(),
            "Special": self.get_special_keys(),
        }

    def get_key_count_by_category(self):
        """Get count of keys in each category"""
        categories = self.get_keys_by_category()
        return {category: len(keys) for category, keys in categories.items()}
