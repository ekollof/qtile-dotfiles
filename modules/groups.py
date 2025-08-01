#!/usr/bin/env python3
"""
Groups and layouts module for qtile
Handles workspace groups and window layouts
"""

from libqtile import layout
from libqtile.config import Group, Key, Match, ScratchPad, DropDown
from libqtile.lazy import lazy


class GroupManager:
    """Manages workspace groups and layouts"""

    def __init__(self, color_manager):
        self.color_manager = color_manager
        self.mod = "mod4"

    def get_layouts(self):
        """Get all available layouts"""
        colordict = self.color_manager.get_colors()

        return [
            layout.Tile(
                margin=4,  # Increased margin for gap between windows
                border_width=1,
                border_focus=colordict["special"]["foreground"],
                border_normal=colordict["special"]["background"],
                ratio=0.5,  # Main window takes 50% of screen
                ratio_increment=0.1,  # How much to change ratio by
                master_match=None,  # No specific master window rules
                expand=True,  # Allow windows to expand to fill space
                master_length=1,  # Number of windows in master pane
                shift_windows=True,  # Allow shifting windows between panes
            ),
            layout.MonadTall(
                margin=4,  # Increased margin for gap between windows
                border_width=1,
                border_focus=colordict["special"]["foreground"],
                border_normal=colordict["special"]["background"],
                ratio=0.6,  # Main window takes 60% of screen width
                min_ratio=0.25,  # Minimum ratio for main window
                max_ratio=0.85,  # Maximum ratio for main window
                change_ratio=0.05,  # How much to change ratio by
                change_size=20,  # How much to change window size by
                new_client_position='after_current',  # Where to place new windows
            ),
            layout.Matrix(
                margin=4,  # Increased margin for gap between windows
                border_width=1,
                border_focus=colordict["special"]["foreground"],
                border_normal=colordict["special"]["background"],
            ),
            layout.Bsp(
                margin=4,  # Increased margin for gap between windows
                border_width=1,
                border_focus=colordict["special"]["foreground"],
                border_normal=colordict["special"]["background"],
                fair=True,  # Distribute space evenly among windows
                grow_amount=10,  # How much to grow/shrink windows by
                lower_right=True,  # Place new windows in lower right
                ratio=1.6,  # Golden ratio for splits
            ),
            layout.Max(),
        ]

    def get_floating_layout(self):
        """Get floating layout configuration"""
        colordict = self.color_manager.get_colors()

        return layout.Floating(
            float_rules=[
                # Specific system dialogs and utilities only
                # NOTE: Removed *layout.Floating.default_float_rules to prevent electron apps from floating
                
                # Core system dialogs (but exclude browser-window role to avoid catching electron apps)
                Match(wm_class="confirm"),
                Match(wm_class="dialog", role="!browser-window"),  # Exclude electron apps with browser-window role
                Match(wm_class="download"),
                Match(wm_class="error"),
                Match(wm_class="file_progress"),
                Match(wm_class="notification"),
                Match(wm_class="splash"),
                Match(wm_class="toolbar"),
                
                # PIN entry (consolidated rules)
                Match(wm_class="pinentry-gtk-2"),
                Match(wm_class="pinentry"),
                Match(title="pinentry"),
                
                # Git tools (gitk)
                Match(wm_class="confirmreset"),
                Match(wm_class="makebranch"),
                Match(wm_class="maketag"),
                Match(title="branchdialog"),
                
                # System authentication
                Match(wm_class="ssh-askpass"),
                
                # Desktop environment
                Match(wm_class="krunner"),  # KDE application launcher
                Match(title="Desktop — Plasma"),  # KDE desktop
                
                # Common utilities (recommended additions)
                Match(wm_class="gnome-calculator"),
                Match(wm_class="kcalc"),
                Match(wm_class="flameshot"),
                Match(wm_class="spectacle"),
                Match(wm_class="org.kde.spectacle"),
                Match(wm_class="Xfce4-screenshooter"),
                
                # Additional specific utilities that should float
                Match(wm_class="Gpick"),  # Color picker
                Match(wm_class="Arandr"),  # Display configuration
                Match(wm_class="Pavucontrol"),  # Audio control
                Match(wm_class="Nm-connection-editor"),  # Network manager
                Match(wm_class="Blueman-manager"),  # Bluetooth manager
                
                # Small system tools
                Match(wm_class="Galculator"),
                Match(wm_class="Gnome-calculator"),
                
                # Note: Electron apps (VSCode, Discord, Slack, etc.) will now tile by default
                # VSCode Insiders: WM_CLASS="code - insiders", "Code - Insiders" with role="browser-window"
                # This will NOT match any of the above rules and will tile properly
            ],
            border_focus=colordict["special"]["foreground"],
            border_normal=colordict["special"]["background"],
            border_width=1,  # Consistent border width with tiling layouts
        )

    def get_groups(self):
        """Get all workspace groups"""
        group_names = [
            ("1:chat", {"layout": "max"}),
            ("2:web", {"layout": "tile"}),
            ("3:shell", {"layout": "tile"}),
            ("4:work", {"layout": "tile"}),
            ("5:games", {"layout": "tile"}),
            ("6:dev", {"layout": "tile"}),
            ("7:mail", {"layout": "tile"}),
            ("8:misc", {"layout": "tile"}),
            ("9:doc", {"layout": "tile"}),
        ]

        groups = []
        for name, kwargs in group_names:
            groups.append(Group(name))

        # Add scratchpad
        dropdowns = [
            DropDown(
                "notepad",
                "st -e nvim /tmp/notepad.md",
                width=0.6,
                height=0.6,
                x=0.2,
                y=0.2,
                opacity=0.9,
            ),
            DropDown(
                "ncmpcpp",
                "st -e ncmpcpp",
                width=0.8,
                height=0.8,
                x=0.1,
                y=0.1,
                opacity=0.9,
            ),
        ]
        groups.append(ScratchPad("scratch", dropdowns))

        return groups, group_names

    def get_group_keys(self):
        """Get group-related keyboard bindings"""
        groups, group_names = self.get_groups()
        keys = []

        for i, (name, kwargs) in enumerate(group_names, 1):
            # Switch to another group
            keys.append(Key([self.mod], str(i), lazy.group[name].toscreen()))
            # Send current window to another group
            keys.append(Key([self.mod, "shift"], str(i), lazy.window.togroup(name)))

        return keys


def create_group_manager(color_manager):
    """Create and return a group manager instance"""
    return GroupManager(color_manager)
