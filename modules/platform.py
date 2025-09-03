#!/usr/bin/env python3
"""
Consolidated Platform Module

@brief Unified platform detection, configuration, and icon generation for qtile
@author Andrath

This module consolidates platform detection, configuration utilities,
and platform-specific icon generation into a single, well-organized system.

Features:
- Cross-platform compatibility (Linux, BSD variants)
- Platform-specific application preferences
- Command overrides for different systems
- Platform mascot icon generation
- SVG icon theming and scaling

Usage:
    from modules.platform import get_platform_info, get_platform_mascot_icon
    platform_info = get_platform_info()
    icon_svg = get_platform_mascot_icon(color_manager)
"""

import platform
import shutil
from typing import Any

try:
    from libqtile.log_utils import logger
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


class PlatformInfo:
    """
    @brief Container for platform-specific information and utilities

    Provides methods to detect the current operating system and determine
    available applications, with fallbacks for cross-platform compatibility.
    """

    def __init__(self) -> None:
        """
        @brief Initialize platform detection and cache system information
        """
        self._system = platform.system().lower()
        self._release = platform.release()
        self._machine = platform.machine()
        self._cached_commands: dict[str, str | None] = {}

    @property
    def system(self) -> str:
        """
        @brief Get the operating system name in lowercase
        @return Operating system name (linux, openbsd, freebsd, etc.)
        """
        return self._system

    @property
    def is_linux(self) -> bool:
        """
        @brief Check if running on Linux
        @return True if the system is Linux
        """
        return self._system == "linux"

    @property
    def is_openbsd(self) -> bool:
        """
        @brief Check if running on OpenBSD
        @return True if the system is OpenBSD
        """
        return self._system == "openbsd"

    @property
    def is_freebsd(self) -> bool:
        """
        @brief Check if running on FreeBSD
        @return True if the system is FreeBSD
        """
        return self._system == "freebsd"

    @property
    def is_netbsd(self) -> bool:
        """
        @brief Check if running on NetBSD
        @return True if the system is NetBSD
        """
        return self._system == "netbsd"

    @property
    def is_bsd(self) -> bool:
        """
        @brief Check if running on any BSD variant
        @return True if the system is any BSD variant
        """
        return self._system in {"openbsd", "freebsd", "netbsd", "dragonfly"}

    @property
    def release(self) -> str:
        """
        @brief Get the operating system release version
        @return OS release version string
        """
        return self._release

    @property
    def machine(self) -> str:
        """
        @brief Get the machine architecture
        @return Machine architecture string (amd64, x86_64, etc.)
        """
        return self._machine

    def find_command(self, command: str) -> str | None:
        """
        @brief Find the full path of a command if it exists
        @param command: Command name to search for
        @return Full path to command or None if not found
        """
        if command in self._cached_commands:
            return self._cached_commands[command]

        path = shutil.which(command)
        self._cached_commands[command] = path
        return path

    def has_command(self, command: str) -> bool:
        """
        @brief Check if a command is available in PATH
        @param command: Command name to check
        @return True if command is available
        """
        return self.find_command(command) is not None

    def get_preferred_application(
        self, app_type: str, preferences: list[str]
    ) -> str | None:
        """
        @brief Get the preferred application from a list of candidates
        @param app_type: Type of application (for logging purposes)
        @param preferences: List of application names in order of preference
        @return First available application or None if none found
        """
        for app in preferences:
            if self.has_command(app):
                return app
        return None


