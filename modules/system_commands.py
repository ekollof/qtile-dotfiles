#!/usr/bin/env python3
"""
System-level commands for qtile
"""

import subprocess
from typing import Any

from libqtile.log_utils import logger


def run_system_command(
    commands: list[list[str]], operation: str, timeout: int = 5
) -> bool:
    """Run system commands with unified error handling

    Args:
        commands: List of command arrays to try in order
        operation: Description of the operation for logging
        timeout: Command timeout in seconds

    Returns:
        True if any command succeeded, False if all failed
    """
    for cmd in commands:
        try:
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                timeout=timeout,
                text=True,
            )
            logger.debug(f"{operation} successful: {' '.join(cmd)}")
            return True
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ) as e:
            logger.debug(f"Command failed: {' '.join(cmd)} - {e}")
            continue

    logger.warning(f"All {operation} commands failed")
    return False


class SystemCommands:
    """Commands for system-level operations and qtile management"""

    def __init__(self, color_manager: Any) -> None:
        self.color_manager = color_manager

    def manual_color_reload(self, qtile: Any) -> None:
        """Manually reload colors"""
        try:
            logger.info("Manual color reload requested")
            self.color_manager.manual_reload_colors()
            logger.info("Color reload completed")
        except Exception as e:
            logger.error(f"Error reloading colors: {e}")

    def manual_retile_all(self, qtile: Any) -> None:
        """Manually force all windows to tile"""
        try:
            from modules.hooks import create_hook_manager

            hook_manager = create_hook_manager(self.color_manager)
            count = hook_manager.force_retile_all_windows(qtile)
            logger.info(f"Manual retile completed - {count} windows retiled")
        except Exception as e:
            logger.error(f"Manual retile failed: {e}")

    def manual_screen_reconfigure(self, qtile: Any) -> None:
        """Manually reconfigure screens after monitor changes"""
        try:
            logger.info("Manual screen reconfiguration requested")
            from modules.bar_factory import create_bar_manager
            from modules.screens import get_screen_count, refresh_screens

            refresh_screens()
            new_screen_count = get_screen_count()
            logger.info(f"Detected {new_screen_count} screens")

            # Recreate screens
            from qtile_config import get_config

            qtile_config = get_config()
            bar_manager = create_bar_manager(self.color_manager, qtile_config)
            new_screens = bar_manager.create_screens(new_screen_count)
            qtile.config.screens = new_screens

            # Restart to apply changes
            qtile.restart()
        except Exception as e:
            logger.error(f"Screen reconfiguration failed: {e}")

    def show_hotkeys(self, qtile: Any, key_manager: Any) -> None:
        """Show hotkey display window"""
        try:
            logger.info("Showing hotkey display")
            from modules.hotkeys import create_hotkey_display

            hotkey_display = create_hotkey_display(key_manager, self.color_manager)
            hotkey_display.show_hotkeys()
        except Exception as e:
            logger.error(f"Error showing hotkeys: {e}")
            # Fallback to simple dmenu
            try:
                from modules.hotkeys import create_hotkey_display

                hotkey_display = create_hotkey_display(key_manager, self.color_manager)
                hotkey_display.show_hotkeys_simple()
            except Exception as e2:
                logger.error(f"Fallback hotkey display also failed: {e2}")

    def restart_qtile(self, qtile: Any) -> None:
        """Restart qtile"""
        try:
            logger.info("Restarting qtile")
            qtile.restart()
        except Exception as e:
            logger.error(f"Error restarting qtile: {e}")

    def shutdown_qtile(self, qtile: Any) -> None:
        """Shutdown qtile"""
        try:
            logger.info("Shutting down qtile")
            qtile.shutdown()
        except Exception as e:
            logger.error(f"Error shutting down qtile: {e}")

    def reload_config(self, qtile: Any) -> None:
        """Reload qtile configuration"""
        try:
            logger.info("Reloading qtile configuration")
            qtile.reload_config()
        except Exception as e:
            logger.error(f"Error reloading config: {e}")

    def get_system_info(self, qtile: Any) -> dict[str, Any]:
        """Get system information"""
        try:
            return {
                "qtile_version": getattr(qtile, "version", "unknown"),
                "screen_count": len(qtile.screens),
                "group_count": len(qtile.groups),
                "current_group": qtile.current_group.name,
                "current_screen": qtile.screens.index(qtile.current_screen),
                "current_layout": qtile.current_group.layout.name,
                "window_count": len(qtile.current_group.windows),
                "color_manager_status": (
                    self.color_manager.is_monitoring() if self.color_manager else False
                ),
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {}

    def debug_dump_state(self, qtile: Any) -> dict[str, Any]:
        """Dump current qtile state for debugging"""
        try:
            state = {
                "system_info": self.get_system_info(qtile),
                "groups": [
                    {
                        "name": g.name,
                        "layout": g.layout.name,
                        "window_count": len(g.windows),
                        "windows": (
                            [w.name for w in g.windows] if hasattr(g, "windows") else []
                        ),
                    }
                    for g in qtile.groups
                ],
                "screens": [
                    {
                        "index": i,
                        "group": screen.group.name if screen.group else None,
                        "width": screen.width,
                        "height": screen.height,
                    }
                    for i, screen in enumerate(qtile.screens)
                ],
            }

            import json

            debug_output = json.dumps(state, indent=2)
            logger.info(f"Qtile state dump:\n{debug_output}")
            return state
        except Exception as e:
            logger.error(f"Error dumping state: {e}")
            return {}

    def emergency_reset(self, qtile: Any) -> None:
        """Emergency reset - try to recover from problematic state"""
        try:
            logger.warning("Emergency reset initiated")

            # Try to normalize all layouts
            for group in qtile.groups:
                try:
                    if hasattr(group.layout, "normalize"):
                        group.layout.normalize()
                    elif hasattr(group.layout, "reset"):
                        group.layout.reset()
                except Exception:
                    pass

            # Force retile if available
            try:
                self.manual_retile_all(qtile)
            except Exception:
                pass

            # Switch to a safe layout (tile or max)
            try:
                qtile.current_group.setlayout("tile")
            except Exception:
                try:
                    qtile.current_group.setlayout("max")
                except Exception:
                    pass

            logger.info("Emergency reset completed")

        except Exception as e:
            logger.error(f"Emergency reset failed: {e}")

    def cycle_through_groups(self, qtile: Any, direction: int = 1) -> None:
        """Cycle through groups in order"""
        try:
            current_idx = qtile.groups.index(qtile.current_group)
            next_idx = (current_idx + direction) % len(qtile.groups)
            qtile.groups[next_idx].cmd_toscreen()
            logger.debug(f"Switched to group: {qtile.groups[next_idx].name}")
        except Exception as e:
            logger.error(f"Error cycling groups: {e}")

    def focus_urgent_window(self, qtile: Any) -> bool:
        """Focus the next urgent window if any"""
        try:
            for group in qtile.groups:
                for window in group.windows:
                    if getattr(window, "urgent", False):
                        group.cmd_toscreen()
                        window.cmd_focus()
                        logger.debug(f"Focused urgent window: {window.name}")
                        return True
            logger.debug("No urgent windows found")
            return False
        except Exception as e:
            logger.error(f"Error focusing urgent window: {e}")
            return False

    # ===== LAPTOP FUNCTION KEY SUPPORT =====

    @staticmethod
    def brightness_up(qtile: Any) -> None:
        """Increase screen brightness"""
        brightness_commands = [
            ["xbacklight", "-inc", "10"],  # xbacklight (most common)
            ["brightnessctl", "set", "+10%"],  # brightnessctl
            ["light", "-A", "10"],  # light utility
            ["doas", "xbacklight", "-inc", "10"],  # OpenBSD with doas
        ]
        run_system_command(brightness_commands, "brightness increase")

    @staticmethod
    def brightness_down(qtile: Any) -> None:
        """Decrease screen brightness"""
        brightness_commands = [
            ["xbacklight", "-dec", "10"],
            ["brightnessctl", "set", "10%-"],
            ["light", "-U", "10"],
            ["doas", "xbacklight", "-dec", "10"],
        ]
        run_system_command(brightness_commands, "brightness decrease")

    @staticmethod
    def volume_up(qtile: Any) -> None:
        """Increase system volume"""
        volume_commands = [
            [
                "pactl",
                "set-sink-volume",
                "@DEFAULT_SINK@",
                "+5%",
            ],  # PulseAudio
            ["amixer", "sset", "Master", "5%+"],  # ALSA
            ["mixerctl", "outputs.master=+0.05"],  # OpenBSD sndio
            ["doas", "mixerctl", "outputs.master=+0.05"],  # OpenBSD with doas
        ]
        run_system_command(volume_commands, "volume increase")

    @staticmethod
    def volume_down(qtile: Any) -> None:
        """Decrease system volume"""
        volume_commands = [
            ["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-5%"],
            ["amixer", "sset", "Master", "5%-"],
            ["mixerctl", "outputs.master=-0.05"],
            ["doas", "mixerctl", "outputs.master=-0.05"],
        ]
        run_system_command(volume_commands, "volume decrease")

    @staticmethod
    def volume_mute_toggle(qtile: Any) -> None:
        """Toggle volume mute"""
        mute_commands = [
            ["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"],
            ["amixer", "sset", "Master", "toggle"],
            ["mixerctl", "outputs.master.mute=toggle"],
            ["doas", "mixerctl", "outputs.master.mute=toggle"],
        ]
        run_system_command(mute_commands, "volume mute toggle")

    @staticmethod
    def media_play_pause(qtile: Any) -> None:
        """Toggle media play/pause"""
        media_commands = [
            ["playerctl", "play-pause"],  # Most media players
            ["mpc", "toggle"],  # MPD
            ["cmus-remote", "-u"],  # cmus
            [
                "dbus-send",
                "--print-reply",
                "--dest=org.mpris.MediaPlayer2.spotify",
                "/org/mpris/MediaPlayer2",
                "org.mpris.MediaPlayer2.Player.PlayPause",
            ],  # Spotify via dbus
        ]
        run_system_command(media_commands, "media play/pause toggle")

    @staticmethod
    def media_next(qtile: Any) -> None:
        """Skip to next media track"""
        next_commands = [
            ["playerctl", "next"],
            ["mpc", "next"],
            ["cmus-remote", "-n"],
        ]
        run_system_command(next_commands, "media next")

    @staticmethod
    def media_prev(qtile: Any) -> None:
        """Skip to previous media track"""
        prev_commands = [
            ["playerctl", "previous"],
            ["mpc", "prev"],
            ["cmus-remote", "-r"],
        ]
        run_system_command(prev_commands, "media previous")

    @staticmethod
    def wifi_toggle(qtile: Any) -> None:
        """Toggle WiFi on/off"""
        # First check if wifi is on or off, then toggle
        # This is a simplified version - you might want to enhance this
        toggle_commands = [
            ["nmcli", "radio", "wifi", "off"],  # NetworkManager
            ["rfkill", "block", "wifi"],  # rfkill
            ["doas", "ifconfig", "iwn0", "down"],  # OpenBSD
        ]
        run_system_command(toggle_commands, "WiFi toggle")

    @staticmethod
    def bluetooth_toggle(qtile: Any) -> None:
        """Toggle Bluetooth on/off"""
        bt_commands = [
            ["bluetoothctl", "power", "off"],  # bluetoothctl
            ["rfkill", "block", "bluetooth"],  # rfkill
            ["doas", "rcctl", "stop", "bluetooth"],  # OpenBSD
        ]
        run_system_command(bt_commands, "Bluetooth toggle")

    @staticmethod
    def keyboard_backlight_toggle(qtile: Any) -> None:
        """Toggle keyboard backlight"""
        kb_light_commands = [
            ["brightnessctl", "--device=kbd_backlight", "set", "+33%"],
            ["light", "-s", "sysfs/leds/kbd_backlight", "-A", "33"],
            ["xset", "led", "3"],  # Fallback
        ]
        run_system_command(kb_light_commands, "keyboard backlight toggle")

    @staticmethod
    def display_toggle(qtile: Any) -> None:
        """Toggle external display"""
        # This is a basic implementation - you might want to customize
        display_commands = [
            ["xrandr", "--auto"],  # Auto-detect displays
            ["autorandr", "--change"],  # If using autorandr
        ]
        run_system_command(display_commands, "display toggle")
