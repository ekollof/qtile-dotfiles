#!/usr/bin/env python3
"""
Bars and widgets module for qtile - BITMAP ICONS VERSION
Handles bar configuration and widget setup using bitmap icons instead of emoticons

This is a modified version that replaces emoticons with bitmap icons.
You can choose between different icon approaches:
1. SVG vector images (recommended)
2. PNG bitmap images  
3. Nerd Font icons (uses your configured preferred font)
4. Simple text symbols

Usage: Replace your current bars.py with this file or copy the relevant parts.
"""

import os
import socket
import subprocess
import platform
from typing import final, Any, TYPE_CHECKING
from libqtile import widget as qtwidget
from libqtile.bar import Bar
from libqtile.config import Screen
from libqtile.lazy import lazy
from libqtile.log_utils import logger
from qtile_extras import widget
from modules.font_utils import get_available_font
from modules.dpi_utils import scale_size, scale_font

if TYPE_CHECKING:
    from modules.colors import ColorManager


@final
class BarManager:
    """Manages qtile bar configuration and widget creation with bitmap icons"""

    def __init__(self, color_manager: "ColorManager", qtile_config) -> None:
        self.color_manager = color_manager
        self.qtile_config = qtile_config
        self.hostname = socket.gethostname()
        self.homedir = os.getenv("HOME")
        
        # Icon configuration - choose your preferred method
        self.icon_method = "svg"  # Options: "svg", "image", "nerd_font", "text"
        self.icon_dir = os.path.join(self.homedir, ".config", "qtile", "icons")

        # Widget defaults - DPI aware
        self.widget_defaults = dict(
            font=get_available_font(qtile_config.preferred_font),
            fontsize=scale_font(15),  # DPI-scaled base font size
            padding=scale_size(3),    # DPI-scaled padding
            border_with=scale_size(3),
            border_focus=color_manager.get_colors()["special"]["foreground"],
            border_normal=color_manager.get_colors()["special"]["background"],
            foreground=color_manager.get_colors()["special"]["foreground"],
            background=color_manager.get_colors()["special"]["background"],
        )

        self.extension_defaults = self.widget_defaults.copy()
        
        # Icon mappings for different methods
        self.icons = {
            "svg": {
                "python": os.path.join(self.icon_dir, "python.svg"),
                "updates": os.path.join(self.icon_dir, "arrow-up.svg"),
                "refresh": os.path.join(self.icon_dir, "refresh.svg"),
                "mail": os.path.join(self.icon_dir, "mail.svg"),
                "ticket": os.path.join(self.icon_dir, "ticket.svg"),
                "thermometer": os.path.join(self.icon_dir, "thermometer.svg"),
                "battery": os.path.join(self.icon_dir, "battery.svg"),
                "zap": os.path.join(self.icon_dir, "zap.svg"),
                "battery_low": os.path.join(self.icon_dir, "battery-low.svg"),
            },
            "image": {
                "python": os.path.join(self.icon_dir, "python.png"),
                "updates": os.path.join(self.icon_dir, "arrow-up.png"),
                "refresh": os.path.join(self.icon_dir, "refresh.png"),
                "mail": os.path.join(self.icon_dir, "mail.png"),
                "ticket": os.path.join(self.icon_dir, "ticket.png"),
                "thermometer": os.path.join(self.icon_dir, "thermometer.png"),
                "battery": os.path.join(self.icon_dir, "battery.png"),
                "zap": os.path.join(self.icon_dir, "zap.png"),
                "battery_low": os.path.join(self.icon_dir, "battery-low.png"),
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
        
        if self.icon_method == "svg":
            icon_path = self.icons["svg"].get(icon_key)
            if icon_path and os.path.exists(icon_path):
                try:
                    # Try to create SVG image widget
                    return widget.Image(
                        filename=icon_path,
                        foreground=colordict["colors"]["color5"],
                        background=colordict["special"]["background"],
                        margin_x=scale_size(3),
                        margin_y=scale_size(2),
                    )
                except Exception as e:
                    logger.warning(f"Failed to load SVG icon {icon_path}: {e}")
                    # Fallback to PNG if SVG fails
                    png_path = self.icons["image"].get(icon_key)
                    if png_path and os.path.exists(png_path):
                        try:
                            return widget.Image(
                                filename=png_path,
                                background=colordict["special"]["background"],
                                margin_x=scale_size(3),
                                margin_y=scale_size(2),
                            )
                        except Exception as e2:
                            logger.warning(f"Failed to load PNG fallback {png_path}: {e2}")
            
            # Final fallback to text
            return widget.TextBox(
                text=text_fallback or self.icons["text"].get(icon_key, "?"),
                foreground=icon_color,
                background=colordict["special"]["background"],
                fontsize=scale_font(16),
            )
        
        elif self.icon_method == "image":
            icon_path = self.icons["image"].get(icon_key)
            if icon_path and os.path.exists(icon_path):
                try:
                    return widget.Image(
                        filename=icon_path,
                        background=colordict["special"]["background"],
                        margin_x=scale_size(3),
                        margin_y=scale_size(2),
                    )
                except Exception as e:
                    logger.warning(f"Failed to load PNG icon {icon_path}: {e}")
            
            # Fallback to text if image doesn't exist or fails to load
            return widget.TextBox(
                text=text_fallback or self.icons["text"].get(icon_key, "?"),
                foreground=icon_color,
                background=colordict["special"]["background"],
                fontsize=scale_font(16),
            )
        
        elif self.icon_method == "nerd_font":
            return widget.TextBox(
                text=self.icons["nerd_font"].get(icon_key, text_fallback),
                foreground=icon_color,
                background=colordict["special"]["background"],
                font=get_available_font(self.qtile_config.preferred_font),
                fontsize=scale_font(16),
            )
        
        else:  # text method
            return widget.TextBox(
                text=self.icons["text"].get(icon_key, text_fallback),
                foreground=icon_color,
                background=colordict["special"]["background"],
                fontsize=scale_font(16),
            )

    def _has_battery(self) -> bool:
        """Check if the system has a battery (cross-platform)"""
        import platform
        import subprocess
        
        try:
            system = platform.system().lower()
            
            if system == "linux":
                # Linux: Check /sys/class/power_supply/
                battery_paths = [
                    "/sys/class/power_supply/BAT0",
                    "/sys/class/power_supply/BAT1", 
                    "/sys/class/power_supply/battery"
                ]
                
                for path in battery_paths:
                    if os.path.exists(path):
                        # Check if it's actually a battery (not just AC adapter)
                        type_file = os.path.join(path, "type")
                        if os.path.exists(type_file):
                            with open(type_file, 'r') as f:
                                if f.read().strip().lower() == "battery":
                                    return True
                return False
                
            elif system in ["openbsd", "freebsd", "netbsd", "dragonfly"]:
                # BSD systems: Use apm or acpiconf
                try:
                    if system == "openbsd":
                        # OpenBSD: Use apm command
                        result = subprocess.run(['apm'], capture_output=True, text=True, timeout=5)
                        # If apm runs without error and shows battery info, we have a battery
                        return result.returncode == 0 and 'battery' in result.stdout.lower()
                    else:
                        # FreeBSD/NetBSD: Try acpiconf
                        result = subprocess.run(['acpiconf', '-i', '0'], capture_output=True, text=True, timeout=5)
                        return result.returncode == 0
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    return False
                    
            elif system == "darwin":
                # macOS: Use pmset command
                try:
                    result = subprocess.run(['pmset', '-g', 'batt'], capture_output=True, text=True, timeout=5)
                    return result.returncode == 0 and 'InternalBattery' in result.stdout
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    return False
                    
            else:
                # Unknown system: Don't try to use battery widget
                logger.debug(f"Unknown system {system}, skipping battery widget")
                return False
                    
        except Exception as e:
            logger.debug(f"Error detecting battery: {e}")
            return False

    def _has_mpd_support(self) -> bool:
        """Check if MPD Python module is available"""
        try:
            import mpd
            logger.debug("MPD module available")
            return True
        except ImportError:
            logger.debug("MPD module not available")
            return False

    def _has_battery_widget_support(self) -> bool:
        """Check if qtile's battery widget supports current platform"""
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
                    test_widget = widget.Battery()
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
        expanded_path = os.path.expanduser(script_path)
        return os.path.isfile(expanded_path) and os.access(expanded_path, os.X_OK)

    def _safe_script_call(self, script_path: str, fallback_text: str = "N/A") -> callable:
        """Create a safe wrapper for script calls that handles missing scripts gracefully"""
        expanded_path = os.path.expanduser(script_path)
        
        def wrapper():
            try:
                if not os.path.isfile(expanded_path):
                    return fallback_text
                
                result = subprocess.check_output(
                    expanded_path, 
                    stderr=subprocess.DEVNULL,
                    timeout=10
                )
                return result.strip().decode("utf-8")
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
            if self._script_exists(config['script_path']):
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
                # Show only active groups (groups with windows) and current group
                hide_unused=True,
                # Optional: Customize what constitutes "unused"
                # visible_groups=None,  # Use default behavior
                mouse_callbacks={"Button1": lazy.spawn("dmenu_run")},
            ),
            widget.Prompt(),
            widget.TaskList(
                border=colordict["colors"]["color1"],
                foreground=colordict["colors"]["color5"],
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

        return Bar(barconfig, scale_size(32), margin=scale_size(5), opacity=0.8)

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
