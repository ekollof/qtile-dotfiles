#!/usr/bin/env python3
"""
Centralized configuration for qtile
All user-configurable settings in one place
"""

import os


class QtileConfig:
    """Centralized qtile configuration"""

    home: str
    
    def __init__(self):
        self.home = os.path.expanduser("~")

    # ===== CORE SETTINGS =====

    @property
    def mod_key(self) -> str:
        """Primary modifier key (Super/Windows key)"""
        return "mod4"

    @property
    def alt_key(self) -> str:
        """Alt modifier key"""
        return "mod1"

    @property
    def terminal(self) -> str:
        """Default terminal emulator"""
        return "st"

    @property
    def browser(self) -> str:
        """Default web browser"""
        return "brave"

    # ===== APPLICATION COMMANDS =====

    @property
    def applications(self) -> dict[str, str]:
        """Application launch commands"""
        return {
            'launcher': 'rofi -show run',
            'password_manager': f'{self.home}/bin/getpass',
            'totp_manager': f'{self.home}/bin/getpass --totp',
            'clipboard': 'clipmenu',
            'wallpaper_picker': f'{self.home}/bin/pickwall.sh',
            'wallpaper_random': f'{self.home}/bin/wallpaper.ksh -r',
            'lock_session': 'loginctl lock-session',
        }

    # ===== LAYOUT SETTINGS =====

    @property
    def layout_defaults(self) -> dict[str, int | bool]:
        """Default settings for all layouts"""
        return {
            'margin': 4,  # Gap between windows
            'border_width': 1,
            'single_border_width': 1,
            'single_margin': 4,
        }

    @property
    def tile_layout(self) -> dict[str, float | int | bool | None]:
        """Tile layout specific settings"""
        return {
            'ratio': 0.5,  # 50/50 split by default
            'ratio_increment': 0.1,  # 10% resize increments
            'master_match': None,
            'expand': True,
            'master_length': 1,
            'shift_windows': True,
        }

    @property
    def monad_tall_layout(self) -> dict[str, float | int | str]:
        """MonadTall layout specific settings"""
        return {
            'ratio': 0.6,  # Main window 60% width
            'min_ratio': 0.25,
            'max_ratio': 0.85,
            'change_ratio': 0.05,  # 5% change increments
            'change_size': 20,
            'new_client_position': 'after_current',
        }

    @property
    def bsp_layout(self) -> dict[str, bool | int | float]:
        """BSP layout specific settings"""
        return {
            'fair': True,  # Even space distribution
            'grow_amount': 10,
            'lower_right': True,
            'ratio': 1.6,  # Golden ratio
        }

    # ===== FLOATING WINDOW RULES =====

    @property
    def floating_rules(self) -> list[dict[str, str]]:
        """Windows that should float"""
        return [
            # Core system dialogs
            {'wm_class': 'confirm'},
            {'wm_class': 'download'},
            {'wm_class': 'error'},
            {'wm_class': 'file_progress'},
            {'wm_class': 'notification'},
            {'wm_class': 'splash'},
            {'wm_class': 'toolbar'},

            # PIN entry and authentication
            {'wm_class': 'pinentry-gtk-2'},
            {'wm_class': 'pinentry'},
            {'title': 'pinentry'},
            {'wm_class': 'ssh-askpass'},

            # Git tools (gitk)
            {'wm_class': 'confirmreset'},
            {'wm_class': 'makebranch'},
            {'wm_class': 'maketag'},
            {'title': 'branchdialog'},

            # Desktop environment
            {'wm_class': 'krunner'},
            {'title': 'Desktop — Plasma'},

            # Calculators and small tools
            {'wm_class': 'gnome-calculator'},
            {'wm_class': 'kcalc'},
            {'wm_class': 'Galculator'},
            {'wm_class': 'Gnome-calculator'},

            # Screenshot tools
            {'wm_class': 'flameshot'},
            {'wm_class': 'spectacle'},
            {'wm_class': 'org.kde.spectacle'},
            {'wm_class': 'Xfce4-screenshooter'},

            # System utilities
            {'wm_class': 'Gpick'},  # Color picker
            {'wm_class': 'Arandr'},  # Display configuration
            {'wm_class': 'Pavucontrol'},  # Audio control
            {'wm_class': 'Nm-connection-editor'},  # Network manager
            {'wm_class': 'Blueman-manager'},  # Bluetooth manager
        ]

    @property
    def force_floating_apps(self) -> list[str]:
        """Apps that should always float (via hooks)"""
        return [
            'nm-connection-editor',    # NetworkManager GUI
            'pavucontrol',            # PulseAudio volume control
            'origin.exe',             # Origin game launcher
            'steam',                  # Steam client (some windows)
            'blueman-manager',        # Bluetooth manager
            'arandr',                # Display settings
            'lxappearance',          # Theme settings
            'qt5ct',                 # Qt5 configuration
            'kvantummanager',        # Kvantum theme manager
        ]

    # ===== WORKSPACE/GROUP SETTINGS =====

    @property
    def groups(self) -> list[tuple[str, dict[str, str]]]:
        """Workspace groups configuration"""
        return [
            ('1:chat', {'layout': 'max'}),
            ('2:web', {'layout': 'tile'}),
            ('3:shell', {'layout': 'tile'}),
            ('4:work', {'layout': 'tile'}),
            ('5:games', {'layout': 'tile'}),
            ('6:dev', {'layout': 'tile'}),
            ('7:mail', {'layout': 'tile'}),
            ('8:misc', {'layout': 'tile'}),
            ('9:doc', {'layout': 'tile'}),
        ]

    @property
    def scratchpads(self) -> list[dict[str, str | float | int]]:
        """Scratchpad dropdown configurations"""
        return [
            {
                'name': 'notepad',
                'command': 'st -e nvim /tmp/notepad.md',
                'width': 0.6,
                'height': 0.6,
                'x': 0.2,
                'y': 0.2,
                'opacity': 0.9,
            },
            {
                'name': 'ncmpcpp',
                'command': 'st -e ncmpcpp',
                'width': 0.8,
                'height': 0.8,
                'x': 0.1,
                'y': 0.1,
                'opacity': 0.9,
            },
        ]

    # ===== COLOR MANAGEMENT =====

    @property
    def color_files(self) -> dict[str, str]:
        """Color file paths"""
        cache_dir = f"{self.home}/.cache/wal"
        return {
            'current': f"{cache_dir}/colors.json",
            'backup': f"{cache_dir}/last_good_colors.json",
            'backup_dir': f"{cache_dir}/backups",
        }

    @property
    def default_colors(self) -> dict[str, dict[str, str]]:
        """Fallback colors when pywal files are unavailable"""
        return {
            "special": {
                "background": "#171616",
                "foreground": "#EEE6EA",
                "cursor": "#EEE6EA"
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
                "color15": "#EEE6EA"
            }
        }

    # ===== MONITOR/SCREEN SETTINGS =====

    @property
    def screen_settings(self) -> dict[str, int | bool]:
        """Screen detection and configuration"""
        return {
            'startup_delay': 30,  # Seconds to wait before handling screen changes
            'detection_delay': 2,  # Seconds to wait after screen change detection
            'auto_restart_on_change': True,  # Restart qtile when screens change
        }

    # ===== AUTOSTART SETTINGS =====

    @property
    def autostart_script(self) -> str:
        """Path to autostart script"""
        return f"{self.home}/.config/qtile/autostart.sh"

    # ===== BAR/WIDGET SETTINGS =====

    @property
    def bar_settings(self) -> dict[str, int | float | list[int]]:
        """Status bar configuration"""
        return {
            'height': 28,
            'opacity': 0.95,
            'margin': [0, 0, 0, 0],  # top, right, bottom, left
        }

    @property
    def widget_defaults(self) -> dict[str, str | int]:
        """Default widget settings"""
        return {
            'font': 'BerkeleyMono Nerd Font Mono',
            'fontsize': 12,
            'padding': 3,
        }

    # ===== HOTKEY DISPLAY SETTINGS =====

    @property
    def hotkey_display(self) -> dict[str, int | float | str]:
        """Hotkey display configuration"""
        return {
            'rofi_width': 1200,
            'rofi_lines': 25,
            'dmenu_lines': 25,
            'font': 'BerkeleyMono Nerd Font Mono',
            'transparency': 0.95,
        }


# Create global config instance
config = QtileConfig()


def get_config() -> QtileConfig:
    """Get the global configuration instance"""
    return config
