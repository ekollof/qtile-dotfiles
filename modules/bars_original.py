#!/usr/bin/env python3
"""
Bars and widgets module for qtile
Handles bar configuration and widget setup
"""

import os
import socket
import subprocess
from pathlib import Path
from typing import final, TYPE_CHECKING, Callable

from libqtile.bar import Bar
from libqtile.config import Screen
from libqtile.lazy import lazy
from libqtile.log_utils import logger
from qtile_extras import widget

if TYPE_CHECKING:
    from modules.colors import ColorManager


@final
class BarManager:
    """Manages qtile bar configuration and widget creation"""

    def __init__(self, color_manager: "ColorManager", qtile_config) -> None:
        self.color_manager = color_manager
        self.qtile_config = qtile_config
        self.hostname = socket.gethostname()
        self.homedir = str(Path.home())

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

    def _has_battery(self) -> bool:
        """Check if the system has a battery (cross-platform)"""
        import platform

        try:
            system = platform.system().lower()

            if system == "linux":
                return self._check_linux_battery()
            elif system in ["openbsd", "freebsd", "netbsd", "dragonfly"]:
                return self._check_bsd_battery()
            elif system == "darwin":
                return self._check_macos_battery()
            else:
                logger.debug(f"Unknown system {system}, skipping battery widget")
                return False

        except Exception as e:
            logger.debug(f"Error detecting battery: {e}")
            return False

    def _check_linux_battery(self) -> bool:
        """Check for battery on Linux systems"""
        battery_paths = [
            "/sys/class/power_supply/BAT0",
            "/sys/class/power_supply/BAT1",
            "/sys/class/power_supply/battery"
        ]

        for path in battery_paths:
            if Path(path).exists():
                type_file = Path(path) / "type"
                if type_file.exists():
                    with open(type_file, 'r') as f:
                        if f.read().strip().lower() == "battery":
                            return True
        return False

    def _check_bsd_battery(self) -> bool:
        """Check for battery on BSD systems"""
        import subprocess
        try:
            # Try apm first (common on OpenBSD)
            result = subprocess.run(['apm'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0 and 'battery' in result.stdout.lower():
                return True
            # Try acpiconf (FreeBSD)
            result = subprocess.run(['acpiconf', '-i', '0'], capture_output=True, text=True, timeout=2)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _check_macos_battery(self) -> bool:
        """Check for battery on macOS"""
        import subprocess
        try:
            result = subprocess.run(['pmset', '-g', 'batt'], capture_output=True, text=True, timeout=2)
            return result.returncode == 0 and 'InternalBattery' in result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _has_mpd_support(self) -> bool:
        """Check if MPD Python module is available"""
        try:
            import mpd
            # Use the module to ensure it's properly loaded
            _ = mpd.MPDClient
            logger.debug("MPD module available")
            return True
        except ImportError:
            logger.debug("MPD module not available, skipping Mpd2 widget")
            return False

    def _has_battery_widget_support(self) -> bool:
        """Check if qtile's battery widget supports current platform"""
        import platform
        try:
            # Check if we have a battery AND the platform is supported
            if not self._has_battery():
                return False

            system = platform.system().lower()
            # qtile's battery widget has known platform issues on some BSD systems
            if system == "openbsd":
                # Test if the battery widget can actually initialize
                try:
                    widget.Battery()
                    return True
                except Exception as e:
                    logger.debug(f"Battery widget not supported on {system}: {e}")
                    return False

            return True
        except Exception as e:
            logger.debug(f"Error checking battery widget support: {e}")
            return False

    def _script_exists(self, script_path: str) -> bool:
        """Check if a script exists and is executable"""
        expanded_path = Path(script_path).expanduser()
        return expanded_path.is_file() and os.access(expanded_path, os.X_OK)

    def _safe_script_call(self, script_path: str, fallback_text: str = "N/A") -> Callable[[], str]:
        """Create a safe wrapper for script calls that handles missing scripts gracefully"""
        expanded_path = Path(script_path).expanduser()

        def wrapper():
            try:
                if not expanded_path.is_file():
                    return fallback_text

                result = subprocess.run(
                    str(expanded_path),
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=True
                )
                return result.stdout.strip()
            except subprocess.TimeoutExpired:
                logger.debug(f"Script {script_path} timed out")
                return "timeout"
            except subprocess.CalledProcessError as e:
                logger.debug(f"Script {script_path} failed with exit code {e.returncode}")
                return "error"
            except FileNotFoundError:
                logger.debug(f"Script {script_path} not found")
                return fallback_text
            except Exception as e:
                logger.debug(f"Error running script {script_path}: {e}")
                return "error"

        return wrapper

    def _get_script_widgets(self, colordict: dict) -> list:
        """Create GenPollText widgets for available scripts using configuration-driven approach"""

        # Generate widgets for available scripts from qtile configuration
        widgets = []
        for config in self.qtile_config.script_configs:
            if self._script_exists(config['script_path']):
                widgets.extend([
                    widget.TextBox(config['icon']),
                    widget.GenPollText(
                        foreground=colordict["colors"]["color5"],
                        background=colordict["special"]["background"],
                        update_interval=config['update_interval'],
                        func=self._safe_script_call(config['script_path'], config['fallback']),
                    ),
                ])
                logger.debug(f"Added {config['name']} widget")
            else:
                logger.debug(f"{config['name']} script not found: {config['script_path']}")

        return widgets

    def create_bar_config(self, screen_num: int) -> Bar:
        """Create bar configuration for a specific screen"""
        colordict = self.color_manager.get_colors()
        logger.info(f"Bar config for screen {screen_num + 1}")

        # Start with core widgets that are always available
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
                # Show only active groups (groups with windows) and current group
                hide_unused=True,
                # Optional: Customize what constitutes "unused"
                # visible_groups=None,  # Use default behavior
            ),
            widget.Prompt(),
            widget.TaskList(
                border=colordict["colors"]["color1"],
                foreground=colordict["special"]["foreground"],
                background=colordict["special"]["background"],
                theme_mode="preferred",
                theme_path="/usr/share/icons/breeze-dark",
            ),
        ]

        # Conditionally add MPD2 widget if mpd module is available
        if self._has_mpd_support():
            barconfig.append(widget.Mpd2(
                foreground=colordict["colors"]["color5"],
                background=colordict["special"]["background"],
            ))
        else:
            logger.debug("Skipping Mpd2 widget - mpd module not available")

        # Continue with update checking widgets
        barconfig.extend([
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
        ])

        # Add script-based widgets (only if scripts are available)
        script_widgets = self._get_script_widgets(colordict)
        barconfig.extend(script_widgets)

        # Conditionally add Battery widget if supported on this platform
        if self._has_battery_widget_support():
            barconfig.extend([
                widget.TextBox("🔋:"),
                widget.Battery(
                    foreground=colordict["colors"]["color5"],
                    background=colordict["special"]["background"],
                    charge_char="⚡",
                    discharge_char="🔋",
                    empty_char="🪫",
                    full_char="🔋",
                    format="{char} {percent:2.0%} {hour:d}:{min:02d}",
                    low_foreground=colordict["colors"]["color1"],  # Red color for low battery
                    low_percentage=0.15,  # 15% threshold for low battery warning
                    update_interval=60,
                ),
            ])
        else:
            logger.debug("Skipping Battery widget - not supported on this platform or no battery detected")

        # Add remaining core widgets
        barconfig.extend([
            widget.Clock(
                foreground=colordict["colors"]["color5"],
                background=colordict["special"]["background"],
                format="%Y-%m-%d %a %H:%M:%S",
            ),
            widget.CurrentLayout(
                foreground=colordict["colors"]["color5"],
                background=colordict["special"]["background"],
            ),
            widget.Systray(
                foreground=colordict["colors"]["color5"],
                background=colordict["special"]["background"],
                border=colordict["colors"]["color1"],
            ),
        ])

        # Remove systray from non-primary screens
        if screen_num != 0:
            barconfig = barconfig[:-1]

        return Bar(barconfig, 30, margin=5, opacity=0.8)

    def create_screens(self, screen_count: int):
        """Create screen configurations with bars"""
        screens = []
        for i in range(screen_count):
            screens.append(
                Screen(top=self.create_bar_config(i))
            )
        return screens


# Import subprocess for widget functions


def create_bar_manager(color_manager: "ColorManager", qtile_config) -> BarManager:
    """Create and return a bar manager instance"""
    return BarManager(color_manager, qtile_config)
