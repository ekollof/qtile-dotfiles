#!/usr/bin/env python3
"""
Platform detection and configuration utilities for qtile
Provides cross-platform compatibility between Linux and BSD systems
"""

import platform
import shutil
import subprocess
from typing import Any


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

    def get_system_info(self) -> dict[str, str]:
        """
        @brief Get comprehensive system information
        @return Dictionary containing system details
        """
        return {
            "system": self._system,
            "release": self._release,
            "machine": self._machine,
            "python_version": platform.python_version(),
            "hostname": platform.node(),
        }


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
                "clipboard_manager": "clipmenu",
                "screenshot": "flameshot gui",
                "audio_mixer": "pavucontrol",
                "network_manager": "nm-connection-editor",
            },
            "openbsd": {
                "lock_session": "xlock",
                "clipboard_manager": "xclip",
                "screenshot": "xwd | xwdtopnm | pnmtopng",
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

    def get_application(
        self, app_type: str, fallback: str | None = None
    ) -> str:
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
                        self._application_preferences[app_type].get(
                            "openbsd", []
                        ),
                    )
                case "linux":
                    preferences = self._application_preferences[app_type][
                        "linux"
                    ]
                case _:
                    preferences = self._application_preferences[app_type].get(
                        system,
                        self._application_preferences[app_type].get(
                            "linux", []
                        ),
                    )

            app = self.platform.get_preferred_application(
                app_type, preferences
            )
            if app:
                return app

        # If no preferred app found, return fallback or default
        return fallback or "xterm"

    def get_command(
        self, command_type: str, fallback: str | None = None
    ) -> str:
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
                command = self._config_overrides.get("linux", {}).get(
                    command_type
                )
            case "openbsd":
                command = self._config_overrides.get("openbsd", {}).get(
                    command_type
                )
            case "freebsd":
                command = self._config_overrides.get("freebsd", {}).get(
                    command_type
                )
            case "netbsd":
                command = self._config_overrides.get("netbsd", {}).get(
                    command_type
                )
            case _:
                command = self._config_overrides.get(system, {}).get(
                    command_type
                )

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


def detect_desktop_environment() -> str | None:
    """
    @brief Detect the current desktop environment
    @return Desktop environment name or None if not detected
    """
    import os

    # Check common environment variables
    desktop_vars = [
        "XDG_CURRENT_DESKTOP",
        "DESKTOP_SESSION",
        "GNOME_DESKTOP_SESSION_ID",
        "KDE_FULL_SESSION",
    ]

    for var in desktop_vars:
        value = os.environ.get(var)
        if value:
            return value.lower()

    # Check for specific desktop processes
    platform_info = get_platform_info()

    desktop_processes = {
        "gnome": "gnome-session",
        "kde": "kwin",
        "xfce": "xfce4-session",
        "lxde": "lxsession",
        "mate": "mate-session",
    }

    for desktop, process in desktop_processes.items():
        if platform_info.has_command("pgrep"):
            try:
                result = subprocess.run(
                    ["pgrep", "-f", process], capture_output=True, timeout=2
                )
                if result.returncode == 0:
                    return desktop
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue

    return None
