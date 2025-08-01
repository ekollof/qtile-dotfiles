#!/usr/bin/env python3
"""
Minimal Qtile Configuration for Debugging
"""

import os
from libqtile.config import Key, Screen, Group, Drag, Click
from libqtile.lazy import lazy
from libqtile import layout, bar, widget

# Basic settings
mod = "mod4"
terminal = "st"

# Simple key bindings
keys = [
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    Key([mod], "q", lazy.window.kill(), desc="Kill focused window"),
    Key([mod, "control"], "r", lazy.restart(), desc="Restart Qtile"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
]

# Simple groups
groups = [Group(i) for i in "12345"]

for i in groups:
    keys.extend([
        Key([mod], i.name, lazy.group[i.name].toscreen()),
        Key([mod, "shift"], i.name, lazy.window.togroup(i.name, switch_group=True)),
    ])

# Simple layouts
layouts = [
    layout.Max(),
    layout.Columns(border_width=2),
]

# Widget defaults
widget_defaults = dict(
    font="sans",
    fontsize=12,
    padding=3,
)
extension_defaults = widget_defaults.copy()

# Simple screens
screens = [
    Screen(
        top=bar.Bar(
            [
                widget.GroupBox(),
                widget.WindowName(),
                widget.Clock(format="%Y-%m-%d %H:%M"),
            ],
            24,
        ),
    ),
]

# Mouse configuration
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

# Basic settings
dgroups_key_binder = None
dgroups_app_rules = []
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating()
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True
wmname = "LG3D"

print("[MINIMAL] Minimal config loaded successfully")
