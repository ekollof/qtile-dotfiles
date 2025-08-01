#!/usr/bin/env python3
"""
Bars and widgets module for qtile
Handles bar configuration and widget setup
"""

import subprocess
import os
import socket
from typing import final
from libqtile import widget as qtwidget
from libqtile.bar import Bar
from libqtile.lazy import lazy
from libqtile.log_utils import logger
from qtile_extras import widget


@final
class BarManager:
    """Manages qtile bar configuration and widget creation"""

    def __init__(self, color_manager) -> None:
        self.color_manager = color_manager
        self.hostname = socket.gethostname()
        self.homedir = os.getenv("HOME")

        # Widget defaults
        self.widget_defaults = dict(
            font="Monospace",
            fontsize=15,
            padding=3,
            border_with=3,
            border_focus=color_manager.get_colors()["special"]["foreground"],
            border_normal=color_manager.get_colors()["special"]["background"],
            foreground=color_manager.get_colors()["special"]["foreground"],
            background=color_manager.get_colors()["special"]["background"],
        )

        self.extension_defaults = self.widget_defaults.copy()

    def get_widget_defaults(self):
        """Get widget defaults"""
        return self.widget_defaults

    def get_extension_defaults(self):
        """Get extension defaults"""
        return self.extension_defaults

    def create_bar_config(self, screen_num: int):
        """Create bar configuration for a specific screen"""
        colordict = self.color_manager.get_colors()
        logger.info(f"Bar config for screen {screen_num + 1}")

        barconfig = [
            # Option 1: Use emoji (current)
            widget.TextBox(
                text="🐍",
                fontsize=20,
                background=colordict["special"]["background"],
                foreground=colordict["colors"]["color5"],
                mouse_callbacks={"Button1": lazy.spawn("dmenu_run")},
            ),

            widget.GroupBox(
                background=colordict["special"]["background"],
                foreground=colordict["colors"]["color5"],
                active=colordict["colors"]["color7"],
                inactive=colordict["colors"]["color1"],
                border=colordict["colors"]["color1"],
                this_current_screen_border=colordict["colors"]["color6"],
            ),
            widget.Prompt(),
            widget.TaskList(
                border=colordict["colors"]["color1"],
                foreground=colordict["colors"]["color5"],
                background=colordict["special"]["background"],
                theme_mode="preferred",
                theme_path="/usr/share/icons/breeze-dark",
            ),
            widget.Mpd2(
                foreground=colordict["colors"]["color5"],
                background=colordict["special"]["background"],
            ),
            widget.CheckUpdates(
                foreground=colordict["colors"]["color5"],
                background=colordict["special"]["background"],
                update_interval=3600,
                display_format="🔼: {updates}",
                distro="Arch_checkupdates",
                no_update_string="🔼: 0",
            ),
            widget.CheckUpdates(
                foreground=colordict["colors"]["color5"],
                background=colordict["special"]["background"],
                update_interval=3600,
                display_format="🔄: {updates}",
                distro="Arch_yay",
                no_update_string="🔄: 0",
            ),
            widget.TextBox("📭:"),
            widget.GenPollText(
                foreground=colordict["colors"]["color5"],
                background=colordict["special"]["background"],
                update_interval=300,
                func=lambda: str(
                    subprocess.check_output(os.path.expanduser("~/bin/imap-checker.ksh"))
                    .strip()
                    .decode("utf-8")
                ),
            ),
            widget.TextBox("🎫:"),
            widget.GenPollText(
                foreground=colordict["colors"]["color5"],
                background=colordict["special"]["background"],
                update_interval=60,
                func=lambda: str(
                    subprocess.check_output(os.path.expanduser("~/bin/kayako.sh"))
                    .strip()
                    .decode("utf-8")
                ),
            ),
            widget.TextBox("🌡:"),
            widget.GenPollText(
                foreground=colordict["colors"]["color5"],
                background=colordict["special"]["background"],
                update_interval=10,
                func=lambda: str(
                    subprocess.check_output(os.path.expanduser("~/bin/cputemp"))
                    .strip()
                    .decode("utf-8")
                ),
            ),
            widget.Clock(
                foreground=colordict["colors"]["color5"],
                background=colordict["special"]["background"],
                format="%Y-%m-%d %a %H:%M:%S",
            ),
            widget.CurrentLayout(
                foreground=colordict["colors"]["color5"],
                background=colordict["special"]["background"],
            ),
            qtwidget.Systray(
                foreground=colordict["special"]["foreground"],
                background=colordict["colors"]["color2"],
                border=colordict["colors"]["color1"],
            ),
        ]

        # Remove systray from non-primary screens
        if screen_num != 0:
            barconfig = barconfig[:-1]

        return Bar(barconfig, 30, margin=5, opacity=0.8)

    def create_screens(self, screen_count: int):
        """Create screen configurations with bars"""
        from libqtile.config import Screen

        screens = []
        for i in range(screen_count):
            screens.append(
                Screen(top=self.create_bar_config(i))
            )
        return screens


# Import subprocess for widget functions


def create_bar_manager(color_manager):
    """Create and return a bar manager instance"""
    return BarManager(color_manager)
