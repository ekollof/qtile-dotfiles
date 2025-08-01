#!/usr/bin/env python3
"""
Key bindings module for qtile
Handles keyboard shortcuts and window management
"""

import os
from libqtile.config import Key
from libqtile.lazy import lazy
from libqtile.log_utils import logger
from qtile_config import get_config


class KeyManager:
    """Manages keyboard bindings and shortcuts"""

    def __init__(self, color_manager):
        self.color_manager = color_manager
        self.config = get_config()
        self.mod = self.config.mod_key
        self.alt = self.config.alt_key
        self.homedir = os.getenv("HOME")
        self.terminal = self.config.terminal
        self.apps = self.config.applications

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

    def manual_retile_all(self, qtile):
        """Manually force all windows to tile"""
        try:
            from modules.hooks import create_hook_manager
            hook_manager = create_hook_manager(self.color_manager)
            count = hook_manager.force_retile_all_windows(qtile)
            logger.info(f"Manual retile completed - {count} windows retiled")
        except Exception as e:
            logger.error(f"Manual retile failed: {e}")

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

    def smart_grow(self, qtile):
        """Smart grow that adapts to current layout"""
        layout_name = qtile.current_group.layout.name.lower()
        
        try:
            if layout_name in ['monadtall', 'monadwide']:
                # MonadTall/Wide: grow main window
                qtile.current_group.layout.grow()
            elif layout_name in ['tile']:
                # Tile: increase ratio
                qtile.current_group.layout.increase_ratio()
            elif layout_name in ['bsp']:
                # BSP: grow window
                qtile.current_group.layout.grow_right()
            elif layout_name == 'matrix':
                # Matrix: add column (horizontal growth)
                qtile.current_group.layout.add()
            # Max and Floating layouts: no-op (but don't error)
        except Exception as e:
            # Fallback for layouts that don't support the operation
            logger.debug(f"Smart grow not supported in {layout_name}: {e}")

    def smart_shrink(self, qtile):
        """Smart shrink that adapts to current layout"""
        layout_name = qtile.current_group.layout.name.lower()
        
        try:
            if layout_name in ['monadtall', 'monadwide']:
                # MonadTall/Wide: shrink main window
                qtile.current_group.layout.shrink()
            elif layout_name in ['tile']:
                # Tile: decrease ratio
                qtile.current_group.layout.decrease_ratio()
            elif layout_name in ['bsp']:
                # BSP: shrink window
                qtile.current_group.layout.grow_left()
            elif layout_name == 'matrix':
                # Matrix: remove column (horizontal shrink)
                qtile.current_group.layout.delete()
            # Max and Floating layouts: no-op
        except Exception as e:
            # Fallback for layouts that don't support the operation
            logger.debug(f"Smart shrink not supported in {layout_name}: {e}")

    def smart_grow_vertical(self, qtile):
        """Smart vertical grow that adapts to current layout"""
        layout_name = qtile.current_group.layout.name.lower()
        
        try:
            if layout_name in ['monadtall', 'monadwide']:
                # MonadTall/Wide: grow main window
                qtile.current_group.layout.grow()
            elif layout_name in ['tile']:
                # Tile: no vertical resize in tile layout
                pass
            elif layout_name in ['bsp']:
                # BSP: grow window up
                qtile.current_group.layout.grow_up()
            elif layout_name == 'matrix':
                # Matrix: no vertical resize (columns only)
                pass
            # Max and Floating layouts: no-op
        except Exception as e:
            logger.debug(f"Smart vertical grow not supported in {layout_name}: {e}")

    def smart_shrink_vertical(self, qtile):
        """Smart vertical shrink that adapts to current layout"""
        layout_name = qtile.current_group.layout.name.lower()
        
        try:
            if layout_name in ['monadtall', 'monadwide']:
                # MonadTall/Wide: shrink main window
                qtile.current_group.layout.shrink()
            elif layout_name in ['tile']:
                # Tile: no vertical resize in tile layout
                pass
            elif layout_name in ['bsp']:
                # BSP: grow window down (shrink upward space)
                qtile.current_group.layout.grow_down()
            elif layout_name == 'matrix':
                # Matrix: no vertical resize (columns only)
                pass
            # Max and Floating layouts: no-op
        except Exception as e:
            logger.debug(f"Smart vertical shrink not supported in {layout_name}: {e}")

    def smart_normalize(self, qtile):
        """Smart normalize that works with different layouts"""
        layout_name = qtile.current_group.layout.name.lower()
        
        try:
            if layout_name in ['monadtall', 'monadwide', 'monadthreecol']:
                # Monad layouts: normalize secondary windows
                qtile.current_group.layout.normalize()
            elif layout_name in ['tile']:
                # Tile: reset to default ratios
                qtile.current_group.layout.reset()
            elif layout_name in ['bsp']:
                # BSP: normalize window sizes
                qtile.current_group.layout.normalize()
            elif layout_name in ['columns']:
                # Columns: normalize column widths and reset ratios
                qtile.current_group.layout.normalize()
            elif layout_name in ['spiral']:
                # Spiral: reset ratios to config values
                qtile.current_group.layout.reset()
            elif layout_name in ['verticaltile']:
                # VerticalTile: normalize window sizes
                qtile.current_group.layout.normalize()
            elif layout_name in ['plasma']:
                # Plasma: reset current window size to automatic
                qtile.current_group.layout.reset_size()
            elif layout_name == 'matrix':
                # Matrix: no normalize function, but we can do nothing gracefully
                pass
            elif layout_name in ['max', 'floating']:
                # Max/Floating: no normalize needed
                pass
            elif hasattr(qtile.current_group.layout, 'normalize'):
                # Generic normalize fallback
                qtile.current_group.layout.normalize()
            elif hasattr(qtile.current_group.layout, 'reset'):
                # Generic reset fallback
                qtile.current_group.layout.reset()
        except Exception as e:
            logger.debug(f"Normalize not supported in {layout_name}: {e}")

    def layout_safe_command(self, qtile, command_name, *args, **kwargs):
        """Execute a layout command only if the layout supports it"""
        try:
            layout = qtile.current_group.layout
            if hasattr(layout, command_name):
                command = getattr(layout, command_name)
                if callable(command):
                    return command(*args, **kwargs)
        except Exception as e:
            logger.debug(f"Layout command {command_name} failed: {e}")

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
            Key([self.mod], "h", lazy.layout.left(), desc="Move focus left in stack pane"),
            Key([self.mod], "l", lazy.layout.right(), desc="Move focus right in stack pane"),
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
            Key(
                [self.mod, "control"],
                "l",
                lazy.function(self.smart_grow),
                desc="Smart grow window horizontally (adapts to layout)",
            ),
            Key(
                [self.mod, "control"],
                "h",
                lazy.function(self.smart_shrink),
                desc="Smart shrink window horizontally (adapts to layout)",
            ),
            Key(
                [self.mod, "control"],
                "k",
                lazy.function(self.smart_grow_vertical),
                desc="Smart grow window vertically (adapts to layout)",
            ),
            Key(
                [self.mod, "control"],
                "j",
                lazy.function(self.smart_shrink_vertical),
                desc="Smart shrink window vertically (adapts to layout)",
            ),
            Key([self.mod, "shift"], "comma", lazy.function(self.window_to_previous_screen)),
            Key([self.mod, "shift"], "period", lazy.function(self.window_to_next_screen)),
            Key([self.mod], "comma", lazy.prev_screen()),
            Key([self.mod], "period", lazy.next_screen()),
            # Restore all windows to default size ratios
            Key([self.mod], "n", lazy.function(self.smart_normalize), desc="Smart normalize layout"),
            Key([self.mod], "x", lazy.layout.maximize(), desc="Maximize window (if supported)"),
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
            Key([self.mod], "p", lazy.spawn(self.apps['launcher']), desc="Launch application launcher"),
            Key([self.mod, "shift"], "p", lazy.spawn(self.apps['password_manager']), desc="Launch password manager"),
            Key([self.mod, "shift"], "o", lazy.spawn(self.apps['totp_manager']), desc="Launch TOTP manager"),
            Key([self.mod, "control"], "w", lazy.spawn(self.apps['wallpaper_picker']), desc="Pick wallpaper"),
            Key([self.mod, "shift"], "c", lazy.spawn(self.apps['clipboard']), desc="Launch clipboard manager"),
            Key([self.alt, "control"], "l", lazy.spawn(self.apps['lock_session']), desc="Lock session"),
            Key([self.alt, "control"], "w", lazy.spawn(self.apps['wallpaper_random']), desc="Set random wallpaper"),
            Key([self.mod], "w", lazy.spawn(self.config.browser), desc="Start browser"),
            Key([self.mod], "f", lazy.window.toggle_floating(), desc="Toggle floating"),
            Key([self.mod, "shift"], "f", lazy.window.toggle_fullscreen(), desc="Toggle fullscreen"),
            Key([self.mod], "t", lazy.group.setlayout("tile"), desc="Go to tiling layout"),
            Key([self.mod], "m", lazy.group.setlayout("max"), desc="Go to max layout"),
            Key([self.mod], "b", lazy.group.setlayout("bsp"), desc="Go to BSP layout"),
            Key([self.mod, "control"], "t", lazy.group.setlayout("monadtall"), desc="Go to MonadTall layout"),
            Key([self.mod, "control"], "m", lazy.group.setlayout("matrix"), desc="Go to Matrix layout"),
            Key([self.mod], "grave", lazy.group["scratch"].dropdown_toggle("notepad")),
            Key([self.mod, "shift"], "m", lazy.group["scratch"].dropdown_toggle("ncmpcpp")),
            Key([self.mod, "control"], "c", lazy.function(self.manual_color_reload), desc="Reload colors"),
            Key([self.mod, "control"], "s", lazy.function(self.manual_screen_reconfigure), desc="Reconfigure screens"),
            Key([self.mod, "control"], "f", lazy.function(self.manual_retile_all), desc="Force retile all windows"),
            Key([self.mod], "s", lazy.function(self.show_hotkeys), desc="Show hotkeys"),
            Key([self.mod, "control"], "r", lazy.restart(), desc="Quick restart qtile"),
        ]


def create_key_manager(color_manager):
    """Create and return a key manager instance"""
    return KeyManager(color_manager)
