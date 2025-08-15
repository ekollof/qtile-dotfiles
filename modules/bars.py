#!/usr/bin/env python3
"""
Enhanced bar manager with dynamic SVG icon generation
Integrates SVG utilities for theme-aware, scalable icon generation

@brief Enhanced bar manager with dynamic SVG capabilities for qtile
@author qtile configuration system
"""

import contextlib
import os
import platform
import re
import socket
import subprocess
import threading
import traceback
import urllib.request
from pathlib import Path
from typing import Any

from libqtile import bar
from libqtile.log_utils import logger
from qtile_extras import widget

from modules.dpi_utils import scale_font, scale_size
from modules.popup_notify_widget import create_popup_notify_widget
from modules.svg_utils import create_themed_icon_cache, get_svg_utils


class EnhancedBarManager:
    """
    @brief Enhanced bar manager with dynamic SVG icon capabilities

    Provides dynamic icon generation, theme integration, and real-time
    icon updates based on system state for qtile bars.
    """

    def __init__(self, color_manager: Any, qtile_config: Any) -> None:
        """
        @brief Initialize enhanced bar manager
        @param color_manager: Color management instance
        @param qtile_config: Qtile configuration instance
        """
        self.color_manager = color_manager
        self.qtile_config = qtile_config
        self.hostname = socket.gethostname()
        self.homedir = str(Path.home())

        # Icon configuration with SVG as primary method
        self.icon_method = "svg_dynamic"  # Options: "svg_dynamic", "svg_static", "svg", "image", "nerd_font", "text"
        self.icon_dir = Path(self.homedir) / ".config" / "qtile" / "icons"
        self.dynamic_icon_dir = self.icon_dir / "dynamic"
        self.themed_icon_dir = self.icon_dir / "themed"

        # Initialize SVG utilities
        self.svg_manipulator, self.icon_generator = get_svg_utils(color_manager)

        # Create directories
        self.dynamic_icon_dir.mkdir(parents=True, exist_ok=True)
        self.themed_icon_dir.mkdir(parents=True, exist_ok=True)

        # Initialize themed icons cache
        self.themed_icons: dict[str, str] = {}

        # Widget defaults with DPI awareness
        self.widget_defaults = self._get_widget_defaults()
        self.extension_defaults = self.widget_defaults.copy()

        # Icon mappings for different methods
        self.icons = self._initialize_icon_mappings()

        # System state cache for dynamic icons
        self._system_state_cache = {}

        # Generate themed icon cache (may use fallback colors initially)
        self._update_themed_icon_cache()

        # Setup popup notifications using simple popup system
        notification_settings = self.qtile_config.notification_settings
        if notification_settings.get("use_popups", False):
            popup_config = {
                "width": 350,
                "height": 100,
                "corner": "top_right",
                "margin_x": 20,
                "margin_y": 60,
                "spacing": 10,
                "timeout_normal": notification_settings.get("default_timeout", 5000)
                / 1000.0,
                "timeout_low": notification_settings.get("default_timeout_low", 3000)
                / 1000.0,
                "timeout_critical": 0.0,
            }
            from modules.simple_popup_notifications import setup_popup_notifications

            setup_popup_notifications(color_manager, self.qtile_config, popup_config)
            logger.info("Simple popup notifications configured and enabled")

        # Schedule icon cache refresh after color manager is fully initialized
        self._schedule_icon_refresh()

    def _get_widget_defaults(self) -> dict[str, Any]:
        """
        @brief Get DPI-aware widget defaults
        @return Dictionary of widget default settings
        """
        from modules.font_utils import get_available_font

        return {
            "font": get_available_font(self.qtile_config.preferred_font),
            "fontsize": scale_font(self.qtile_config.preferred_fontsize),
            "padding": scale_size(3),
        }

    def _get_widget_defaults_without_background(self) -> dict[str, Any]:
        """
        @brief Get widget defaults without background for custom styling
        @return Dictionary of widget default settings excluding background
        """
        defaults = self.widget_defaults.copy()
        defaults.pop("background", None)
        return defaults

    def _get_widget_defaults_excluding(self, *exclude_params: str) -> dict[str, Any]:
        """
        @brief Get widget defaults excluding specified parameters
        @param exclude_params: Parameter names to exclude from defaults
        @return Dictionary of widget default settings without conflicts
        """
        defaults = self.widget_defaults.copy()
        for param in exclude_params:
            defaults.pop(param, None)
        return defaults

    def _initialize_icon_mappings(self) -> dict[str, dict[str, str]]:
        """
        @brief Initialize icon mappings for different methods
        @return Dictionary of icon mappings by method
        """
        return {
            "svg": {
                "python": str(self.icon_dir / "python.svg"),
                "platform": str(
                    self.icon_dir / "platform.svg"
                ),  # Platform-specific mascot
                "updates": str(self.icon_dir / "arrow-up.svg"),
                "refresh": str(self.icon_dir / "refresh.svg"),
                "mail": str(self.icon_dir / "mail.svg"),
                "ticket": str(self.icon_dir / "ticket.svg"),
                "thermometer": str(self.icon_dir / "thermometer.svg"),
                "battery": str(self.icon_dir / "battery.svg"),
                "zap": str(self.icon_dir / "zap.svg"),
                "battery_low": str(self.icon_dir / "battery-low.svg"),
                "wifi": str(self.icon_dir / "wifi.svg"),
                "volume": str(self.icon_dir / "volume.svg"),
                "cpu": str(self.icon_dir / "cpu.svg"),
                "memory": str(self.icon_dir / "memory.svg"),
                "network": str(self.icon_dir / "network.svg"),
            },
            "image": {
                "python": str(self.icon_dir / "python.png"),
                "platform": str(
                    self.icon_dir / "platform.png"
                ),  # Platform-specific mascot
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
                "python": "\ue73c",  # Python icon
                "platform": "\uf17c",  # Desktop/computer icon (fallback for platform)
                "updates": "\uf0aa",  # Arrow up
                "refresh": "\uf2f1",  # Refresh
                "mail": "\uf0e0",  # Mail
                "ticket": "\uf3ff",  # Ticket
                "thermometer": "\uf2c9",  # Thermometer
                "battery": "\uf240",  # Battery
                "zap": "\uf0e7",  # Lightning
                "battery_low": "\uf244",  # Battery low
                "wifi": "\uf1eb",  # WiFi
                "volume": "\uf028",  # Volume
                "cpu": "\uf2db",  # Microchip
                "memory": "\uf538",  # Memory
                "network": "\uf0ac",  # Globe
            },
            "text": {
                "python": "🐍",
                "platform": "🖥️",  # Computer emoji for platform
                "updates": "⬆",
                "refresh": "🔄",
                "mail": "📧",
                "ticket": "🎫",
                "thermometer": "🌡",
                "battery": "🔋",
                "zap": "⚡",
                "battery_low": "🪫",
                "wifi": "📶",
                "volume": "🔊",
                "cpu": "💻",
                "memory": "🧠",
                "network": "🌐",
            },
        }

    def _update_themed_icon_cache(self) -> None:
        """
        @brief Generate/update themed icon cache based on current colors
        """
        try:
            self.themed_icons = create_themed_icon_cache(
                self.color_manager,
                self.themed_icon_dir,
                scale_size(24),  # DPI-aware icon size
            )
            logger.debug(f"Generated {len(self.themed_icons)} themed icons")
        except Exception as e:
            logger.warning(f"Failed to generate themed icon cache: {e}")
            self.themed_icons = {}

    def _schedule_icon_refresh(self) -> None:
        """
        @brief Schedule icon cache refresh after color manager initialization

        This helps ensure icons get proper theme colors even if the color manager
        wasn't fully initialized during bar manager construction.
        """

        def refresh_icons():
            try:
                # Force a fresh color load
                if hasattr(self.color_manager, "force_start_monitoring"):
                    old_icons_count = len(self.themed_icons)
                    self._update_themed_icon_cache()
                    new_icons_count = len(self.themed_icons)
                    if new_icons_count > 0 and new_icons_count != old_icons_count:
                        logger.info(
                            f"Refreshed themed icons: {old_icons_count} -> {new_icons_count}"
                        )
            except Exception as e:
                logger.debug(
                    f"Icon refresh failed (this is normal during startup): {e}"
                )

        # Try to refresh icons after a short delay

        threading.Timer(2.0, refresh_icons).start()

    def refresh_themed_icons(self) -> None:
        """
        @brief Public method to refresh themed icon cache when colors change

        Call this method when you know the color scheme has changed and
        icons need to be regenerated with new colors.
        """
        logger.info("Refreshing themed icons with current colors...")
        self._update_themed_icon_cache()
        logger.info(
            f"Themed icon refresh complete: {len(self.themed_icons)} icons generated"
        )

    def create_dynamic_icon(self, icon_type: str, **kwargs: Any) -> str:
        """
        @brief Create icon dynamically based on system state
        @param icon_type: Type of icon (battery, wifi, volume, etc.)
        @param kwargs: Icon-specific parameters
        @return Path to generated SVG file
        """
        try:
            match icon_type:
                case "battery":
                    level = kwargs.get("level", 100)
                    charging = kwargs.get("charging", False)
                    svg_content = self.icon_generator.battery_icon(level, charging)

                case "wifi":
                    strength = kwargs.get("strength", 3)
                    connected = kwargs.get("connected", True)
                    svg_content = self.icon_generator.wifi_icon(strength, connected)

                case "volume":
                    level = kwargs.get("level", 100)
                    muted = kwargs.get("muted", False)
                    svg_content = self.icon_generator.volume_icon(level, muted)

                case "cpu":
                    usage = kwargs.get("usage", 0.0)
                    svg_content = self.icon_generator.cpu_icon(usage)

                case "memory":
                    usage = kwargs.get("usage", 0.0)
                    svg_content = self.icon_generator.memory_icon(usage)

                case "network":
                    rx_active = kwargs.get("rx_active", False)
                    tx_active = kwargs.get("tx_active", False)
                    svg_content = self.icon_generator.network_icon(rx_active, tx_active)

                case "platform":
                    svg_content = self.icon_generator.platform_mascot_icon()

                case "python":
                    svg_content = self.icon_generator.python_icon()

                case "mail":
                    svg_content = self.icon_generator.mail_icon()

                case "ticket":
                    svg_content = self.icon_generator.ticket_icon()

                case "thermometer":
                    svg_content = self.icon_generator.thermometer_icon()

                case "updates":
                    svg_content = self.icon_generator.updates_icon()

                case "refresh":
                    svg_content = self.icon_generator.refresh_icon()

                case _:
                    # Return static themed icon if available
                    return self.themed_icons.get(icon_type, "")

            # Save dynamic icon
            filename = f"{icon_type}_dynamic.svg"
            file_path = self.dynamic_icon_dir / filename
            file_path.write_text(svg_content, encoding="utf-8")

            return str(file_path)

        except Exception as e:
            logger.warning(f"Failed to create dynamic icon {icon_type}: {e}")
            return self.themed_icons.get(icon_type, "")

    def recolor_existing_icon(
        self, icon_path: str, color_overrides: dict[str, str] | None = None
    ) -> str:
        """
        @brief Recolor an existing SVG icon with current theme
        @param icon_path: Path to existing SVG file
        @param color_overrides: Optional color overrides
        @return Path to recolored icon
        """
        try:
            svg_icon = self.svg_manipulator.load_svg(icon_path)
            if not svg_icon:
                return icon_path

            # Apply theme colors
            themed_icon = self.svg_manipulator.theme_colorize(
                svg_icon, color_overrides or {}
            )

            # Save themed version
            original_path = Path(icon_path)
            themed_path = self.themed_icon_dir / f"themed_{original_path.name}"

            if self.svg_manipulator.save_svg(themed_icon, themed_path):
                return str(themed_path)
            else:
                return icon_path

        except Exception as e:
            logger.warning(f"Failed to recolor icon {icon_path}: {e}")
            return icon_path

    def _create_icon_widget(
        self,
        icon_key: str,
        text_fallback: str = "",
        color: str | None = None,
        **dynamic_kwargs: Any,
    ) -> Any:
        """
        @brief Create an icon widget based on the selected method with dynamic support
        @param icon_key: Icon identifier key
        @param text_fallback: Fallback text if icon fails to load
        @param color: Optional color override
        @param dynamic_kwargs: Parameters for dynamic icon generation
        @return Configured widget
        """
        colordict = self.color_manager.get_colors()
        colors = colordict.get("colors", {})
        special = colordict.get("special", {})
        icon_color = color or colors.get("color5", "#ffffff")
        bg_color = special.get("background", "#000000")

        match self.icon_method:
            case "svg_dynamic":
                # Use dynamic SVG generation
                icon_path = self.create_dynamic_icon(icon_key, **dynamic_kwargs)
                if icon_path and Path(icon_path).exists():
                    try:
                        return widget.Image(
                            filename=icon_path,
                            background=bg_color,
                            margin=scale_size(2),
                        )
                    except Exception as e:
                        logger.warning(
                            f"Failed to load dynamic SVG icon {icon_path}: {e}"
                        )

                # Fall back to themed static icon
                themed_path = self.themed_icons.get(icon_key)
                if themed_path and Path(themed_path).exists():
                    try:
                        return widget.Image(
                            filename=themed_path,
                            background=bg_color,
                            margin=scale_size(2),
                        )
                    except Exception as e:
                        logger.warning(f"Failed to load themed icon {themed_path}: {e}")

            case "svg_static":
                # Use static themed icons
                themed_path = self.themed_icons.get(icon_key)
                if themed_path and Path(themed_path).exists():
                    try:
                        return widget.Image(
                            filename=themed_path,
                            background=bg_color,
                            margin=scale_size(2),
                        )
                    except Exception as e:
                        logger.warning(f"Failed to load themed icon {themed_path}: {e}")

            case "svg":
                # Use original SVG files with recoloring
                icon_path = self.icons["svg"].get(icon_key)
                if icon_path and Path(icon_path).exists():
                    themed_path = self.recolor_existing_icon(icon_path)
                    try:
                        return widget.Image(
                            filename=themed_path,
                            background=bg_color,
                            margin=scale_size(2),
                        )
                    except Exception as e:
                        logger.warning(f"Failed to load SVG icon {themed_path}: {e}")

            case "image":
                # Use PNG images
                icon_path = self.icons["image"].get(icon_key)
                if icon_path and Path(icon_path).exists():
                    try:
                        return widget.Image(
                            filename=icon_path,
                            background=bg_color,
                            margin=scale_size(2),
                        )
                    except Exception as e:
                        logger.warning(f"Failed to load PNG icon {icon_path}: {e}")

            case "nerd_font":
                # Use Nerd Font icons
                from modules.font_utils import get_available_font

                return widget.TextBox(
                    text=self.icons["nerd_font"].get(icon_key, text_fallback),
                    foreground=icon_color,
                    background=bg_color,
                    font=get_available_font(self.qtile_config.preferred_font),
                    fontsize=scale_font(self.qtile_config.preferred_icon_fontsize),
                    padding=scale_size(3),
                )

            case _:  # "text" or fallback
                # Use text/emoji icons
                return widget.TextBox(
                    text=self.icons["text"].get(icon_key, text_fallback),
                    foreground=icon_color,
                    background=bg_color,
                    fontsize=scale_font(self.qtile_config.preferred_icon_fontsize),
                    padding=scale_size(3),
                )

        # Final fallback to text
        return widget.TextBox(
            text=text_fallback or "?",
            foreground=icon_color,
            background=bg_color,
            fontsize=scale_font(self.qtile_config.preferred_icon_fontsize),
            padding=scale_size(3),
        )

    def _check_battery_support(self) -> bool:
        """
        @brief Check if battery widget is supported on current platform
        @return True if battery is supported
        """
        try:
            system = platform.system().lower()
            logger.debug(f"Checking battery support for platform: {system}")

            match system:
                case "linux":
                    result = self._check_linux_battery()
                    logger.debug(f"Linux battery check result: {result}")
                    return result
                case "openbsd" | "freebsd" | "netbsd" | "dragonfly":
                    result = self._check_bsd_battery(system)
                    logger.debug(f"BSD ({system}) battery check result: {result}")
                    return result
                case _:
                    logger.debug(f"Unsupported platform for battery widget: {system}")
                    return False

        except Exception as e:
            logger.warning(f"Exception during battery support check: {e}")
            return False

    def _check_linux_battery(self) -> bool:
        """
        @brief Check for battery on Linux systems
        @return True if battery detected
        """
        # Battery detection paths for different Unix-like systems
        battery_paths = [
            "/sys/class/power_supply/BAT0",  # Linux standard
            "/sys/class/power_supply/BAT1",  # Linux secondary battery
            "/sys/class/power_supply/battery",  # Linux generic
            "/dev/acpi/battery",  # FreeBSD
            "/dev/apm",  # OpenBSD APM
        ]

        for path in battery_paths:
            if Path(path).exists():
                type_file = Path(path) / "type"
                if type_file.exists():
                    try:
                        battery_type = type_file.read_text().strip().lower()
                        if battery_type == "battery":
                            # Test actual widget compatibility
                            return self._test_battery_widget_compatibility()
                    except Exception:
                        continue
        return False

    def _check_bsd_battery(self, system: str) -> bool:
        """
        @brief Check for battery on BSD systems
        @param system: BSD system type
        @return True if battery detected
        """
        try:
            if system == "openbsd":
                logger.debug("Checking OpenBSD battery with 'apm' command")
                result = subprocess.run(
                    ["apm"], capture_output=True, text=True, timeout=5
                )
                logger.debug(
                    f"apm command result: returncode={result.returncode}, stdout='{result.stdout.strip()}'"
                )

                if result.returncode != 0:
                    logger.debug("apm command failed, no battery detected")
                    return False

                output_lower = result.stdout.lower()
                has_battery = "battery" in output_lower

                # Additional checks for OpenBSD - apm might show "no battery" or similar
                if "no battery" in output_lower or "not present" in output_lower:
                    logger.debug("apm output indicates no battery present")
                    return False

                logger.debug(f"OpenBSD battery detection result: {has_battery}")

                # If apm suggests battery exists, test actual widget compatibility
                if has_battery:
                    return self._test_battery_widget_compatibility()
                return False
            else:
                logger.debug(f"Checking {system} battery with 'acpiconf' command")
                result = subprocess.run(
                    ["acpiconf", "-i", "0"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                logger.debug(f"acpiconf command result: returncode={result.returncode}")
                has_battery = result.returncode == 0
                logger.debug(f"{system} battery detection result: {has_battery}")

                # Test actual widget compatibility if acpiconf suggests battery exists
                if has_battery:
                    return self._test_battery_widget_compatibility()
                return False

        except subprocess.TimeoutExpired:
            logger.debug(f"Battery check command timed out on {system}")
            return False
        except FileNotFoundError:
            logger.debug(f"Battery check command not found on {system}")
            return False
        except Exception as e:
            logger.debug(f"Exception during {system} battery check: {e}")
            return False

    def _get_icon_theme_path(self) -> str:
        """
        @brief Get appropriate icon theme path for the current system
        @return Path to suitable icon theme directory
        """
        # Common icon theme locations across Unix-like systems
        theme_paths = [
            "/usr/share/icons/breeze-dark",  # KDE Plasma (Linux)
            "/usr/share/icons/Adwaita",  # GNOME default
            "/usr/local/share/icons/breeze-dark",  # FreeBSD/OpenBSD KDE
            "/opt/local/share/icons/breeze-dark",  # macOS with MacPorts
            "/usr/share/pixmaps",  # Fallback
        ]

        for path in theme_paths:
            if Path(path).exists():
                return path

        # Ultimate fallback - no theme path
        return ""

    def _test_battery_widget_compatibility(self) -> bool:
        """
        @brief Test if qtile Battery widget can actually be created on this platform
        @return True if Battery widget is compatible
        """
        try:
            logger.debug("Testing Battery widget compatibility by attempting creation")
            # Try to create a minimal battery widget to test compatibility
            _ = widget.Battery(format="{percent:2.0%}")
            logger.debug("Battery widget compatibility test passed")
            return True
        except RuntimeError as e:
            if "Unknown platform" in str(e):
                logger.debug(f"Battery widget not compatible: {e}")
                return False
            else:
                logger.warning(f"Unexpected error during battery widget test: {e}")
                return False
        except Exception as e:
            logger.debug(f"Battery widget compatibility test failed: {e}")
            return False

    def _script_available(self, script_path: str) -> bool:
        """
        @brief Check if a script is available and executable
        @param script_path: Path to script
        @return True if script is available
        """
        path_obj = Path(script_path).expanduser()
        return path_obj.exists() and path_obj.is_file() and os.access(path_obj, os.X_OK)

    def _safe_script_call(self, script_path: str, fallback: str = "N/A"):
        """
        @brief Create safe script call function with comprehensive error handling
        @param script_path: Path to script
        @param fallback: Fallback value on failure
        @return Function that safely calls script
        """
        def safe_call():
            try:
                script_path_obj = Path(script_path).expanduser()
                result = subprocess.run(
                    [str(script_path_obj)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                # Check if we got valid output regardless of return code
                output = result.stdout.strip()
                if output and output != "N/A" and len(output) > 0:
                    # Script produced output - use it even if return code is non-zero
                    logger.debug(f"Script {script_path} output: '{output}' (return code: {result.returncode})")
                    return output

                # No valid output - check what went wrong
                if result.returncode != 0:
                    stderr = result.stderr.strip()
                    if stderr:
                        logger.warning(f"Script {script_path} failed with error: {stderr}")
                    else:
                        logger.warning(f"Script {script_path} failed with return code {result.returncode} but no error message")
                else:
                    logger.warning(f"Script {script_path} succeeded but returned empty output")

                return fallback

            except subprocess.TimeoutExpired:
                logger.warning(f"Script {script_path} timed out")
                return fallback
            except FileNotFoundError:
                logger.warning(f"Script {script_path} not found")
                return fallback
            except Exception as e:
                logger.warning(f"Script {script_path} execution error: {e}")
                return fallback

        return safe_call

    def _get_script_widgets(self, colordict: dict[str, Any]) -> list[Any]:
        """
        @brief Create GenPollText widgets for available scripts with dynamic icons
        @param colordict: Color dictionary from color manager
        @return List of configured widgets
        """
        from modules.font_utils import get_available_font

        script_icon_mapping = {
            "imap-checker": "mail",
            "kayako": "ticket",
            "cputemp": "thermometer",
        }

        # Extract colors once at the beginning
        colors = colordict.get("colors", {})
        special = colordict.get("special", {})

        widgets = []
        for config in self.qtile_config.script_configs:
            if self._script_available(config["script_path"]):
                # Determine icon based on script name
                icon_key = None
                for script_type, icon in script_icon_mapping.items():
                    if script_type in config["script_path"].lower():
                        icon_key = icon
                        break

                if icon_key:
                    # Add dynamic icon widget
                    widgets.append(self._create_icon_widget(icon_key))
                else:
                    # Fallback to original icon text
                    widgets.append(
                        widget.TextBox(
                            text=config["icon"],
                            foreground=colors.get("color5", "#ffffff"),
                            background=special.get("background", "#000000"),
                            font=get_available_font(self.qtile_config.preferred_font),
                            fontsize=scale_font(
                                self.qtile_config.preferred_icon_fontsize
                            ),
                            padding=scale_size(3),
                        )
                    )

                # Add script output widget
                widgets.append(
                    widget.GenPollText(
                        foreground=colors.get("color5", "#ffffff"),
                        background=special.get("background", "#000000"),
                        font=get_available_font(self.qtile_config.preferred_font),
                        fontsize=scale_font(self.qtile_config.preferred_fontsize),
                        padding=scale_size(3),
                        update_interval=config["update_interval"],
                        func=self._safe_script_call(
                            config["script_path"], config["fallback"]
                        ),
                    )
                )
                logger.debug(f"Added {config['name']} widget with dynamic icon")
            else:
                logger.debug(
                    f"{config['name']} script not found: {config['script_path']}"
                )

        return widgets

    class _OpenBSDDewey:
        """@brief OpenBSD version comparison using Dewey decimal system"""

        def __init__(self, string: str) -> None:
            """@param string Version string to parse"""
            self.deweys = string.split('.')
            self.suffix = ''
            self.suffix_value = 0
            if self.deweys:
                last = self.deweys[-1]
                m = re.match(r'^(\d+)(rc|alpha|beta|pre|pl)(\d*)$', last)
                if m:
                    self.deweys[-1] = m.group(1)
                    self.suffix = m.group(2)
                    self.suffix_value = int(m.group(3) or '0')

        def to_string(self) -> str:
            """@return String representation of version"""
            r = '.'.join(self.deweys)
            if self.suffix:
                r += self.suffix + (str(self.suffix_value) if self.suffix_value else '')
            return r

        def compare(self, other: 'EnhancedBarManager._OpenBSDDewey') -> int:
            """@param other Other version to compare @return -1, 0, or 1"""
            deweys1 = self.deweys
            deweys2 = other.deweys
            min_len = min(len(deweys1), len(deweys2))
            for i in range(min_len):
                r = self._dewey_part_compare(deweys1[i], deweys2[i])
                if r != 0:
                    return r
            r = len(deweys1) - len(deweys2)
            if r != 0:
                return 1 if r > 0 else -1
            return self._suffix_compare(other)

        def _dewey_part_compare(self, a: str, b: str) -> int:
            """@brief Compare individual dewey parts"""
            if a.isdigit() and b.isdigit():
                ia = int(a)
                ib = int(b)
                return 1 if ia > ib else -1 if ia < ib else 0
            return 1 if a > b else -1 if a < b else 0

        def _suffix_compare(self, other: 'EnhancedBarManager._OpenBSDDewey') -> int:
            """@brief Compare version suffixes (rc, alpha, beta, etc.)"""
            if self.suffix == other.suffix:
                return 1 if self.suffix_value > other.suffix_value else -1 if self.suffix_value < other.suffix_value else 0
            if self.suffix == 'pl':
                return 1
            if other.suffix == 'pl':
                return -1
            if self.suffix == '':
                return 1
            if self.suffix in ['alpha', 'beta']:
                return -1
            return 0

    class _OpenBSDVersion:
        """@brief OpenBSD package version with v and p handling"""

        def __init__(self, string: str) -> None:
            """@param string Version string to parse"""
            self.original_string = string
            self.v = 0
            m = re.match(r'(.*)v(\d+)$', string)
            if m:
                self.v = int(m.group(2))
                string = m.group(1)
            self.p = -1
            m = re.match(r'(.*)p(\d+)$', string)
            if m:
                self.p = int(m.group(2))
                string = m.group(1)
            self.dewey = EnhancedBarManager._OpenBSDDewey(string)

        def compare(self, other: 'EnhancedBarManager._OpenBSDVersion') -> int:
            """@param other Other version to compare @return -1, 0, or 1"""
            if self.v != other.v:
                return 1 if self.v > other.v else -1
            if self.dewey.to_string() == other.dewey.to_string():
                return 1 if self.p > other.p else -1 if self.p < other.p else 0
            return self.dewey.compare(other.dewey)

    def _get_openbsd_update_count(self) -> int:
        """
        @brief Count available OpenBSD package updates
        @return Number of packages with available updates
        @throws Exception if update checking fails
        """
        try:
            # Multi-version package stems (packages that can have multiple versions)
            multi_version_stems = {
                'lua', 'python', 'ruby', 'php', 'perl', 'postgresql',
                'mariadb', 'node', 'tcl', 'tk'
            }

            def get_version_prefix(v: str) -> str:
                """Get major.minor version prefix"""
                parts = v.split('.')
                numeric = []
                for p in parts:
                    m = re.match(r'^\d+', p)
                    if not m:
                        break
                    numeric.append(m.group(0))
                    if len(numeric) >= 2:
                        break
                return '.'.join(numeric)

            # Determine mirror
            mirror = 'https://cdn.openbsd.org/pub/OpenBSD'
            installurl_path = Path('/etc/installurl')
            if installurl_path.exists():
                with installurl_path.open('r') as f:
                    mirror = f.readline().strip()

            # Determine if -current
            is_current = False
            try:
                sysctl_output = subprocess.check_output(['sysctl', 'kern.version']).decode()
                if '-current' in sysctl_output:
                    is_current = True
            except subprocess.CalledProcessError:
                pass

            # Determine release and arch
            release = 'snapshots' if is_current else subprocess.check_output(['uname', '-r']).decode().strip()
            arch = subprocess.check_output(['machine']).decode().strip()

            # Construct URL
            url = f"{mirror}/{release}/packages/{arch}/index.txt"

            # Fetch index.txt with timeout
            try:
                with urllib.request.urlopen(url, timeout=30) as response:
                    index_data = response.read().decode()
            except Exception as e:
                logger.warning(f"Failed to fetch OpenBSD package index: {e}")
                return 0

            # Load available packages
            available = {}
            for line in index_data.splitlines():
                fields = line.split()
                if not fields:
                    continue
                file = fields[-1]
                if not file.endswith('.tgz'):
                    continue
                file = file[:-4]
                m = re.match(r'^(.*?)-(\d.*)$', file)
                if m:
                    stem = m.group(1)
                    rest = m.group(2)
                    parts = rest.split('-')
                    version = parts[0]
                    flavor = '-'.join(parts[1:]) if len(parts) > 1 else ''
                else:
                    stem = file
                    version = ''
                    flavor = ''
                key = stem + ('-' + flavor if flavor else '')
                available[key] = file

            # Get all installed packages
            pkg_db = Path('/var/db/pkg')
            if not pkg_db.exists():
                logger.warning("OpenBSD package database not found")
                return 0

            installed = [entry.name for entry in pkg_db.iterdir()
                        if entry.is_dir() and (entry / '+CONTENTS').is_file()]

            # Count updates
            count = 0
            for inst in installed:
                if inst.startswith('quirks-'):
                    continue

                m = re.match(r'^(.*?)-(\d.*)$', inst)
                if m:
                    stem = m.group(1)
                    rest = m.group(2)
                    parts = rest.split('-')
                    version = parts[0]
                    flavor = '-'.join(parts[1:]) if len(parts) > 1 else ''
                else:
                    stem = inst
                    version = ''
                    flavor = ''

                key = stem + ('-' + flavor if flavor else '')
                if key not in available:
                    continue

                cand = available[key]
                m = re.match(r'^(.*?)-(\d.*)$', cand)
                if m:
                    rest_c = m.group(2)
                    parts_c = rest_c.split('-')
                    version_c = parts_c[0]
                else:
                    continue

                if stem in multi_version_stems:
                    prefix = get_version_prefix(version)
                    prefix_c = get_version_prefix(version_c)
                    if prefix != prefix_c:
                        continue

                v_inst = EnhancedBarManager._OpenBSDVersion(version)
                v_cand = EnhancedBarManager._OpenBSDVersion(version_c)
                if v_cand.compare(v_inst) > 0:
                    count += 1

            return count

        except Exception as e:
            logger.error(f"OpenBSD update check failed: {e}")
            return 0

    def _create_safe_check_updates_widget(self, distro: str, colors: dict[str, str], special: dict[str, str]):
        """
        @brief Create CheckUpdates widget with proper error handling
        @param distro: Distribution type for updates check
        @param colors: Color dictionary
        @param special: Special colors dictionary
        @return CheckUpdates widget instance with error handling
        """
        try:
            # Create widget with safe configuration
            updates_widget = widget.CheckUpdates(
                **self._get_widget_defaults_excluding("background"),
                foreground=colors.get("color5", "#ffffff"),
                background=special.get("background", "#000000"),
                update_interval=3600,
                display_format="{updates}",
                distro=distro,
                no_update_string="0",
                colour_have_updates=colors.get("color3", "#ffff00"),
                colour_no_updates=colors.get("color5", "#ffffff"),
                # Add error handling parameters
                execute=None,  # Disable click action to prevent issues
                mouse_callbacks={},  # Clear mouse callbacks
            )

            logger.debug(f"Created CheckUpdates widget for {distro}")
            return updates_widget

        except Exception as e:
            logger.warning(f"Failed to create CheckUpdates widget for {distro}: {e}")
            # Return a simple TextBox as fallback
            return widget.TextBox(
                text="0",
                foreground=colors.get("color5", "#ffffff"),
                background=special.get("background", "#000000"),
                fontsize=scale_font(self.qtile_config.preferred_fontsize),
            )

    def _detect_package_manager(self) -> list[str]:
        """
        @brief Detect available package managers and return appropriate distro strings
        @return List of distro strings for CheckUpdates widget based on qtile-extras documentation

        Supported distros from qtile-extras CheckUpdates:
        Arch, Arch_checkupdates, Arch_Sup, Arch_paru, Arch_paru_Sup, Arch_yay,
        Debian, Gentoo_eix, Guix, Ubuntu, Fedora, FreeBSD, Mandriva, Void
        """
        available_distros = []

        # Check platform first
        system = platform.system().lower()
        logger.debug(f"Detected system: {system}")

        if system == "linux":
            # Check for Arch Linux
            if Path("/etc/arch-release").exists():
                # Check for checkupdates command (official repos) - preferred method
                if subprocess.run(["which", "checkupdates"], capture_output=True).returncode == 0:
                    available_distros.append("Arch_checkupdates")
                    logger.debug("Found checkupdates - adding Arch_checkupdates")

                # Check for paru (AUR helper) - preferred over yay
                if subprocess.run(["which", "paru"], capture_output=True).returncode == 0:
                    available_distros.append("Arch_paru")
                    logger.debug("Found paru - adding Arch_paru")
                # Check for yay (alternative AUR helper)
                elif subprocess.run(["which", "yay"], capture_output=True).returncode == 0:
                    available_distros.append("Arch_yay")
                    logger.debug("Found yay - adding Arch_yay")
                # Fallback to basic pacman
                elif subprocess.run(["which", "pacman"], capture_output=True).returncode == 0:
                    available_distros.append("Arch")
                    logger.debug("Found pacman - adding Arch")

            # Check for Ubuntu/Debian
            elif Path("/etc/debian_version").exists():
                try:
                    with open("/etc/os-release") as f:
                        os_info = f.read().lower()
                        if "ubuntu" in os_info:
                            if subprocess.run(["which", "aptitude"], capture_output=True).returncode == 0:
                                available_distros.append("Ubuntu")
                                logger.debug("Found aptitude - adding Ubuntu")
                        else:  # Debian or derivative
                            if subprocess.run(["which", "apt-show-versions"], capture_output=True).returncode == 0:
                                available_distros.append("Debian")
                                logger.debug("Found apt-show-versions - adding Debian")
                except FileNotFoundError:
                    # Fallback to generic check
                    if subprocess.run(["which", "apt"], capture_output=True).returncode == 0:
                        available_distros.append("Ubuntu")  # Use Ubuntu as fallback
                        logger.debug("Found apt - adding Ubuntu (fallback)")

            # Check for Fedora
            elif Path("/etc/fedora-release").exists():
                if subprocess.run(["which", "dnf"], capture_output=True).returncode == 0:
                    available_distros.append("Fedora")
                    logger.debug("Found dnf - adding Fedora")

            # Check for Gentoo
            elif Path("/etc/gentoo-release").exists():
                if subprocess.run(["which", "eix"], capture_output=True).returncode == 0:
                    available_distros.append("Gentoo_eix")
                    logger.debug("Found eix - adding Gentoo_eix")

            # Check for Void Linux
            elif Path("/etc/os-release").exists():
                try:
                    with open("/etc/os-release") as f:
                        if "void" in f.read().lower() and subprocess.run(["which", "xbps-install"], capture_output=True).returncode == 0:
                            available_distros.append("Void")
                            logger.debug("Found xbps-install - adding Void")
                except FileNotFoundError:
                    pass

        elif system == "freebsd":
            if subprocess.run(["which", "pkg"], capture_output=True).returncode == 0:
                available_distros.append("FreeBSD")
                logger.debug("Found pkg - adding FreeBSD")

        elif system == "openbsd":
            # OpenBSD support via custom implementation - double check with uname
            if Path("/usr/sbin/pkg_add").exists():
                try:
                    uname_output = subprocess.check_output(['uname']).decode().strip().lower()
                    if uname_output == "openbsd":
                        available_distros.append("OpenBSD")
                        logger.debug("OpenBSD confirmed via uname and pkg_add - adding OpenBSD")
                    else:
                        logger.warning(f"pkg_add found but uname reports '{uname_output}', not OpenBSD")
                except subprocess.CalledProcessError:
                    logger.warning("pkg_add found but uname command failed - skipping OpenBSD")

        elif system == "darwin":  # macOS
            # Note: Homebrew is NOT in the supported list, but we could add it if needed
            logger.info("macOS detected but Homebrew not in CheckUpdates supported distros")

        if not available_distros:
            logger.info(f"No supported package managers detected on {system}")
            logger.info("Update widgets support: Arch variants, Debian, Ubuntu, Fedora, Gentoo, Void, FreeBSD, OpenBSD")
        else:
            logger.info(f"Detected supported package managers: {available_distros}")

        return available_distros

    def _create_update_widgets(self, colors: dict[str, str], special: dict[str, str]) -> list[Any]:
        """
        @brief Create update checking widgets based on detected package managers
        @param colors: Color dictionary
        @param special: Special colors dictionary
        @return List of widgets for package update checking
        """
        widgets = []
        distros = self._detect_package_manager()

        if not distros:
            logger.info("No package managers detected - skipping update widgets")
            return widgets

        # Create appropriate icons and widgets for each detected package manager
        for i, distro in enumerate(distros):
            # Add icon - use different icons for different types
            if "arch" in distro.lower() or "aur" in distro.lower():
                icon = "updates" if i == 0 else "refresh"
            elif distro in ["Ubuntu", "Fedora", "RHEL", "openSUSE"]:
                icon = "updates"
            elif distro in ["OpenBSD", "FreeBSD"]:
                icon = "updates"  # Use updates icon for BSD systems
            elif distro == "Homebrew":
                icon = "updates"
            else:
                icon = "updates"

            widgets.append(self._create_icon_widget(icon))

            # Handle OpenBSD with custom widget since CheckUpdates doesn't support it
            if distro == "OpenBSD":
                from modules.font_utils import get_available_font

                openbsd_widget = widget.GenPollText(
                    func=self._get_openbsd_update_count,
                    update_interval=3600,
                    **self._get_widget_defaults_excluding("background"),
                    foreground=colors.get("color5", "#ffffff"),
                    background=special.get("background", "#000000"),
                    format="{updates}",
                    font=get_available_font(self.qtile_config.preferred_font),
                )
                widgets.append(openbsd_widget)
                logger.debug("Created GenPollText widget for OpenBSD updates")
            else:
                widgets.append(self._create_safe_check_updates_widget(distro, colors, special))

        return widgets

    def create_bar_config(self, screen_num: int) -> bar.Bar:
        """
        @brief Create bar configuration for a specific screen with dynamic SVG icons
        @param screen_num: Screen number (0-based)
        @return Configured bar instance
        """
        colordict = self.color_manager.get_colors()
        colors = colordict.get("colors", {})
        special = colordict.get("special", {})
        logger.info(
            f"Creating bar config for screen {screen_num + 1} using {self.icon_method} icons"
        )

        # Start with core widgets
        barconfig = [
            # Platform mascot with dynamic coloring (Tux for Linux, Puffy for OpenBSD, etc.)
            self._create_icon_widget("platform"),
            widget.GroupBox(
                **self._get_widget_defaults_excluding("background", "padding"),
                background=special.get("background", "#000000"),
                foreground=colors.get("color5", "#ffffff"),
                active=colors.get("color7", "#ffffff"),
                inactive=colors.get("color1", "#808080"),
                border=colors.get("color1", "#808080"),
                this_current_screen_border=colors.get("color6", "#00ff00"),
                other_current_screen_border=colors.get("color4", "#0000ff"),
                this_screen_border=colors.get("color4", "#0000ff"),
                other_screen_border=colors.get("color0", "#000000"),
                highlight_color=colors.get("color6", "#00ff00"),
                highlight_method="line",
                borderwidth=scale_size(2),
                margin_y=scale_size(3),
                margin_x=0,
                padding_y=scale_size(5),
                padding_x=scale_size(3),
                disable_drag=True,
                hide_unused=True,
            ),
            widget.TaskList(
                border=colors.get("color1", "#808080"),
                foreground=special.get("foreground", "#ffffff"),
                theme_mode="preferred",
                # Fallback icon theme paths for different systems
                theme_path=self._get_icon_theme_path(),
            ),
            widget.Spacer(),
        ]

        # Add script widgets if available
        script_widgets = self._get_script_widgets(colordict)
        barconfig.extend(script_widgets)

        # System monitoring widgets with dynamic icons
        barconfig.extend(
            # Package updates - auto-detect based on system
            self._create_update_widgets(colors, special)
        )

        barconfig.extend(
            [
                # CPU usage with dynamic icon
                self._create_icon_widget("cpu"),
                widget.CPU(
                    **self._get_widget_defaults_excluding("background"),
                    foreground=colors.get("color5", "#ffffff"),
                    background=special.get("background", "#000000"),
                    format="{load_percent:3.0f}%",
                    update_interval=5,
                ),
                # Memory usage with dynamic icon
                self._create_icon_widget("memory"),
                widget.Memory(
                    **self._get_widget_defaults_excluding("background"),
                    foreground=colors.get("color5", "#ffffff"),
                    background=special.get("background", "#000000"),
                    format="{MemPercent:3.0f}%",
                    update_interval=5,
                ),
                # Network activity with dynamic icon
                self._create_icon_widget("network"),
                widget.Net(
                    **self._get_widget_defaults_excluding("background"),
                    foreground=colors.get("color5", "#ffffff"),
                    background=special.get("background", "#000000"),
                    format="{down:>3.0f}{down_suffix:<2} ↓↑ {up:>3.0f}{up_suffix:<2}",
                    update_interval=5,
                ),
                # Volume with dynamic icon
                self._create_icon_widget("volume"),
                widget.Volume(
                    **self._get_widget_defaults_excluding("background"),
                    foreground=colors.get("color5", "#ffffff"),
                    background=special.get("background", "#000000"),
                    fmt="{}",
                    update_interval=1,
                ),
            ]
        )

        # Add battery widget if supported
        battery_supported = self._check_battery_support()
        logger.info(f"Battery widget support check: {battery_supported}")

        if battery_supported:
            try:
                barconfig.extend(
                    [
                        self._create_icon_widget("battery"),
                        widget.Battery(
                            **self._get_widget_defaults_excluding("background"),
                            foreground=colors.get("color5", "#ffffff"),
                            background=special.get("background", "#000000"),
                            format="{percent:2.0%}",
                            update_interval=30,
                            low_percentage=0.20,
                            low_foreground=colors.get("color1", "#ff0000"),
                            charge_char="↑",
                            discharge_char="↓",
                            full_char="=",
                            unknown_char="?",
                        ),
                    ]
                )
                logger.info("Successfully added Battery widget with dynamic icon")
            except RuntimeError as e:
                if "Unknown platform" in str(e):
                    logger.warning(
                        f"Battery widget not supported on this platform: {e}"
                    )
                    logger.info(
                        "Skipping Battery widget due to platform incompatibility"
                    )
                else:
                    logger.error(f"Runtime error creating Battery widget: {e}")
                    logger.info("Continuing without Battery widget")
            except Exception as e:
                logger.error(
                    f"Failed to create Battery widget despite support check passing: {e}"
                )
                logger.info("Continuing without Battery widget")
        else:
            logger.info("Skipping Battery widget - not supported on this platform")

        # Clock and system tray
        barconfig.extend(
            [
                widget.Clock(
                    **self._get_widget_defaults_excluding("background"),
                    foreground=colors.get("color5", "#ffffff"),
                    background=special.get("background", "#000000"),
                    format="%Y-%m-%d %H:%M:%S",
                    update_interval=1,
                ),
            ]
        )

        # Add notification widget only to primary screen to avoid duplicates
        if screen_num == 0:
            try:
                notification_settings = self.qtile_config.notification_settings
                if notification_settings.get("enabled", True):
                    use_popups = notification_settings.get("use_popups", False)
                    show_in_bar = notification_settings.get("show_in_bar", True)

                    # Create popup notification widget
                    notification_widget = create_popup_notify_widget(
                        **self._get_widget_defaults_excluding("background"),
                        foreground=special.get("foreground", "#ffffff"),
                        background=special.get("background", "#000000"),
                        default_timeout=notification_settings.get(
                            "default_timeout", 5000
                        )
                        // 1000,
                        default_timeout_low=notification_settings.get(
                            "default_timeout_low", 3000
                        )
                        // 1000,
                        default_timeout_urgent=notification_settings.get(
                            "default_timeout_urgent", 0
                        )
                        // 1000
                        if notification_settings.get("default_timeout_urgent", 0) > 0
                        else None,
                        action=notification_settings.get("enable_actions", True),
                        audiofile=None
                        if not notification_settings.get("enable_sound", False)
                        else notification_settings.get("sound_file"),
                        show_in_bar=show_in_bar,
                        show_popups=use_popups,
                    )

                    barconfig.append(notification_widget)
                    mode_desc = (
                        "popup"
                        if use_popups and not show_in_bar
                        else ("popup + bar" if use_popups else "bar only")
                    )
                    logger.info(
                        f"Added popup notification widget to primary screen ({mode_desc})"
                    )
                else:
                    logger.info("Notification system disabled in configuration")
            except Exception as e:
                logger.warning(f"Failed to add notification widget: {e}")

        # Add system tray only to primary screen with error handling
        if screen_num == 0:
            try:
                barconfig.append(
                    widget.Systray(
                        background=special.get("background", "#000000"),
                        icon_size=scale_size(20),
                        padding=scale_size(5),
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to create Systray widget: {e}")
                # Continue without system tray

        # Add current layout widget
        barconfig.extend(
            [
                widget.CurrentLayout(
                    **self._get_widget_defaults_excluding("background"),
                    background=special.get("background", "#000000"),
                ),
            ]
        )

        # Create bar with DPI-aware height
        return bar.Bar(
            barconfig,
            size=self.qtile_config.bar_settings["height"],
            background=special.get("background", "#000000"),
            opacity=self.qtile_config.bar_settings["opacity"],
            margin=self.qtile_config.bar_settings["margin"],
        )

    def update_dynamic_icons(self) -> None:
        """
        @brief Update dynamic icons based on current system state

        This method should be called when colors change or system state updates
        to regenerate themed icons.
        """
        try:
            # Regenerate themed icon cache
            self._update_themed_icon_cache()

            # Clear dynamic icon cache to force regeneration
            if self.dynamic_icon_dir.exists():
                for icon_file in self.dynamic_icon_dir.glob("*.svg"):
                    with contextlib.suppress(Exception):
                        icon_file.unlink()

            logger.info("Dynamic icons updated for new color scheme")

        except Exception as e:
            logger.warning(f"Failed to update dynamic icons: {e}")

    def get_icon_status(self) -> dict[str, Any]:
        """
        @brief Get status information about icon system
        @return Dictionary with icon system status
        """
        return {
            "method": self.icon_method,
            "themed_icons_count": len(self.themed_icons),
            "icon_dirs": {
                "base": str(self.icon_dir),
                "dynamic": str(self.dynamic_icon_dir),
                "themed": str(self.themed_icon_dir),
            },
            "svg_utils_available": hasattr(self.svg_manipulator, "load_svg")
            and callable(getattr(self.svg_manipulator, "load_svg", None)),
        }

    def get_widget_defaults(self) -> dict[str, Any]:
        """
        @brief Get widget defaults for compatibility
        @return Dictionary of widget default settings
        """
        return self.widget_defaults

    def get_extension_defaults(self) -> dict[str, Any]:
        """
        @brief Get extension defaults for compatibility
        @return Dictionary of extension default settings
        """
        return self.extension_defaults

    def create_screens(self, screen_count: int | None = None) -> list[Any]:
        """
        @brief Create screen configurations with bars
        @param screen_count: Number of screens to create
        @return List of screen configurations
        """
        from libqtile.config import Screen

        # Ensure screen_count is a valid integer
        if screen_count is None or screen_count <= 0:
            screen_count = 1

        screens = []
        for i in range(screen_count):
            try:
                bar_config = self.create_bar_config(i)
                screen = Screen(top=bar_config)
                screens.append(screen)
                logger.debug(f"Created screen {i + 1} with enhanced SVG bar")
            except Exception as e:
                logger.error(f"Failed to create screen {i + 1}: {e}")
                logger.error(f"Full traceback for screen {i + 1}:")
                logger.error(traceback.format_exc())
                logger.info(f"Creating fallback screen {i + 1} without bar")
                # Create fallback screen without bar
                screens.append(Screen())

        return screens


def create_enhanced_bar_manager(
    color_manager: Any, qtile_config: Any
) -> EnhancedBarManager:
    """
    @brief Factory function to create enhanced bar manager
    @param color_manager: Color management instance
    @param qtile_config: Qtile configuration instance
    @return Configured EnhancedBarManager instance
    """
    return EnhancedBarManager(color_manager, qtile_config)
