#!/usr/bin/env python3
"""
System-level commands for qtile
"""

from libqtile.log_utils import logger


class SystemCommands:
    """Commands for system-level operations and qtile management"""
    
    def __init__(self, color_manager):
        self.color_manager = color_manager

    def manual_color_reload(self, qtile):
        """Manually reload colors"""
        try:
            logger.info("Manual color reload requested")
            self.color_manager.update_colors()
            logger.info("Color reload completed")
        except Exception as e:
            logger.error(f"Error reloading colors: {e}")

    def manual_retile_all(self, qtile):
        """Manually force all windows to tile"""
        try:
            from modules.hooks import create_hook_manager
            hook_manager = create_hook_manager(self.color_manager)
            count = hook_manager.force_retile_all_windows(qtile)
            logger.info(f"Manual retile completed - {count} windows retiled")
        except Exception as e:
            logger.error(f"Manual retile failed: {e}")

    def manual_screen_reconfigure(self, qtile):
        """Manually reconfigure screens after monitor changes"""
        try:
            logger.info("Manual screen reconfiguration requested")
            from modules.screens import refresh_screens, get_screen_count
            from modules.bars import create_bar_manager
            
            refresh_screens()
            new_screen_count = get_screen_count()
            logger.info(f"Detected {new_screen_count} screens")

            # Recreate screens
            bar_manager = create_bar_manager(self.color_manager)
            new_screens = bar_manager.create_screens(new_screen_count)
            qtile.config.screens = new_screens

            # Restart to apply changes
            qtile.restart()
        except Exception as e:
            logger.error(f"Screen reconfiguration failed: {e}")

    def show_hotkeys(self, qtile, key_manager):
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

    def restart_qtile(self, qtile):
        """Restart qtile"""
        try:
            logger.info("Restarting qtile")
            qtile.restart()
        except Exception as e:
            logger.error(f"Error restarting qtile: {e}")

    def shutdown_qtile(self, qtile):
        """Shutdown qtile"""
        try:
            logger.info("Shutting down qtile")
            qtile.shutdown()
        except Exception as e:
            logger.error(f"Error shutting down qtile: {e}")

    def reload_config(self, qtile):
        """Reload qtile configuration"""
        try:
            logger.info("Reloading qtile configuration")
            qtile.reload_config()
        except Exception as e:
            logger.error(f"Error reloading config: {e}")

    def get_system_info(self, qtile):
        """Get system information"""
        try:
            return {
                'qtile_version': getattr(qtile, 'version', 'unknown'),
                'screen_count': len(qtile.screens),
                'group_count': len(qtile.groups),
                'current_group': qtile.current_group.name,
                'current_screen': qtile.screens.index(qtile.current_screen),
                'current_layout': qtile.current_group.layout.name,
                'window_count': len(qtile.current_group.windows),
                'color_manager_status': self.color_manager.is_monitoring() if self.color_manager else False,
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {}

    def debug_dump_state(self, qtile):
        """Dump current qtile state for debugging"""
        try:
            state = {
                'system_info': self.get_system_info(qtile),
                'groups': [
                    {
                        'name': g.name,
                        'layout': g.layout.name,
                        'window_count': len(g.windows),
                        'windows': [w.name for w in g.windows] if hasattr(g, 'windows') else []
                    }
                    for g in qtile.groups
                ],
                'screens': [
                    {
                        'index': i,
                        'group': screen.group.name if screen.group else None,
                        'width': screen.width,
                        'height': screen.height,
                    }
                    for i, screen in enumerate(qtile.screens)
                ]
            }
            
            import json
            debug_output = json.dumps(state, indent=2)
            logger.info(f"Qtile state dump:\n{debug_output}")
            return state
        except Exception as e:
            logger.error(f"Error dumping state: {e}")
            return {}

    def emergency_reset(self, qtile):
        """Emergency reset - try to recover from problematic state"""
        try:
            logger.warning("Emergency reset initiated")
            
            # Try to normalize all layouts
            for group in qtile.groups:
                try:
                    if hasattr(group.layout, 'normalize'):
                        group.layout.normalize()
                    elif hasattr(group.layout, 'reset'):
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
                qtile.current_group.setlayout('tile')
            except Exception:
                try:
                    qtile.current_group.setlayout('max')
                except Exception:
                    pass
            
            logger.info("Emergency reset completed")
            
        except Exception as e:
            logger.error(f"Emergency reset failed: {e}")

    def cycle_through_groups(self, qtile, direction=1):
        """Cycle through groups in order"""
        try:
            current_idx = qtile.groups.index(qtile.current_group)
            next_idx = (current_idx + direction) % len(qtile.groups)
            qtile.groups[next_idx].cmd_toscreen()
            logger.debug(f"Switched to group: {qtile.groups[next_idx].name}")
        except Exception as e:
            logger.error(f"Error cycling groups: {e}")

    def focus_urgent_window(self, qtile):
        """Focus the next urgent window if any"""
        try:
            for group in qtile.groups:
                for window in group.windows:
                    if getattr(window, 'urgent', False):
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
    def brightness_up(qtile):
        """Increase screen brightness"""
        try:
            import subprocess
            
            # Try different brightness control methods (OpenBSD compatible)
            brightness_commands = [
                ['xbacklight', '-inc', '10'],           # xbacklight (most common)
                ['brightnessctl', 'set', '+10%'],       # brightnessctl
                ['light', '-A', '10'],                  # light utility
                ['doas', 'xbacklight', '-inc', '10']    # OpenBSD with doas
            ]
            
            for cmd in brightness_commands:
                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                    logger.debug(f"Brightness increased using: {' '.join(cmd)}")
                    return
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            logger.warning("No brightness control utility found")
            
        except Exception as e:
            logger.error(f"Error increasing brightness: {e}")

    @staticmethod 
    def brightness_down(qtile):
        """Decrease screen brightness"""
        try:
            import subprocess
            
            brightness_commands = [
                ['xbacklight', '-dec', '10'],
                ['brightnessctl', 'set', '10%-'],
                ['light', '-U', '10'],
                ['doas', 'xbacklight', '-dec', '10']
            ]
            
            for cmd in brightness_commands:
                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                    logger.debug(f"Brightness decreased using: {' '.join(cmd)}")
                    return
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            logger.warning("No brightness control utility found")
            
        except Exception as e:
            logger.error(f"Error decreasing brightness: {e}")

    @staticmethod
    def volume_up(qtile):
        """Increase system volume"""
        try:
            import subprocess
            
            volume_commands = [
                ['pactl', 'set-sink-volume', '@DEFAULT_SINK@', '+5%'],   # PulseAudio
                ['amixer', 'sset', 'Master', '5%+'],                     # ALSA
                ['mixerctl', 'outputs.master=+0.05'],                    # OpenBSD sndio
                ['doas', 'mixerctl', 'outputs.master=+0.05']             # OpenBSD with doas
            ]
            
            for cmd in volume_commands:
                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                    logger.debug(f"Volume increased using: {' '.join(cmd)}")
                    return
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            logger.warning("No volume control utility found")
            
        except Exception as e:
            logger.error(f"Error increasing volume: {e}")

    @staticmethod
    def volume_down(qtile):
        """Decrease system volume"""
        try:
            import subprocess
            
            volume_commands = [
                ['pactl', 'set-sink-volume', '@DEFAULT_SINK@', '-5%'],
                ['amixer', 'sset', 'Master', '5%-'],
                ['mixerctl', 'outputs.master=-0.05'],
                ['doas', 'mixerctl', 'outputs.master=-0.05']
            ]
            
            for cmd in volume_commands:
                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                    logger.debug(f"Volume decreased using: {' '.join(cmd)}")
                    return
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            logger.warning("No volume control utility found")
            
        except Exception as e:
            logger.error(f"Error decreasing volume: {e}")

    @staticmethod
    def volume_mute_toggle(qtile):
        """Toggle volume mute"""
        try:
            import subprocess
            
            mute_commands = [
                ['pactl', 'set-sink-mute', '@DEFAULT_SINK@', 'toggle'],
                ['amixer', 'sset', 'Master', 'toggle'],
                ['mixerctl', 'outputs.master.mute=toggle'],
                ['doas', 'mixerctl', 'outputs.master.mute=toggle']
            ]
            
            for cmd in mute_commands:
                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                    logger.debug(f"Volume mute toggled using: {' '.join(cmd)}")
                    return
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            logger.warning("No volume mute control utility found")
            
        except Exception as e:
            logger.error(f"Error toggling volume mute: {e}")

    @staticmethod
    def media_play_pause(qtile):
        """Toggle media play/pause"""
        try:
            import subprocess
            
            media_commands = [
                ['playerctl', 'play-pause'],                    # Most media players
                ['mpc', 'toggle'],                              # MPD
                ['cmus-remote', '-u'],                          # cmus
                ['dbus-send', '--print-reply', '--dest=org.mpris.MediaPlayer2.spotify', 
                 '/org/mpris/MediaPlayer2', 'org.mpris.MediaPlayer2.Player.PlayPause']  # Spotify via dbus
            ]
            
            for cmd in media_commands:
                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                    logger.debug(f"Media play/pause toggled using: {' '.join(cmd)}")
                    return
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            logger.warning("No media control utility found")
            
        except Exception as e:
            logger.error(f"Error toggling media play/pause: {e}")

    @staticmethod
    def media_next(qtile):
        """Skip to next media track"""
        try:
            import subprocess
            
            next_commands = [
                ['playerctl', 'next'],
                ['mpc', 'next'],
                ['cmus-remote', '-n']
            ]
            
            for cmd in next_commands:
                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                    logger.debug(f"Media next using: {' '.join(cmd)}")
                    return
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            logger.warning("No media next control utility found")
            
        except Exception as e:
            logger.error(f"Error skipping to next track: {e}")

    @staticmethod
    def media_prev(qtile):
        """Skip to previous media track"""
        try:
            import subprocess
            
            prev_commands = [
                ['playerctl', 'previous'],
                ['mpc', 'prev'],
                ['cmus-remote', '-r']
            ]
            
            for cmd in prev_commands:
                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                    logger.debug(f"Media previous using: {' '.join(cmd)}")
                    return
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            logger.warning("No media previous control utility found")
            
        except Exception as e:
            logger.error(f"Error skipping to previous track: {e}")

    @staticmethod
    def wifi_toggle(qtile):
        """Toggle WiFi on/off"""
        try:
            import subprocess
            
            wifi_commands = [
                ['nmcli', 'radio', 'wifi'],                     # Check current state
                ['rfkill', 'list', 'wifi'],                     # Alternative check
                ['ifconfig', 'iwn0'],                           # OpenBSD check (iwn0 common Intel wifi)
            ]
            
            # First check if wifi is on or off, then toggle
            # This is a simplified version - you might want to enhance this
            toggle_commands = [
                ['nmcli', 'radio', 'wifi', 'off'],              # NetworkManager
                ['rfkill', 'block', 'wifi'],                    # rfkill
                ['doas', 'ifconfig', 'iwn0', 'down'],           # OpenBSD
            ]
            
            for cmd in toggle_commands:
                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                    logger.debug(f"WiFi toggled using: {' '.join(cmd)}")
                    return
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            logger.warning("No WiFi control utility found")
            
        except Exception as e:
            logger.error(f"Error toggling WiFi: {e}")

    @staticmethod
    def bluetooth_toggle(qtile):
        """Toggle Bluetooth on/off"""
        try:
            import subprocess
            
            bt_commands = [
                ['bluetoothctl', 'power', 'off'],               # bluetoothctl
                ['rfkill', 'block', 'bluetooth'],               # rfkill
                ['doas', 'rcctl', 'stop', 'bluetooth'],         # OpenBSD
            ]
            
            for cmd in bt_commands:
                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                    logger.debug(f"Bluetooth toggled using: {' '.join(cmd)}")
                    return
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            logger.warning("No Bluetooth control utility found")
            
        except Exception as e:
            logger.error(f"Error toggling Bluetooth: {e}")

    @staticmethod
    def keyboard_backlight_toggle(qtile):
        """Toggle keyboard backlight"""
        try:
            import subprocess
            
            kb_light_commands = [
                ['brightnessctl', '--device=kbd_backlight', 'set', '+33%'],
                ['light', '-s', 'sysfs/leds/kbd_backlight', '-A', '33'],
                ['xset', 'led', '3']                             # Fallback
            ]
            
            for cmd in kb_light_commands:
                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                    logger.debug(f"Keyboard backlight toggled using: {' '.join(cmd)}")
                    return
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            logger.warning("No keyboard backlight control utility found")
            
        except Exception as e:
            logger.error(f"Error toggling keyboard backlight: {e}")

    @staticmethod
    def display_toggle(qtile):
        """Toggle external display"""
        try:
            import subprocess
            
            # This is a basic implementation - you might want to customize
            display_commands = [
                ['xrandr', '--auto'],                           # Auto-detect displays
                ['autorandr', '--change'],                      # If using autorandr
            ]
            
            for cmd in display_commands:
                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                    logger.debug(f"Display toggled using: {' '.join(cmd)}")
                    return
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            logger.warning("No display control utility found")
            
        except Exception as e:
            logger.error(f"Error toggling display: {e}")