class PlatformConfig:
    """
    @brief Platform-specific configuration manager

    Provides platform-specific overrides for applications, commands,
    and other configuration values based on the detected operating system.
    """

    def __init__(self, platform_info: PlatformInfo | None = None) -> None:
        """
        @brief Initialize platform configuration manager
        @param platform_info: Optional PlatformInfo instance, creates new if None
        """
        self.platform = platform_info or PlatformInfo()
        self._config_overrides: dict[str, dict[str, Any]] = {}
        self._application_preferences: dict[str, Any] = {}
        self._load_platform_configs()

    def _load_platform_configs(self) -> None:
        """
        @brief Load platform-specific configuration overrides

        Orchestrates loading of all platform-specific configurations
        by calling focused configuration methods.
        """
        self._application_preferences = self._get_application_preferences()
        self._config_overrides = self._get_command_overrides()

    def _get_terminal_preferences(self) -> dict[str, list[str]]:
        """
        @brief Get terminal emulator preferences by platform
        @return Dictionary mapping platforms to terminal preference lists
        """
        return {
            "linux": ["st", "alacritty", "kitty", "xterm"],
            "openbsd": ["st", "urxvt", "xterm"],
            "freebsd": ["st", "alacritty", "xterm"],
            "netbsd": ["st", "urxvt", "xterm"],
        }

    def _get_browser_preferences(self) -> dict[str, list[str]]:
        """
        @brief Get browser preferences by platform
        @return Dictionary mapping platforms to browser preference lists
        """
        return {
            "linux": ["brave", "chromium", "google-chrome"],
            "openbsd": ["chrome", "iridium"],
            "freebsd": ["chromium", "brave"],
            "netbsd": ["chromium"],
        }

    def _get_file_manager_preferences(self) -> dict[str, list[str]]:
        """
        @brief Get file manager preferences by platform
        @return Dictionary mapping platforms to file manager preference lists
        """
        return {
            "linux": ["thunar", "pcmanfm", "nautilus", "dolphin"],
            "openbsd": ["pcmanfm", "thunar", "xfe"],
            "freebsd": ["pcmanfm", "thunar", "nautilus"],
            "netbsd": ["pcmanfm", "xfe"],
        }

    def _get_launcher_preferences(self) -> dict[str, list[str]]:
        """
        @brief Get application launcher preferences by platform
        @return Dictionary mapping platforms to launcher preference lists
        """
        return {
            "linux": ["rofi", "dmenu", "albert", "ulauncher"],
            "openbsd": ["rofi", "dmenu"],
            "freebsd": ["rofi", "dmenu"],
            "netbsd": ["dmenu"],
        }

    def _get_media_player_preferences(self) -> dict[str, list[str]]:
        """
        @brief Get media player preferences by platform
        @return Dictionary mapping platforms to media player preference lists
        """
        return {
            "linux": ["mpv", "vlc", "mplayer"],
            "openbsd": ["mpv", "mplayer", "vlc"],
            "freebsd": ["mpv", "vlc", "mplayer"],
            "netbsd": ["mplayer", "mpv"],
        }

    def _get_application_preferences(self) -> dict[str, dict[str, list[str]]]:
        """
        @brief Aggregate all application preferences by type and platform
        @return Dictionary mapping application types to platform preferences
        """
        return {
            "terminal": self._get_terminal_preferences(),
            "browser": self._get_browser_preferences(),
            "file_manager": self._get_file_manager_preferences(),
            "launcher": self._get_launcher_preferences(),
            "media_player": self._get_media_player_preferences(),
        }

    def _get_command_overrides(self) -> dict[str, dict[str, str]]:
        """
        @brief Get platform-specific command overrides
        @return Dictionary mapping platforms to command overrides
        """
        return {
            "linux": {
                "lock_session": "loginctl lock-session",
                "clipboard_manager": "clipmenu.sh",
                "clipmenuscreenshot": "flameshot gui",
                "audio_mixer": "pavucontrol",
                "network_manager": "nm-connection-editor",
            },
            "openbsd": {
                "lock_session": "xlock",
                "clipboard_manager": "clipmenu.sh",
                "clipmenuscreenshot": "xwd | xwdtopnm | pnmtopng",
                "audio_mixer": "mixerctl",
                "network_manager": "ifconfig",
            },
            "freebsd": {
                "lock_session": "xlock",
                "clipboard_manager": "xclip",
                "screenshot": "scrot",
                "audio_mixer": "mixer",
                "network_manager": "bsdconfig networking",
            },
            "netbsd": {
                "lock_session": "xlock",
                "clipboard_manager": "xclip",
                "screenshot": "xwd",
                "audio_mixer": "mixerctl",
                "network_manager": "ifconfig",
            },
        }

    def get_application(self, app_type: str, fallback: str | None = None) -> str:
        """
        @brief Get the best available application for the current platform
        @param app_type: Type of application to find
        @param fallback: Fallback application if none of the preferences are available
        @return Application command name
        """
        system = self.platform.system

        if app_type in self._application_preferences:
            # Use match statement for cleaner platform-specific logic
            match system:
                case "openbsd" | "freebsd" | "netbsd" | "dragonfly":
                    preferences = self._application_preferences[app_type].get(
                        system,
                        self._application_preferences[app_type].get("openbsd", []),
                    )
                case "linux":
                    preferences = self._application_preferences[app_type]["linux"]
                case _:
                    preferences = self._application_preferences[app_type].get(
                        system,
                        self._application_preferences[app_type].get("linux", []),
                    )

            app = self.platform.get_preferred_application(app_type, preferences)
            if app:
                return app

        # If no preferred app found, return fallback or default
        return fallback or "xterm"

    def get_command(self, command_type: str, fallback: str | None = None) -> str:
        """
        @brief Get platform-specific command override
        @param command_type: Type of command to get
        @param fallback: Fallback command if no override exists
        @return Command string for the current platform
        """
        system = self.platform.system

        # Use match statement for platform-specific command selection
        match system:
            case "linux":
                command = self._config_overrides.get("linux", {}).get(command_type)
            case "openbsd":
                command = self._config_overrides.get("openbsd", {}).get(command_type)
            case "freebsd":
                command = self._config_overrides.get("freebsd", {}).get(command_type)
            case "netbsd":
                command = self._config_overrides.get("netbsd", {}).get(command_type)
            case _:
                command = self._config_overrides.get(system, {}).get(command_type)

        if command:
            # Verify the base command exists
            base_cmd = command.split()[0]
            if self.platform.has_command(base_cmd):
                return command

        # Return fallback or try Linux defaults
        if fallback:
            return fallback

        linux_defaults = self._config_overrides.get("linux", {})
        return linux_defaults.get(command_type, "")

    def get_config_overrides(self) -> dict[str, Any]:
        """
        @brief Get all configuration overrides for the current platform
        @return Dictionary of configuration overrides
        """
        return self._config_overrides.get(self.platform.system, {})

    def add_override(self, key: str, value: Any) -> None:
        """
        @brief Add a configuration override for the current platform
        @param key: Configuration key
        @param value: Configuration value
        """
        system = self.platform.system
        if system not in self._config_overrides:
            self._config_overrides[system] = {}
        self._config_overrides[system][key] = value


