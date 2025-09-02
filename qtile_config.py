#!/usr/bin/env python3
"""
Centralized configuration for qtile - DPI AWARE VERSION

@brief Centralized qtile configuration with automatic DPI scaling support
@author qtile configuration system

All user-conf            "wallpaper_picker": f"{self.home}/bin/pick            "wallpaper_picker": f"{self.home}/bin/pickwall.sh",
            "wallpaper_random": f"{self.home}/bin/wallpaper.ksh -r",
            "lock_session": self.platform_config.get_command(l.sh",
            "wallpaper_random": f"{self.home}/bin/wallpaper.ksh -r",rable settings in one place with automatic DPI scaling.
Provides platform-aware defaults, font management, and cross-platform
compatibility for both X11 and Wayland environments.

Key features:
- Automatic DPI detection and scaling
- Platform-specific defaults
- Font fallback management
- Cross-platform portability
"""

from pathlib import Path
from typing import Any

from modules.dpi_utils import get_dpi_manager, scale_font, scale_size
from modules.font_utils import get_available_font
from modules.platform import get_platform_config, get_platform_info


class QtileConfig:
    """
    @brief Centralized qtile configuration with DPI awareness

    Provides all configuration settings for qtile with automatic DPI scaling,
    platform detection, and intelligent defaults. Manages fonts, applications,
    layouts, and system-specific preferences.

    Complex operation for comprehensive qtile configuration management.
    """

    home: str

    def __init__(self):
        self.home = str(Path.home())
        self.dpi_manager = get_dpi_manager()
        self.platform_info = get_platform_info()
        self.platform_config = get_platform_config()
        
        # Fix PATH for spawned processes to include user directories
        self._setup_environment()
        
    def _setup_environment(self):
        """Setup environment variables for spawned processes by sourcing ~/.profile"""
        import os
        import subprocess
        
        profile_path = f"{self.home}/.profile"
        
        # Check if ~/.profile exists
        if os.path.exists(profile_path):
            try:
                # Find an appropriate shell to source the profile
                shell_cmd = self._find_suitable_shell()
                if not shell_cmd:
                    # No suitable shell found, use fallback
                    self._setup_path_fallback()
                    return
                
                # Source ~/.profile and capture the resulting environment
                # This mimics what shells do when they start
                source_cmd = self._get_source_command(shell_cmd, profile_path)
                
                result = subprocess.run(
                    source_cmd,
                    capture_output=True,
                    text=True,
                    timeout=5  # Prevent hanging
                )
                
                if result.returncode == 0:
                    # Parse the environment output and update os.environ
                    for line in result.stdout.strip().split('\n'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key] = value
                else:
                    # Sourcing failed, use fallback
                    self._setup_path_fallback()
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                # If sourcing fails, fall back to manual PATH setup
                self._setup_path_fallback()
        else:
            # No ~/.profile, use fallback
            self._setup_path_fallback()
    
    def _find_suitable_shell(self) -> str | None:
        """Find a suitable shell for sourcing environment files"""
        import shutil
        
        # Preferred shells in order of preference
        shell_candidates = [
            'bash',      # Most common and feature-rich
            'zsh',       # Modern alternative to bash
            'ksh',       # Available on most Unix systems
            'dash',      # Debian/Ubuntu default sh
            'sh',        # POSIX shell (always available)
        ]
        
        # Try to find the first available shell
        for shell in shell_candidates:
            shell_path = shutil.which(shell)
            if shell_path:
                return shell_path
        
        # Last resort: try common shell paths
        fallback_paths = [
            '/bin/bash',
            '/usr/bin/bash',
            '/usr/local/bin/bash',
            '/bin/sh',
            '/usr/bin/sh',
        ]
        
        import os
        for path in fallback_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
        
        return None
    
    def _get_source_command(self, shell_path: str, profile_path: str) -> list[str]:
        """Get the appropriate source command for the given shell"""
        import os
        
        shell_name = os.path.basename(shell_path)
        
        # Different shells have different syntax for sourcing files
        if shell_name in ['bash', 'zsh', 'ksh']:
            # These shells support the 'source' command
            return [shell_path, '-c', f'source "{profile_path}" && env']
        elif shell_name in ['dash', 'sh']:
            # POSIX shells use '.' instead of 'source'
            return [shell_path, '-c', f'. "{profile_path}" && env']
        else:
            # Default to POSIX syntax for unknown shells
            return [shell_path, '-c', f'. "{profile_path}" && env']
    
    def _setup_path_fallback(self):
        """Fallback PATH setup if ~/.profile sourcing fails"""
        import os
        
        user_paths = [
            f"{self.home}/bin",
            f"{self.home}/.local/bin"
        ]
        
        current_path = os.environ.get('PATH', '')
        path_entries = current_path.split(':')
        
        for user_path in user_paths:
            if user_path not in path_entries:
                current_path = f"{user_path}:{current_path}"
        
        os.environ['PATH'] = current_path

    # ===== FONT SETTINGS =====
    #
    # 🎯 TO CHANGE FONT SIZES: Simply modify the return values below!
    # - preferred_fontsize: Controls text size (widgets, window titles, etc.)
    # - preferred_icon_fontsize: Controls icon/symbol size (usually larger)
    #
    # Both values are automatically scaled for high-DPI displays.
    # After changes, restart qtile with Super+Ctrl+R

    @property
    def preferred_font(self) -> str:
        """
        @brief User's preferred font - change this to your preferred font
        @return Font name string for use in qtile widgets
        @example To use JetBrains Mono: return "JetBrains Mono Nerd Font"
        """
        return "BerkeleyMono Nerd Font Mono"

    @property
    def preferred_fontsize(self) -> int:
        """
        @brief User's preferred base font size (before DPI scaling)
        @return Base font size in points
        @note This will be automatically scaled for high-DPI displays
        @example For larger text, change to: return 14
        @example For smaller text, change to: return 10
        """
        return 16  # 🔧 CHANGE THIS VALUE to adjust font size

    @property
    def preferred_icon_fontsize(self) -> int:
        """
        @brief User's preferred icon font size (before DPI scaling)
        @return Base icon font size in points
        @note Icons may need larger fonts for better visibility
        @example For larger icons, change to: return 18
        @example For smaller icons, change to: return 14
        """
        return 20  # 🔧 CHANGE THIS VALUE to adjust icon font size

    @property
    def preferred_bar_height(self) -> int:
        """
        @brief User's preferred bar height (before DPI scaling)
        @return Base bar height in pixels
        @note This will be automatically scaled for high-DPI displays
        @example For taller bar, change to: return 32
        @example For shorter bar, change to: return 24
        """
        return 32  # 🔧 CHANGE THIS VALUE to adjust bar height

    # ===== DPI SETTINGS =====

    @property
    def dpi_info(self) -> dict[str, Any]:
        """
        @brief Get DPI scaling information from the DPI manager
        @return Dictionary containing DPI scaling details and recommendations
        """
        return self.dpi_manager.get_scaling_info()

    # ===== SCRIPT WIDGET SETTINGS =====

    @property
    def script_configs(self) -> list[dict[str, Any]]:
        """
        @brief Configure custom scripts for GenPollText widgets with DPI awareness

        Complex operation for comprehensive script widget configuration.
        @return List of dictionaries containing script configuration parameters
        """
        return [
            {
                "script_path": "~/bin/imap-checker.ksh",
                "icon": "📭:",
                "update_interval": 300,
                "fallback": "N/A",
                "name": "email checker",
            },
            {
                "script_path": "~/bin/kayako.sh",
                "icon": "🎫:",
                "update_interval": 60,
                "fallback": "N/A",
                "name": "ticket checker",
            },
            {
                "script_path": "~/bin/cputemp",
                "icon": "🌡:",
                "update_interval": 10,
                "fallback": "N/A",
                "name": "CPU temperature",
            },
        ]

    @property
    def mouse_warp_focus(self) -> bool:
        """
        @brief Enable mouse warping when changing window focus

        When True, the mouse cursor automatically moves to the center of the
        newly focused window when using Super+hjkl navigation keys.
        When False, focus changes without moving the mouse cursor.

        @return Boolean indicating whether mouse warping is enabled
        """
        return True

    # ===== CORE SETTINGS =====

    @property
    def mod_key(self) -> str:
        """
        @brief Primary modifier key (Super/Windows key)
        @return String representing the primary modifier key
        """
        return "mod4"

    @property
    def alt_key(self) -> str:
        """
        @brief Alt modifier key
        @return String representing the alt modifier key
        """
        return "mod1"

    @property
    def terminal(self) -> str:
        """
        @brief Default terminal emulator - platform aware
        @return Terminal command string based on platform configuration
        """
        return self.platform_config.get_application("terminal", "st")

    @property
    def browser(self) -> str:
        """
        @brief Default web browser - platform aware
        @return Browser command string based on platform configuration
        """
        return self.platform_config.get_application("browser", "brave")

    # ===== APPLICATION COMMANDS =====

    @property
    def applications(self) -> dict[str, str]:
        """
        @brief Application launch commands - platform aware
        @return Dictionary mapping application types to launch commands
        """
        launcher_app = self.platform_config.get_application("launcher", "rofi")
        launcher_cmd = (
            f"{launcher_app} -show run" if launcher_app == "rofi" else launcher_app
        )

        return {
            "launcher": launcher_cmd,
            "password_manager": f"{self.home}/bin/getpass",
            "totp_manager": f"{self.home}/bin/getpass --totp",
            "clipboard": self.platform_config.get_command(
                "clipboard_manager", "clipmenu"
            ),
            "wallpaper_picker": f"{self.home}/bin/pickwall.sh",
           "wallpaper_random": f"{self.home}/bin/wallpaper.ksh -r",
            "lock_session": self.platform_config.get_command(
                "lock_session", "loginctl lock-session"
            ),
            "screenshot": self.platform_config.get_command(
                "screenshot", "flameshot gui"
            ),
            "audio_mixer": self.platform_config.get_command(
                "audio_mixer", "pavucontrol"
            ),
            "network_manager": self.platform_config.get_command(
                "network_manager", "nm-connection-editor"
            ),
            "file_manager": self.platform_config.get_application("file_managerthunar"),
            "media_player": self.platform_config.get_application("media_player", "mpv"),
        }

    # ===== LAYOUT SETTINGS - DPI AWARE =====

    @property
    def layout_defaults(self) -> dict[str, int | bool]:
        """
        @brief Default settings for all layouts - DPI scaled
        @return Dictionary with margin, border_width, and other layout settings
        """
        return {
            "margin": scale_size(4),  # DPI-scaled gap between windows
            "border_width": max(1, scale_size(1)),  # Minimum 1px border
            "single_border_width": max(1, scale_size(1)),
            "single_margin": scale_size(4),
        }

    @property
    def tile_layout(
        self,
    ) -> dict[str, float | int | bool | None]:  # Complex operation
        """
        @brief Tile layout specific settings - DPI aware
        @return Dictionary with ratio, increment, and tiling configuration
        """
        return {
            "ratio": 0.5,  # 50/50 split by default
            "ratio_increment": 0.1,  # 10% resize increments
            "master_match": None,
            "expand": True,
            "master_length": 1,
            "shift_windows": True,
        }

    @property
    def monad_tall_layout(self) -> dict[str, int | float | str]:
        """
        @brief MonadTall layout specific settings - DPI scaled
        @return Dictionary with ratio, min_ratio, and max_ratio for MonadTall
        """
        return {
            "ratio": 0.6,  # Main window 60% width
            "min_ratio": 0.25,
            "max_ratio": 0.85,
            "change_ratio": 0.05,  # 5% change increments
            "change_size": scale_size(20),  # DPI-scaled size changes
            "new_client_position": "after_current",
        }

    @property
    def bsp_layout(self) -> dict[str, int | float]:
        """
        @brief BSP layout specific settings - DPI scaled
        @return Dictionary with ratio and fair settings for BSP layout
        """
        return {
            "fair": True,  # Even space distribution
            "grow_amount": scale_size(10),  # DPI-scaled grow amount
            "lower_right": True,
            "ratio": 1.6,  # Golden ratio
        }

    # ===== FLOATING WINDOW RULES =====

    @property
    def floating_rules(self) -> list[dict[str, str]]:
        """
        @brief Windows that should float
        @return List of rules defining which windows should be floating
        """
        return [
            # Core system dialogs
            {"wm_class": "confirm"},
            {"wm_class": "download"},
            {"wm_class": "error"},
            {"wm_class": "file_progress"},
            {"wm_class": "notification"},
            {"wm_class": "splash"},
            {"wm_class": "toolbar"},
            # PIN entry and authentication
            {"wm_class": "pinentry-gtk-2"},
            {"wm_class": "pinentry"},
            {"title": "pinentry"},
            {"wm_class": "ssh-askpass"},
            # Git tools (gitk)
            {"wm_class": "confirmreset"},
            {"wm_class": "makebranch"},
            {"wm_class": "maketag"},
            {"title": "branchdialog"},
            # Desktop environment
            {"wm_class": "krunner"},
            {"title": "Desktop — Plasma"},
            # Calculators and small tools
            {"wm_class": "gnome-calculator"},
            {"wm_class": "kcalc"},
            {"wm_class": "Galculator"},
            {"wm_class": "Gnome-calculator"},
            # Screenshot tools
            {"wm_class": "flameshot"},
            {"wm_class": "spectacle"},
            {"wm_class": "org.kde.spectacle"},
            {"wm_class": "Xfce4-screenshooter"},
            # System utilities
            {"wm_class": "Gpick"},  # Color picker
            {"wm_class": "Arandr"},  # Display configuration
            {"wm_class": "Pavucontrol"},  # Audio control
            {"wm_class": "Nm-connection-editor"},  # Network manager
            {"wm_class": "Blueman-manager"},  # Bluetooth manager
        ]

    @property
    def force_floating_apps(self) -> list[str]:
        """
        @brief Apps that should always float (via hooks)
        @return List of application names that should be forced to float
        """
        return [
            "nm-connection-editor",  # NetworkManager GUI
            "pavucontrol",  # PulseAudio volume control
            "origin.exe",  # Origin game launcher
            "steam",  # Steam client (some windows)
            "blueman-manager",  # Bluetooth manager
            "arandr",  # Display settings
            "lxappearance",  # Theme settings
            "qt5ct",  # Qt5 configuration
            "kvantummanager",  # Kvantum theme manager
        ]

    # ===== WORKSPACE/GROUP SETTINGS =====

    @property
    def groups(self) -> list[tuple[str, dict[str, str]]]:
        """
        @brief Workspace groups configuration
        @return List of tuples containing group names and layout settings
        """
        return [
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

    @property
    def scratchpads(self) -> list[dict[str, str | float | int]]:
        """
        @brief Scratchpad dropdown configurations
        @return List of dictionaries containing scratchpad settings
        """
        return [
            {
                "name": "notepad",
                "command": "st -e nvim /tmp/notepad.md",
                "width": 0.6,
                "height": 0.6,
                "x": 0.2,
                "y": 0.2,
                "opacity": 0.9,
            },
            {
                "name": "ncmpcpp",
                "command": "st -e ncmpcpp",
                "width": 0.8,
                "height": 0.8,
                "x": 0.1,
                "y": 0.1,
                "opacity": 0.9,
            },
        ]

    # ===== COLOR MANAGEMENT =====

    @property
    def color_files(self) -> dict[str, str]:
        """
        @brief Color file paths
        @return Dictionary mapping color file types to their paths
        """
        cache_dir = f"{self.home}/.cache/wal"
        return {
            "current": f"{cache_dir}/colors.json",
            "backup": f"{cache_dir}/last_good_colors.json",
            "backup_dir": f"{cache_dir}/backups",
        }

    @property
    def default_colors(self) -> dict[str, dict[str, str]]:
        """
        @brief Fallback colors when pywal files are unavailable
        @return Dictionary with special and colors sections for default theme
        """
        return {
            "special": {
                "background": "#171616",
                "foreground": "#EEE6EA",
                "cursor": "#EEE6EA",
            },
            "colors": {
                "color0": "#171616",
                "color1": "#B0607C",
                "color2": "#739F63",
                "color3": "#D19A66",
                "color4": "#7AA2F7",
                "color5": "#C678DD",
                "color6": "#56B6C2",
                "color7": "#EEE6EA",
                "color8": "#28221F",
                "color9": "#B0607C",
                "color10": "#739F63",
                "color11": "#D19A66",
                "color12": "#7AA2F7",
                "color13": "#C678DD",
                "color14": "#56B6C2",
                "color15": "#EEE6EA",
            },
        }

    # ===== MONITOR/SCREEN SETTINGS =====

    @property
    def screen_settings(self) -> dict[str, int | bool]:
        """
        @brief Screen detection and configuration
        @return Dictionary with timing and behavior settings for screen changes
        """
        return {
            "startup_delay": 30,  # Seconds to wait before handling screen changes
            "detection_delay": 2,  # Seconds to wait after screen change detection
            "auto_restart_on_change": True,  # Restart qtile when screens change
        }

    # ===== ICON SETTINGS =====

    @property
    def icon_method(self) -> str:
        """
        @brief Icon rendering method for the bar manager

        The dynamic SVG system is the only supported method:
        - "svg_dynamic": Generate icons dynamically based on system state (default and only option)

        @return Icon method string (always "svg_dynamic")
        """
        return "svg_dynamic"  # Only dynamic SVG system is supported

    @property
    def svg_icon_size(self) -> int:
        """
        @brief Base size for SVG icons before DPI scaling
        @return Icon size in pixels (will be DPI-scaled automatically)
        """
        return 24

    # ===== AUTOSTART SETTINGS =====

    @property
    def autostart_script(self) -> str:
        """
        @brief Path to autostart script
        @return String path to the autostart script file
        """
        return f"{self.home}/.config/qtile/autostart.sh"

    # ===== BAR/WIDGET SETTINGS - DPI AWARE =====

    @property
    def bar_settings(
        self,
    ) -> dict[str, int | float | list[int]]:  # Complex operation
        """
        @brief Status bar configuration - DPI scaled
        @return Dictionary with height, opacity, and margin settings
        for the status bar
        """
        return {
            "height": scale_size(
                self.preferred_bar_height
            ),  # DPI-scaled configurable bar height
            "opacity": 0.95,
            "margin": [0, 0, 0, 0],  # top, right, bottom, left
        }

    @property
    def widget_defaults(self) -> dict[str, str | int]:
        """
        @brief Default widget settings with font fallback - DPI aware
        @return Dictionary with font, fontsize, and padding settings for widgets
        """
        return {
            "font": get_available_font(self.preferred_font),
            "fontsize": scale_font(
                self.preferred_fontsize
            ),  # DPI-scaled configurable font size
            "padding": scale_size(3),  # DPI-scaled padding
        }

    # ===== NOTIFICATION SETTINGS =====

    @property
    def notification_settings(self) -> dict[str, Any]:
        """
        @brief Notification system configuration
        @return Dictionary with notification behavior and appearance settings
        """
        return {
            "enabled": True,  # Enable built-in notification system
            "default_timeout": 5000,  # Default timeout in milliseconds
            "default_timeout_low": 3000,  # Low priority timeout
            "default_timeout_urgent": 0,  # Urgent notifications never timeout
            "enable_sound": False,  # Disable notification sounds by default
            "show_in_bar": False,  # Show notifications in status bar
            "use_popups": True,  # Use standard bar notifications
            "max_notification_length": 150,  # Maximum notification text length (longer for popups)
            "enable_actions": True,  # Enable notification action buttons
            "libnotify_compatible": True,  # Enable libnotify D-Bus compatibility
        }

    # ===== HOTKEY DISPLAY SETTINGS - DPI AWARE =====

    @property
    def hotkey_display(self) -> dict[str, int | float | str]:
        """
        @brief Hotkey display configuration with font fallback - DPI aware
        @return Dictionary with rofi_width, rofi_lines, dmenu_lines, font,
                and transparency settings
        """
        return {
            "rofi_width": scale_size(1200),  # DPI-scaled width
            "rofi_lines": 25,
            "dmenu_lines": 25,
            "font": get_available_font(self.preferred_font),
            "transparency": 0.95,
        }

    # ===== BSD-SPECIFIC CONFIGURATION EXAMPLES =====

    def get_bsd_specific_overrides(self) -> dict[str, Any]:
        """
        @brief Get BSD-specific configuration overrides and examples
        @return Dictionary of BSD-specific settings and examples

        This method demonstrates how to add BSD-specific overrides
        for applications, commands, and other settings that differ
        between Linux and BSD systems.
        """
        if not self.platform_info.is_bsd:
            return {}

        bsd_overrides = {}

        # OpenBSD-specific settings
        if self.platform_info.is_openbsd:
            bsd_overrides.update(
                {
                    # OpenBSD package manager
                    "package_manager": "pkg_add",
                    "package_search": "pkg_info -Q",
                    "package_update": "syspatch && pkg_add -u",
                    # OpenBSD-specific paths
                    "browser_config_path": f"{self.home}/.mozilla",
                    "audio_device": "/dev/audio",
                    # OpenBSD system commands
                    "system_info": "sysctl hw.model hw.ncpu hw.physmem",
                    "mount_usb": "doas mount /dev/sd1i /mnt/usb",
                    "wifi_config": "doas ifconfig iwn0 scan",
                    # OpenBSD-specific hotkeys (examples)
                    "suspend_system": "doas zzz",
                    "hibernate_system": "doas ZZZ",
                }
            )

        # FreeBSD-specific settings
        elif self.platform_info.is_freebsd:
            bsd_overrides.update(
                {
                    # FreeBSD package manager
                    "package_manager": "pkg",
                    "package_search": "pkg search",
                    "package_update": "pkg update && pkg upgrade",
                    # FreeBSD-specific commands
                    "system_info": "sysctl hw.model hw.ncpu hw.physmem",
                    "mount_usb": "mount /dev/da0s1 /mnt/usb",
                    "wifi_config": "ifconfig wlan0 scan",
                }
            )

        # NetBSD-specific settings
        elif self.platform_info.is_netbsd:
            bsd_overrides.update(
                {
                    # NetBSD package manager
                    "package_manager": "pkgin",
                    "package_search": "pkgin search",
                    "package_update": "pkgin update && pkgin upgrade",
                    # NetBSD-specific commands
                    "system_info": "sysctl hw.model hw.ncpu hw.physmem64",
                    "mount_usb": "mount /dev/sd0e /mnt/usb",
                }
            )

        return bsd_overrides

    def apply_bsd_customizations(self) -> None:
        """
        @brief Apply BSD-specific customizations to the configuration

        This method shows how you can customize your qtile configuration
        for BSD systems. Call this method after initialization to apply
        BSD-specific settings.

        Complex operation for BSD-specific configuration customization.
        """
        if not self.platform_info.is_bsd:
            return

        # Get BSD-specific overrides
        bsd_config = self.get_bsd_specific_overrides()

        # Apply overrides to platform config
        for key, value in bsd_config.items():
            self.platform_config.add_override(key, value)

        # BSD-specific application overrides (examples)
        if self.platform_info.is_openbsd:
            # OpenBSD often has different default applications
            self.platform_config.add_override("text_editor", "vi")
            self.platform_config.add_override("pdf_viewer", "xpdf")
            self.platform_config.add_override("image_viewer", "xv")

        # BSD systems might need different font settings
        if self.platform_info.is_bsd:
            # Fallback to more common fonts on BSD
            self.platform_config.add_override("fallback_font", "DejaVu Sans Mono")


# Create global config instance
config = QtileConfig()

# Apply BSD-specific customizations if running on BSD
if config.platform_info.is_bsd:
    config.apply_bsd_customizations()


def get_config() -> QtileConfig:
    """
    @brief Get the global configuration instance
    @return Singleton QtileConfig instance with all user settings
    """
    return config


def get_platform_overrides() -> dict[str, str]:
    """
    @brief Get platform-specific configuration overrides
    @return Dictionary of platform-specific settings for current OS
    # Complex operation
    """
    return config.platform_config.get_config_overrides()


def is_bsd_system() -> bool:
    """
    @brief Check if running on a BSD system
    @return True if the current system is any BSD variant
    """
    return config.platform_info.is_bsd


def is_linux_system() -> bool:
    """
    @brief Check if running on a Linux system
    @return True if the current system is Linux
    """
    return config.platform_info.is_linux
