#!/usr/bin/env python3
"""
Bars and widgets module for qtile - BITMAP ICONS VERSION
Handles bar configuration and widget setup using bitmap icons instead of emoticons

This is a modified version that replaces emoticons with bitmap icons.
You can choose between different icon approaches:
1. Image widgets (PNG files)
2. Nerd Font icons (if you have a Nerd Font installed)
3. Simple text symbols

Usage: Replace your current bars.py with this file or copy the relevant parts.
"""

import os
import socket
import subprocess
from pathlib import Path
from typing import final, TYPE_CHECKING, Callable

from libqtile.bar import Bar
from libqtile.config import Screen

from libqtile.log_utils import logger
from qtile_extras import widget

if TYPE_CHECKING:
    from modules.colors import ColorManager


@final
class BarManager:
    """Manages qtile bar configuration and widget creation with bitmap icons"""

    def __init__(self, color_manager: "ColorManager", qtile_config) -> None:
        self.color_manager = color_manager
        self.qtile_config = qtile_config
        self.hostname = socket.gethostname()
        self.homedir = str(Path.home())

        # Icon configuration - choose your preferred method
        self.icon_method = "svg"  # Options: "svg", "image", "nerd_font", "text"
        self.icon_dir = Path(self.homedir) / ".config" / "qtile" / "icons"

        # Widget defaults
        self.widget_defaults = dict(
            font="Monospace",
            fontsize=16,
            padding=3,
            border_with=3,
            border_focus=color_manager.get_colors()["special"]["foreground"],
            border_normal=color_manager.get_colors()["special"]["background"],
            foreground=color_manager.get_colors()["special"]["foreground"],
            background=color_manager.get_colors()["special"]["background"],
        )

        self.extension_defaults = self.widget_defaults.copy()

        # Icon mappings for different methods
        self.icons = {
            "svg": {
                "python": str(self.icon_dir / "python.svg"),
                "updates": str(self.icon_dir / "arrow-up.svg"),
                "refresh": str(self.icon_dir / "refresh.svg"),
                "mail": str(self.icon_dir / "mail.svg"),
                "ticket": str(self.icon_dir / "ticket.svg"),
                "thermometer": str(self.icon_dir / "thermometer.svg"),
                "battery": str(self.icon_dir / "battery.svg"),
                "zap": str(self.icon_dir / "zap.svg"),
                "battery_low": str(self.icon_dir / "battery-low.svg"),
            },
            "image": {
                "python": str(self.icon_dir / "python.png"),
                "updates": str(self.icon_dir / "arrow-up.png"),
                "refresh": str(self.icon_dir / "refresh.png"),
                "mail": str(self.icon_dir / "mail.png"),
                "ticket": str(self.icon_dir / "ticket.png"),
                "thermometer": str(self.icon_dir / "thermometer.png"),
                "battery": str(self.icon_dir / "battery.png"),
                "zap": str(self.icon_dir / "zap.png"),
                "battery_low": str(self.icon_dir / "battery-low.png"),
            },
            "nerd_font": {
                "python": "\ue73c",  # Python icon from Nerd Fonts
                "updates": "\uf0aa",  # Arrow up
                "refresh": "\uf2f1",  # Refresh
                "mail": "\uf0e0",     # Mail
                "ticket": "\uf3ff",   # Ticket
                "thermometer": "\uf2c9",  # Thermometer
                "battery": "\uf240",  # Battery
                "zap": "\uf0e7",      # Lightning
                "battery_low": "\uf244",  # Battery low
            },
            "text": {
                "python": "Py",
                "updates": "↑",
                "refresh": "⟲",
                "mail": "✉",
                "ticket": "🎟",
                "thermometer": "T°",
                "battery": "⚡",
                "zap": "⚡",
                "battery_low": "⚠",
            }
        }

    def get_widget_defaults(self):
        """Get widget defaults"""
        return self.widget_defaults

    def get_extension_defaults(self):
        """Get extension defaults"""
        return self.extension_defaults

    def _create_icon_widget(self, icon_key, text_fallback="", color=None):
        """Create an icon widget based on the selected method with error handling"""
        colordict = self.color_manager.get_colors()
        icon_color = color or colordict["colors"]["color5"]

        match self.icon_method:
            case "svg":
                icon_path = self.icons["svg"].get(icon_key)
                if icon_path and Path(icon_path).exists():
                    try:
                        # Try to create SVG image widget
                        return widget.Image(
                            filename=icon_path,
                            background=colordict["special"]["background"]
                        )
                    except Exception as e:
                        logger.warning(f"Failed to load SVG icon {icon_path}: {e}")
                        # Try PNG fallback
                        png_path = icon_path.replace('.svg', '.png')
                        if Path(png_path).exists():
                            try:
                                return widget.Image(
                                    filename=png_path,
                                    background=colordict["special"]["background"]
                                )
                            except Exception as e2:
                                logger.warning(f"Failed to load PNG fallback {png_path}: {e2}")

                # Final fallback to text
                return widget.TextBox(
                    text=text_fallback or self.icons["text"].get(icon_key, "?"),
                    foreground=icon_color,
                    background=colordict["special"]["background"],
                    fontsize=16,
                )

            case "image":
                icon_path = self.icons["image"].get(icon_key)
                if icon_path and Path(icon_path).exists():
                    try:
                        return widget.Image(
                            filename=icon_path,
                            background=colordict["special"]["background"]
                        )
                    except Exception as e:
                        logger.warning(f"Failed to load PNG icon {icon_path}: {e}")

                # Fallback to text if image doesn't exist or fails to load
                return widget.TextBox(
                    text=text_fallback or self.icons["text"].get(icon_key, "?"),
                    foreground=icon_color,
                    background=colordict["special"]["background"],
                    fontsize=16,
                )

            case "nerd_font":
                return widget.TextBox(
                    text=self.icons["nerd_font"].get(icon_key, text_fallback),
                    foreground=icon_color,
                    background=colordict["special"]["background"],
                    font="MonoMono Nerd Font",  # Use your preferred Nerd Font
                    fontsize=16,
                )

            case _:  # text method
                return widget.TextBox(
                    text=self.icons["text"].get(icon_key, text_fallback),
                    foreground=icon_color,
                    background=colordict["special"]["background"],
                    fontsize=16,
                )

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

    def _check_bsd_battery(self, system: str) -> bool:
        """Check for battery on BSD systems"""
        import subprocess
        try:
            if system == "openbsd":
                result = subprocess.run(['apm'], capture_output=True, text=True, timeout=5)
                return result.returncode == 0 and 'battery' in result.stdout.lower()
            else:
                result = subprocess.run(['acpiconf', '-i', '0'], capture_output=True, text=True, timeout=5)
                return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _check_darwin_battery(self) -> bool:
        """Check for battery on macOS"""
        import subprocess
        try:
            result = subprocess.run(['pmset', '-g', 'batt'], capture_output=True, text=True, timeout=5)
            return result.returncode == 0 and 'InternalBattery' in result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _has_battery(self) -> bool:
        """Check if the system has a battery (cross-platform)"""
        import platform

        try:
            system = platform.system().lower()

            match system:
                case "linux":
                    return self._check_linux_battery()
                case "openbsd" | "freebsd" | "netbsd" | "dragonfly":
                    return self._check_bsd_battery(system)
                case "darwin":
                    return self._check_darwin_battery()
                case _:
                    logger.debug(f"Unknown system {system}, skipping battery widget")
                    return False

        except Exception as e:
            logger.debug(f"Error detecting battery: {e}")
            return False

    def _has_mpd_support(self) -> bool:
        """Check if MPD Python module is available"""
        try:

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
                    from qtile_extras import widget
                    widget.Battery()
                    return True
                except Exception as e:
                    logger.debug(f"Battery widget not supported on {system}: {e}")
                    return False

            return True
        except Exception as e:
            logger.debug(f"Error checking battery widget support: {e}")
            return False

    def _script_available(self, script_path: str) -> bool:
        """Check if script exists and is executable"""
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
        """Create GenPollText widgets for available scripts using bitmap icons"""

        # Map script types to icon keys
        script_icon_mapping = {
            'imap-checker': 'mail',
            'kayako': 'ticket',
            'cputemp': 'thermometer'
        }

        widgets = []
        for config in self.qtile_config.script_configs:
            if self._script_available(config['script_path']):
                # Determine icon based on script name
                icon_key = None
                for script_type, icon in script_icon_mapping.items():
                    if script_type in config['script_path'].lower():
                        icon_key = icon
                        break

                if icon_key:
                    # Add icon widget
                    widgets.append(self._create_icon_widget(icon_key))
                else:
                    # Fallback to original icon text
                    widgets.append(widget.TextBox(config['icon']))

                # Add the data widget
                widgets.append(widget.GenPollText(
                    foreground=colordict["colors"]["color5"],
                    background=colordict["special"]["background"],
                    update_interval=config['update_interval'],
                    func=self._safe_script_call(config['script_path'], config['fallback']),
                ))
                logger.debug(f"Added {config['name']} widget with bitmap icon")
            else:
                logger.debug(f"{config['name']} script not found: {config['script_path']}")

        return widgets

    def create_bar_config(self, screen_num: int) -> Bar:
        """Create bar configuration for a specific screen with bitmap icons"""
        colordict = self.color_manager.get_colors()
        logger.info(f"Bar config for screen {screen_num + 1} using {self.icon_method} icons")

        # Start with core widgets that are always available
        barconfig = [
            # Python logo (replaces 🐍)
            self._create_icon_widget("python"),

            widget.GroupBox(
                background=colordict["special"]["background"],
                foreground=colordict["colors"]["color5"],
                active=colordict["colors"]["color7"],
                inactive=colordict["colors"]["color1"],
                border=colordict["colors"]["color1"],
                this_current_screen_border=colordict["colors"]["color6"],
                hide_unused=True,
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

        # Continue with update checking widgets (with bitmap icons)
        barconfig.extend([
            # Package updates (replaces 🔼)
            self._create_icon_widget("updates"),
            widget.CheckUpdates(
                foreground=colordict["colors"]["color5"],
                background=colordict["special"]["background"],
                update_interval=3600,
                display_format="{updates}",
                distro="Arch_checkupdates",
                no_update_string="0",
            ),
            # AUR updates (replaces 🔄)
            self._create_icon_widget("refresh"),
            widget.CheckUpdates(
                foreground=colordict["colors"]["color5"],
                background=colordict["special"]["background"],
                update_interval=3600,
                display_format="{updates}",
                distro="Arch_yay",
                no_update_string="0",
            ),
        ])

        # Add script-based widgets (with bitmap icons)
        script_widgets = self._get_script_widgets(colordict)
        barconfig.extend(script_widgets)

        # Conditionally add Battery widget if supported on this platform
        if self._has_battery_widget_support():
            barconfig.extend([
                self._create_icon_widget("battery"),
                widget.Battery(
                    foreground=colordict["colors"]["color5"],
                    background=colordict["special"]["background"],
                    charge_char="",  # Remove emoji, icon widget handles this
                    discharge_char="",
                    empty_char="",
                    full_char="",
                    format="{percent:2.0%} {hour:d}:{min:02d}",
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

    def set_icon_method(self, method: str):
        """Change the icon method"""
        if method in ["svg", "image", "nerd_font", "text"]:
            self.icon_method = method
            logger.info(f"Icon method changed to: {method}")
        else:
            logger.warning(f"Invalid icon method: {method}")


def create_bar_manager(color_manager: "ColorManager", qtile_config) -> BarManager:
    """Create and return a bar manager instance"""
    return BarManager(color_manager, qtile_config)