class PlatformMascotGenerator:
    """
    @brief Generates platform-specific mascot icons for the system bar

    Detects the current platform and provides appropriate SVG mascot icons
    that represent the operating system in a fun, recognizable way.
    """

    def __init__(self, color_manager: Any = None) -> None:
        """
        @brief Initialize platform mascot generator
        @param color_manager: Optional color manager for theming
        """
        self.color_manager = color_manager
        self.current_platform = self._detect_platform()
        logger.debug(f"Detected platform: {self.current_platform}")

    def _detect_platform(self) -> str:
        """
        @brief Detect the current operating system platform
        @return Platform identifier string
        """
        system = platform.system().lower()

        # Use modern match statement (Python 3.10+)
        match system:
            case "openbsd":
                return "openbsd"
            case "freebsd":
                return "freebsd"
            case "netbsd":
                return "netbsd"
            case "dragonfly":
                return "dragonfly"
            case "linux":
                return "linux"
            case "darwin":
                return "macos"
            case "windows":
                return "windows"
            case _:
                # Fallback for unknown systems
                logger.debug(
                    f"Unknown platform '{system}', using generic computer icon"
                )
                return "generic"

    def get_platform_mascot(self, size: int = 24) -> str:
        """
        @brief Get SVG content for the current platform's mascot
        @param size: Icon size in pixels
        @return SVG content as string
        """
        colors = self._get_colors()

        match self.current_platform:
            case "linux":
                return self._tux_penguin(size, colors)
            case "openbsd":
                return self._puffy_pufferfish(size, colors)
            case "freebsd":
                return self._beastie_daemon(size, colors)
            case "netbsd":
                return self._netbsd_flag(size, colors)
            case "dragonfly":
                return self._beastie_daemon(
                    size, colors
                )  # DragonFly uses same mascot as FreeBSD
            case "macos":
                return self._apple_logo(size, colors)
            case "windows":
                return self._windows_logo(size, colors)
            case _:
                return self._generic_computer(size, colors)

    def _get_colors(self) -> dict[str, str]:
        """
        @brief Get themed colors for the mascot
        @return Dictionary of color values
        """
        if self.color_manager:
            try:
                qtile_colors = self.color_manager.get_colors()
                if qtile_colors and "colors" in qtile_colors:
                    return {
                        "primary": qtile_colors["colors"][
                            "color5"
                        ],  # Main color (blue)
                        "secondary": qtile_colors["colors"][
                            "color11"
                        ],  # Warning/accent color
                        "accent": qtile_colors["colors"]["color4"],  # Different blue
                        "highlight": qtile_colors["colors"]["color15"],  # Light color
                        "dark": qtile_colors["colors"]["color0"],  # Dark color
                        "background": qtile_colors["special"]["background"],
                        "foreground": qtile_colors["colors"]["color5"],  # Match text
                        "white": qtile_colors["colors"]["color15"],  # Light/white
                        "orange": qtile_colors["colors"]["color11"],  # Orange/yellow
                    }
            except Exception as e:
                logger.debug(f"Could not get colors from color_manager: {e}")

        # Fallback colors
        return {
            "primary": "#4A88A2",  # Medium blue
            "secondary": "#9E6C8F",  # Purple accent
            "accent": "#39919B",  # Teal
            "highlight": "#C5C5DE",  # Light purple
            "dark": "#424446",  # Dark gray
            "background": "#17191A",  # Dark background
            "foreground": "#4A88A2",  # Match text color
            "white": "#C5C5DE",  # Light color
            "orange": "#9E6C8F",  # Orange/accent
        }

    def _tux_penguin(self, size: int, colors: dict[str, str]) -> str:
        """
        @brief Generate Tux the penguin (Linux mascot) - Enhanced version
        @param size: Icon size
        @param colors: Color scheme
        @return SVG content
        """
        # Enhanced Tux with more details and better proportions
        black = colors["dark"]  # Dark body
        white = colors["white"]  # Belly and face
        orange = colors["orange"]  # Beak and feet
        eye_highlight = colors["highlight"]  # Eye highlights

        return f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <!-- Tux the Penguin - Linux Mascot (Enhanced) -->
            <!-- Main body with better shape -->
            <ellipse cx="12" cy="16.5" rx="6.5" ry="5.2" fill="{black}"/>

            <!-- Head with better proportions -->
            <circle cx="12" cy="8.5" r="4.8" fill="{black}"/>

            <!-- White belly with better shape -->
            <ellipse cx="12" cy="15.8" rx="4" ry="3.8" fill="{white}"/>

            <!-- White face area with better shape -->
            <ellipse cx="12" cy="9" rx="2.8" ry="2.2" fill="{white}"/>

            <!-- Orange beak with better shape -->
            <ellipse cx="12" cy="10" rx="1.2" ry="0.6" fill="{orange}"/>

            <!-- Eyes with better proportions and highlights -->
            <circle cx="10.2" cy="8" r="0.8" fill="{black}"/>
            <circle cx="13.8" cy="8" r="0.8" fill="{black}"/>
            <circle cx="10.4" cy="7.7" r="0.25" fill="{eye_highlight}"/>
            <circle cx="14" cy="7.7" r="0.25" fill="{eye_highlight}"/>

            <!-- Enhanced wings/flippers -->
            <ellipse cx="6.8" cy="13.5" rx="2" ry="3.5" fill="{black}" transform="rotate(-15 6.8 13.5)"/>
            <ellipse cx="17.2" cy="13.5" rx="2" ry="3.5" fill="{black}" transform="rotate(15 17.2 13.5)"/>

            <!-- Enhanced feet with better shape -->
            <ellipse cx="9.5" cy="20.5" rx="1.8" ry="1" fill="{orange}"/>
            <ellipse cx="14.5" cy="20.5" rx="1.8" ry="1" fill="{orange}"/>

            <!-- Add subtle shadow for depth -->
            <ellipse cx="12" cy="21" rx="5" ry="0.8" fill="{colors["background"]}" opacity="0.3"/>
        </svg>"""

    def _puffy_pufferfish(self, size: int, colors: dict[str, str]) -> str:
        """
        @brief Generate Puffy the pufferfish (OpenBSD mascot) - Enhanced version
        @param size: Icon size
        @param colors: Color scheme
        @return SVG content
        """
        # Enhanced Puffy with more spikes and better details
        body_color = colors["primary"]  # Main body
        spike_color = colors["accent"]  # Spikes
        eye_color = colors["dark"]  # Eyes
        mouth_color = colors["orange"]  # Mouth
        fin_color = colors["secondary"]  # Fins and tail
        eye_highlight = colors["highlight"]  # Eye highlights

        return f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <!-- Puffy the Pufferfish - OpenBSD Mascot (Enhanced) -->
            <!-- Main body with better shape -->
            <ellipse cx="12" cy="12" rx="7.5" ry="6.5" fill="{body_color}"/>

            <!-- Enhanced spikes around body (more spikes, better positioned) -->
            <!-- Top spikes -->
            <circle cx="8" cy="6.5" r="0.7" fill="{spike_color}"/>
            <circle cx="12" cy="5" r="0.7" fill="{spike_color}"/>
            <circle cx="16" cy="6.5" r="0.7" fill="{spike_color}"/>

            <!-- Side spikes -->
            <circle cx="5.5" cy="10" r="0.7" fill="{spike_color}"/>
            <circle cx="18.5" cy="10" r="0.7" fill="{spike_color}"/>
            <circle cx="5.5" cy="14" r="0.7" fill="{spike_color}"/>
            <circle cx="18.5" cy="14" r="0.7" fill="{spike_color}"/>

            <!-- Bottom spikes -->
            <circle cx="8" cy="17.5" r="0.7" fill="{spike_color}"/>
            <circle cx="12" cy="18.5" r="0.7" fill="{spike_color}"/>
            <circle cx="16" cy="17.5" r="0.7" fill="{spike_color}"/>

            <!-- Diagonal spikes for more detail -->
            <circle cx="7" cy="8" r="0.5" fill="{spike_color}"/>
            <circle cx="17" cy="8" r="0.5" fill="{spike_color}"/>
            <circle cx="7" cy="16" r="0.5" fill="{spike_color}"/>
            <circle cx="17" cy="16" r="0.5" fill="{spike_color}"/>

            <!-- Enhanced eyes with highlights -->
            <circle cx="9.5" cy="10.5" r="1.4" fill="{colors["white"]}"/>
            <circle cx="14.5" cy="10.5" r="1.4" fill="{colors["white"]}"/>
            <circle cx="9.5" cy="10.5" r="0.8" fill="{eye_color}"/>
            <circle cx="14.5" cy="10.5" r="0.8" fill="{eye_color}"/>
            <circle cx="9.7" cy="10.2" r="0.25" fill="{eye_highlight}"/>
            <circle cx="14.7" cy="10.2" r="0.25" fill="{eye_highlight}"/>

            <!-- Enhanced mouth -->
            <ellipse cx="12" cy="14.5" rx="1.8" ry="1" fill="{mouth_color}"/>

            <!-- Enhanced fins with better shape -->
            <ellipse cx="5" cy="14" rx="1.2" ry="2.5" fill="{fin_color}" transform="rotate(-25 5 14)"/>
            <ellipse cx="19" cy="14" rx="1.2" ry="2.5" fill="{fin_color}" transform="rotate(25 19 14)"/>

            <!-- Enhanced tail -->
            <polygon points="20,12 23,10.5 23,13.5" fill="{fin_color}"/>

            <!-- Add subtle body texture/shadow -->
            <ellipse cx="12" cy="12.5" rx="6" ry="5" fill="{colors["dark"]}" opacity="0.1"/>
        </svg>"""

    def _beastie_daemon(self, size: int, colors: dict[str, str]) -> str:
        """
        @brief Generate Beastie the BSD daemon (FreeBSD mascot) - Enhanced version
        @param size: Icon size
        @param colors: Color scheme
        @return SVG content
        """
        # Enhanced Beastie with more details and better proportions
        body_color = colors["primary"]  # Main body (red/orange)
        horn_color = colors["dark"]  # Horns (dark)
        eye_color = colors["white"]  # Eyes (white)
        pupil_color = colors["dark"]  # Pupils (dark)
        trident_color = colors["accent"]  # Trident (metallic)
        smile_color = colors["orange"]  # Smile (warm)
        eye_highlight = colors["highlight"]  # Eye highlights

        return f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <!-- Beastie the BSD Daemon - FreeBSD Mascot (Enhanced) -->
            <!-- Head with better shape and details -->
            <ellipse cx="12" cy="10.5" rx="5.2" ry="4.8" fill="{body_color}"/>

            <!-- Enhanced horns with better shape -->
            <polygon points="8.5,6.5 7.5,4.5 9.5,5.5" fill="{horn_color}"/>
            <polygon points="15.5,6.5 16.5,4.5 14.5,5.5" fill="{horn_color}"/>

            <!-- Horn details/highlights -->
            <polygon points="8.7,6.2 8.2,5.2 9.2,5.7" fill="{colors["background"]}" opacity="0.3"/>
            <polygon points="15.3,6.2 15.8,5.2 14.8,5.7" fill="{colors["background"]}" opacity="0.3"/>

            <!-- Enhanced eyes with highlights -->
            <circle cx="10" cy="9.5" r="1.2" fill="{eye_color}"/>
            <circle cx="14" cy="9.5" r="1.2" fill="{eye_color}"/>
            <circle cx="10" cy="9.5" r="0.6" fill="{pupil_color}"/>
            <circle cx="14" cy="9.5" r="0.6" fill="{pupil_color}"/>
            <circle cx="10.3" cy="9.2" r="0.25" fill="{eye_highlight}"/>
            <circle cx="14.3" cy="9.2" r="0.25" fill="{eye_highlight}"/>

            <!-- Enhanced smile -->
            <path d="M 9 12 Q 12 14 15 12" stroke="{smile_color}" stroke-width="1" fill="none" stroke-linecap="round"/>

            <!-- Body with better proportions -->
            <ellipse cx="12" cy="17.5" rx="4.5" ry="5" fill="{body_color}"/>

            <!-- Enhanced arms with better shape -->
            <ellipse cx="7.5" cy="15.5" rx="1.2" ry="3" fill="{body_color}" transform="rotate(-10 7.5 15.5)"/>
            <ellipse cx="16.5" cy="15.5" rx="1.2" ry="3" fill="{body_color}" transform="rotate(10 16.5 15.5)"/>

            <!-- Enhanced trident with better details -->
            <rect x="11.7" y="19.5" width="0.6" height="3.5" fill="{trident_color}"/>
            <polygon points="10.8,19.5 12,18.2 13.2,19.5" fill="{trident_color}"/>
            <!-- Trident prongs -->
            <rect x="11.2" y="19.5" width="0.15" height="2" fill="{trident_color}"/>
            <rect x="12.65" y="19.5" width="0.15" height="2" fill="{trident_color}"/>

            <!-- Enhanced tail with better curve -->
            <path d="M 12 21 Q 14.5 22.5 16 21" stroke="{colors["secondary"]}" stroke-width="1.2" fill="none" stroke-linecap="round"/>

            <!-- Add subtle body shadow for depth -->
            <ellipse cx="12" cy="18" rx="3.5" ry="4" fill="{colors["dark"]}" opacity="0.1"/>
        </svg>"""

    def _netbsd_flag(self, size: int, colors: dict[str, str]) -> str:
        """
        @brief Generate NetBSD flag logo - Enhanced version
        @param size: Icon size
        @param colors: Color scheme
        @return SVG content
        """
        # Enhanced NetBSD flag with better design and more details
        pole_color = colors["dark"]  # Flagpole (dark)
        flag_primary = colors["primary"]  # Main flag color
        flag_accent = colors["accent"]  # Flag accent/stripes
        flag_highlight = colors["white"]  # Flag highlights
        flag_shadow = colors["background"]  # Shadow effects

        return f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <!-- NetBSD Flag Logo (Enhanced) -->
            <!-- Flagpole with better design -->
            <rect x="3.5" y="3" width="2" height="18" fill="{pole_color}" rx="0.5"/>
            <!-- Pole highlight -->
            <rect x="4" y="3.5" width="0.8" height="17" fill="{colors["highlight"]}" opacity="0.3"/>

            <!-- Main flag with better shape and shadow -->
            <polygon points="5.5,3 5.5,15 19.5,9" fill="{flag_primary}"/>
            <!-- Flag shadow for depth -->
            <polygon points="5.7,15.2 19.7,9.2 19.7,9.8 5.7,15.8" fill="{flag_shadow}" opacity="0.2"/>

            <!-- Enhanced flag stripes/pattern with better proportions -->
            <!-- Main horizontal stripes -->
            <rect x="6.5" y="5" width="10" height="1" fill="{flag_accent}"/>
            <rect x="6.5" y="7" width="8" height="1" fill="{flag_highlight}"/>
            <rect x="6.5" y="9" width="6" height="1" fill="{flag_accent}"/>
            <rect x="6.5" y="11" width="4" height="1" fill="{flag_highlight}"/>
            <rect x="6.5" y="13" width="2" height="1" fill="{flag_accent}"/>

            <!-- Vertical accent stripes for more detail -->
            <rect x="8" y="4" width="0.8" height="12" fill="{flag_accent}" opacity="0.6"/>
            <rect x="12" y="4" width="0.8" height="10" fill="{flag_highlight}" opacity="0.4"/>
            <rect x="16" y="4" width="0.8" height="8" fill="{flag_accent}" opacity="0.5"/>

            <!-- NetBSD logo text (stylized) -->
            <text x="8" y="8.5" font-family="monospace" font-size="2.5" fill="{flag_highlight}" opacity="0.8">N</text>
            <text x="11" y="10.5" font-family="monospace" font-size="1.8" fill="{flag_accent}" opacity="0.6">BSD</text>

            <!-- Flag border with better definition -->
            <polygon points="5.5,3 5.5,15 19.5,9" fill="none" stroke="{colors["dark"]}" stroke-width="0.4"/>

            <!-- Wind effect lines -->
            <path d="M 6 4 Q 8 3.5 10 4" stroke="{flag_highlight}" stroke-width="0.3" fill="none" opacity="0.4"/>
            <path d="M 6 6 Q 9 5.5 12 6" stroke="{flag_highlight}" stroke-width="0.3" fill="none" opacity="0.3"/>
            <path d="M 6 8 Q 10 7.5 14 8" stroke="{flag_highlight}" stroke-width="0.3" fill="none" opacity="0.2"/>
        </svg>"""

    def _apple_logo(self, size: int, colors: dict[str, str]) -> str:
        """
        @brief Generate Apple logo (macOS mascot) - Enhanced version
        @param size: Icon size
        @param colors: Color scheme
        @return SVG content
        """
        # Enhanced Apple logo with more details and better design
        apple_body = colors["primary"]  # Main apple body
        apple_leaf = colors["accent"]  # Leaf (green-ish)
        apple_highlight = colors["white"]  # Highlight
        bite_color = colors["background"]  # Bite mark (background color)
        apple_stem = colors["dark"]  # Stem
        apple_shadow = colors["background"]  # Shadow effects

        return f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <!-- Apple Logo - macOS (Enhanced) -->
            <!-- Apple body with better shape and gradient effect -->
            <path d="M 12 20.5 C 8.5 20.5 6.5 17.5 6.5 14.5 C 6.5 11.5 8.5 9.5 12 9.5 C 12.8 9.5 13.5 9.7 14.2 10 C 14.5 9.7 15 9.5 15.5 9.5 C 18.5 9.5 20.5 11.5 20.5 14.5 C 20.5 17.5 18.5 20.5 15.5 20.5 C 14.8 20.5 14.2 20.3 13.5 20 C 13.2 20.3 12.8 20.5 12 20.5 Z" fill="{apple_body}"/>

            <!-- Apple highlight with better positioning -->
            <ellipse cx="11.5" cy="12.5" rx="2" ry="4" fill="{apple_highlight}" opacity="0.4"/>
            <ellipse cx="13" cy="14" rx="1" ry="2" fill="{apple_highlight}" opacity="0.6"/>

            <!-- Enhanced leaf with better shape and stem -->
            <ellipse cx="15" cy="7.5" rx="1.8" ry="3" fill="{apple_leaf}" transform="rotate(35 15 7.5)"/>
            <!-- Leaf vein -->
            <path d="M 14.2 7.5 Q 15 5.5 15.8 7.5" stroke="{colors["dark"]}" stroke-width="0.4" fill="none"/>
            <!-- Leaf highlight -->
            <ellipse cx="14.8" cy="6.8" rx="0.8" ry="1.5" fill="{apple_highlight}" opacity="0.3" transform="rotate(35 14.8 6.8)"/>

            <!-- Apple stem -->
            <rect x="13.2" y="8.5" width="0.6" height="1.5" fill="{apple_stem}" rx="0.3"/>
            <ellipse cx="13.5" cy="8.3" rx="0.4" ry="0.3" fill="{apple_highlight}" opacity="0.5"/>

            <!-- Enhanced bite mark with better shape -->
            <path d="M 16.5 13.5 C 17 13 17.5 13.5 17.5 14.5 C 17.5 15.5 17 16 16.5 16.5 C 16 17 15.5 16.5 15.5 15.5 C 15.5 14.5 16 14 16.5 13.5 Z" fill="{bite_color}"/>

            <!-- Bite mark shadow -->
            <path d="M 16.7 13.7 C 17.1 13.3 17.3 13.7 17.3 14.5 C 17.3 15.3 17.1 15.7 16.7 16.1 C 16.3 16.5 15.9 16.1 15.9 15.3 C 15.9 14.5 16.3 14.1 16.7 13.7 Z" fill="{colors["dark"]}" opacity="0.2"/>

            <!-- Apple body shadow for depth -->
            <ellipse cx="12.5" cy="15" rx="5" ry="4" fill="{apple_shadow}" opacity="0.15"/>
        </svg>"""

    def _windows_logo(self, size: int, colors: dict[str, str]) -> str:
        """
        @brief Generate Windows logo - Enhanced version
        @param size: Icon size
        @param colors: Color scheme
        @return SVG content
        """
        # Enhanced Windows logo with better design and effects
        blue_pane = colors["primary"]  # Top-left (blue)
        green_pane = colors["accent"]  # Top-right (green)
        yellow_pane = colors["orange"]  # Bottom-left (yellow/orange)
        red_pane = colors["secondary"]  # Bottom-right (red)
        pane_highlight = colors["highlight"]  # Pane highlights
        pane_shadow = colors["background"]  # Pane shadows

        return f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <!-- Windows Logo - Classic Four Panes (Enhanced) -->
            <!-- Top-left pane (blue) with depth -->
            <rect x="4.5" y="4.5" width="7" height="7" fill="{blue_pane}"/>
            <rect x="5" y="5" width="6" height="6" fill="{pane_highlight}" opacity="0.2"/>
            <rect x="5.5" y="5.5" width="5" height="5" fill="{blue_pane}" opacity="0.1"/>

            <!-- Top-right pane (green) with depth -->
            <rect x="12.5" y="4.5" width="7" height="7" fill="{green_pane}"/>
            <rect x="13" y="5" width="6" height="6" fill="{pane_highlight}" opacity="0.2"/>
            <rect x="13.5" y="5.5" width="5" height="5" fill="{green_pane}" opacity="0.1"/>

            <!-- Bottom-left pane (yellow) with depth -->
            <rect x="4.5" y="12.5" width="7" height="7" fill="{yellow_pane}"/>
            <rect x="5" y="13" width="6" height="6" fill="{pane_highlight}" opacity="0.2"/>
            <rect x="5.5" y="13.5" width="5" height="5" fill="{yellow_pane}" opacity="0.1"/>

            <!-- Bottom-right pane (red) with depth -->
            <rect x="12.5" y="12.5" width="7" height="7" fill="{red_pane}"/>
            <rect x="13" y="13" width="6" height="6" fill="{pane_highlight}" opacity="0.2"/>
            <rect x="13.5" y="13.5" width="5" height="5" fill="{red_pane}" opacity="0.1"/>

            <!-- Enhanced borders with better definition -->
            <rect x="4.5" y="4.5" width="15" height="15" fill="none" stroke="{colors["dark"]}" stroke-width="0.5"/>
            <line x1="11.5" y1="4.5" x2="11.5" y2="19.5" stroke="{colors["dark"]}" stroke-width="0.5"/>
            <line x1="4.5" y1="11.5" x2="19.5" y2="11.5" stroke="{colors["dark"]}" stroke-width="0.5"/>

            <!-- Subtle inner shadows for depth -->
            <rect x="5" y="5" width="14" height="14" fill="none" stroke="{pane_shadow}" stroke-width="0.3" opacity="0.3"/>
            <line x1="11.8" y1="5" x2="11.8" y2="19" stroke="{pane_shadow}" stroke-width="0.2" opacity="0.3"/>
            <line x1="5" y1="11.8" x2="19" y2="11.8" stroke="{pane_shadow}" stroke-width="0.2" opacity="0.3"/>

            <!-- Windows logo "W" pattern overlay -->
            <path d="M 6 7 L 7.5 10 L 9 7 M 9 7 L 10.5 10 L 12 7" stroke="{pane_highlight}" stroke-width="0.8" fill="none" opacity="0.4"/>
            <path d="M 14 7 L 15.5 10 L 17 7 M 17 7 L 18.5 10 L 20 7" stroke="{pane_highlight}" stroke-width="0.8" fill="none" opacity="0.4"/>
            <path d="M 6 15 L 7.5 18 L 9 15 M 9 15 L 10.5 18 L 12 15" stroke="{pane_highlight}" stroke-width="0.8" fill="none" opacity="0.4"/>
            <path d="M 14 15 L 15.5 18 L 17 15 M 17 15 L 18.5 18 L 20 15" stroke="{pane_highlight}" stroke-width="0.8" fill="none" opacity="0.4"/>
        </svg>"""

    def _generic_computer(self, size: int, colors: dict[str, str]) -> str:
        """
        @brief Generate generic computer icon fallback - Enhanced version
        @param size: Icon size
        @param colors: Color scheme
        @return SVG content
        """
        # Enhanced generic computer with more details and better design
        monitor_frame = colors["dark"]  # Monitor frame (dark)
        monitor_screen = colors["primary"]  # Screen (main color)
        screen_glow = colors["accent"]  # Screen glow/activity
        stand_color = colors["secondary"]  # Monitor stand
        base_color = colors["highlight"]  # Base
        keyboard_color = colors["background"]  # Keyboard
        screen_highlight = colors["white"]  # Screen highlights

        return f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <!-- Generic Computer Monitor (Enhanced) -->
            <!-- Monitor frame with better design -->
            <rect x="3" y="5" width="18" height="12" rx="1.5" fill="{monitor_frame}"/>
            <rect x="3.5" y="5.5" width="17" height="11" rx="1" fill="{monitor_frame}" opacity="0.8"/>

            <!-- Screen with better design -->
            <rect x="4" y="6" width="16" height="10" fill="{monitor_screen}"/>

            <!-- Enhanced screen activity/glow with more detail -->
            <rect x="5" y="7" width="14" height="1.5" fill="{screen_glow}" opacity="0.7"/>
            <rect x="5" y="9" width="10" height="1" fill="{screen_glow}" opacity="0.5"/>
            <rect x="5" y="10.5" width="8" height="0.8" fill="{screen_glow}" opacity="0.4"/>
            <rect x="5" y="12" width="6" height="0.6" fill="{screen_glow}" opacity="0.3"/>
            <rect x="5" y="13" width="4" height="0.5" fill="{screen_glow}" opacity="0.2"/>

            <!-- Screen highlights for glass effect -->
            <rect x="4.5" y="6.5" width="15" height="2" fill="{screen_highlight}" opacity="0.2"/>
            <ellipse cx="12" cy="8" rx="8" ry="1" fill="{screen_highlight}" opacity="0.1"/>

            <!-- Monitor stand with better design -->
            <rect x="10.5" y="17" width="3" height="2" fill="{stand_color}" rx="0.5"/>
            <rect x="9.5" y="18.5" width="5" height="1.5" fill="{stand_color}" rx="0.3"/>

            <!-- Base with better design -->
            <ellipse cx="12" cy="19.5" rx="5" ry="0.8" fill="{base_color}"/>

            <!-- Keyboard -->
            <rect x="6" y="20.5" width="12" height="2" rx="0.5" fill="{keyboard_color}"/>
            <rect x="6.5" y="21" width="11" height="1" rx="0.3" fill="{colors["dark"]}" opacity="0.3"/>
            <!-- Keyboard keys -->
            <rect x="7" y="21.2" width="0.8" height="0.6" fill="{colors["dark"]}" opacity="0.5"/>
            <rect x="8" y="21.2" width="0.8" height="0.6" fill="{colors["dark"]}" opacity="0.5"/>
            <rect x="9" y="21.2" width="0.8" height="0.6" fill="{colors["dark"]}" opacity="0.5"/>
            <rect x="10.5" y="21.2" width="3" height="0.6" fill="{colors["dark"]}" opacity="0.5"/>
            <rect x="14" y="21.2" width="0.8" height="0.6" fill="{colors["dark"]}" opacity="0.5"/>
            <rect x="15" y="21.2" width="0.8" height="0.6" fill="{colors["dark"]}" opacity="0.5"/>
            <rect x="16" y="21.2" width="0.8" height="0.6" fill="{colors["dark"]}" opacity="0.5"/>

            <!-- Power indicator with glow -->
            <circle cx="19" cy="14" r="0.6" fill="{colors["orange"]}"/>
            <circle cx="19" cy="14" r="0.8" fill="{colors["orange"]}" opacity="0.3"/>

            <!-- Screen reflection/glare -->
            <polygon points="4,6 8,6 6,10 4,10" fill="{screen_highlight}" opacity="0.15"/>
        </svg>"""


# Global platform detection instances
_platform_info: PlatformInfo | None = None
_platform_config: PlatformConfig | None = None


def get_platform_info() -> PlatformInfo:
    """
    @brief Get the global platform information instance
    @return Singleton PlatformInfo instance
    """
    global _platform_info
    if _platform_info is None:
        _platform_info = PlatformInfo()
    return _platform_info


def get_platform_config() -> PlatformConfig:
    """
    @brief Get the global platform configuration instance
    @return Singleton PlatformConfig instance
    """
    global _platform_config
    if _platform_config is None:
        _platform_config = PlatformConfig(get_platform_info())
    return _platform_config


def get_platform_mascot_icon(color_manager: Any = None, size: int = 24) -> str:
    """
    @brief Get the platform-specific mascot icon for the current system
    @param color_manager: Optional color manager for theming
    @param size: Icon size in pixels
    @return SVG content as string
    """
    generator = PlatformMascotGenerator(color_manager)
    return generator.get_platform_mascot(size)


# Maintain backward compatibility
__all__ = [
    "PlatformConfig",
    "PlatformInfo",
    "PlatformMascotGenerator",
    "get_platform_config",
    "get_platform_info",
    "get_platform_mascot_icon",
]
