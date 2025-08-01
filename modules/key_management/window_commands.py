#!/usr/bin/env python3
"""
Window management commands for qtile
"""

from libqtile.log_utils import logger


class WindowCommands:
    """Commands for managing windows across screens and groups"""
    
    def __init__(self):
        pass

    @staticmethod
    def window_to_previous_screen(qtile):
        """Move window to previous screen"""
        try:
            i = qtile.screens.index(qtile.current_screen)
            if i != 0:
                group = qtile.screens[i - 1].group.name
                qtile.current_window.togroup(group)
                logger.debug(f"Moved window to screen {i - 1} (group: {group})")
            else:
                logger.debug("Already on first screen, cannot move to previous")
        except Exception as e:
            logger.error(f"Error moving window to previous screen: {e}")

    @staticmethod
    def window_to_next_screen(qtile):
        """Move window to next screen"""
        try:
            i = qtile.screens.index(qtile.current_screen)
            if i + 1 != len(qtile.screens):
                group = qtile.screens[i + 1].group.name
                qtile.current_window.togroup(group)
                logger.debug(f"Moved window to screen {i + 1} (group: {group})")
            else:
                logger.debug("Already on last screen, cannot move to next")
        except Exception as e:
            logger.error(f"Error moving window to next screen: {e}")

    @staticmethod
    def cycle_window_through_screens(qtile):
        """Cycle current window through all screens"""
        try:
            current_screen_idx = qtile.screens.index(qtile.current_screen)
            next_screen_idx = (current_screen_idx + 1) % len(qtile.screens)
            
            if next_screen_idx != current_screen_idx:
                group = qtile.screens[next_screen_idx].group.name
                qtile.current_window.togroup(group)
                logger.debug(f"Cycled window to screen {next_screen_idx} (group: {group})")
        except Exception as e:
            logger.error(f"Error cycling window through screens: {e}")

    @staticmethod
    def focus_previous_screen(qtile):
        """Focus previous screen"""
        try:
            qtile.cmd_prev_screen()
        except Exception as e:
            logger.error(f"Error focusing previous screen: {e}")

    @staticmethod
    def focus_next_screen(qtile):
        """Focus next screen"""
        try:
            qtile.cmd_next_screen()
        except Exception as e:
            logger.error(f"Error focusing next screen: {e}")

    @staticmethod
    def toggle_window_floating(qtile):
        """Toggle floating state of current window"""
        try:
            if qtile.current_window:
                qtile.current_window.toggle_floating()
                state = "floating" if qtile.current_window.floating else "tiled"
                logger.debug(f"Window is now {state}")
        except Exception as e:
            logger.error(f"Error toggling window floating: {e}")

    @staticmethod
    def toggle_window_fullscreen(qtile):
        """Toggle fullscreen state of current window"""
        try:
            if qtile.current_window:
                qtile.current_window.toggle_fullscreen()
                state = "fullscreen" if qtile.current_window.fullscreen else "windowed"
                logger.debug(f"Window is now {state}")
        except Exception as e:
            logger.error(f"Error toggling window fullscreen: {e}")

    @staticmethod
    def kill_window(qtile):
        """Kill the current window"""
        try:
            if qtile.current_window:
                window_name = getattr(qtile.current_window, 'name', 'unknown')
                qtile.current_window.kill()
                logger.debug(f"Killed window: {window_name}")
        except Exception as e:
            logger.error(f"Error killing window: {e}")

    @staticmethod
    def minimize_window(qtile):
        """Minimize current window if supported"""
        try:
            if qtile.current_window and hasattr(qtile.current_window, 'minimize'):
                qtile.current_window.minimize()
                logger.debug("Window minimized")
        except Exception as e:
            logger.error(f"Error minimizing window: {e}")

    @staticmethod
    def get_window_info(qtile):
        """Get information about the current window"""
        try:
            if qtile.current_window:
                return {
                    'name': getattr(qtile.current_window, 'name', 'unknown'),
                    'wm_class': getattr(qtile.current_window, 'get_wm_class', lambda: None)(),
                    'floating': qtile.current_window.floating,
                    'fullscreen': qtile.current_window.fullscreen,
                    'minimized': getattr(qtile.current_window, 'minimized', False),
                    'group': qtile.current_window.group.name if qtile.current_window.group else None,
                    'screen': qtile.screens.index(qtile.current_screen),
                }
            return None
        except Exception as e:
            logger.error(f"Error getting window info: {e}")
            return None

    @staticmethod
    def move_window_to_group(qtile, group_name):
        """Move current window to specified group"""
        try:
            if qtile.current_window and group_name in [g.name for g in qtile.groups]:
                qtile.current_window.togroup(group_name)
                logger.debug(f"Moved window to group: {group_name}")
            else:
                logger.warning(f"Invalid group name: {group_name}")
        except Exception as e:
            logger.error(f"Error moving window to group {group_name}: {e}")

    @staticmethod
    def bring_group_to_front(qtile, group_name):
        """Bring specified group to current screen"""
        try:
            if group_name in [g.name for g in qtile.groups]:
                qtile.groups_map[group_name].cmd_toscreen()
                logger.debug(f"Brought group {group_name} to front")
            else:
                logger.warning(f"Invalid group name: {group_name}")
        except Exception as e:
            logger.error(f"Error bringing group {group_name} to front: {e}")

    @staticmethod
    def swap_window_to_main(qtile):
        """Swap current window with main window in layouts that support it"""
        try:
            layout_name = qtile.current_group.layout.name.lower()
            if layout_name in ['monadtall', 'monadwide', 'bsp']:
                if hasattr(qtile.current_group.layout, 'swap_main'):
                    qtile.current_group.layout.swap_main()
                    logger.debug("Swapped window to main position")
                elif hasattr(qtile.current_group.layout, 'swap'):
                    qtile.current_group.layout.swap()
                    logger.debug("Swapped windows")
        except Exception as e:
            logger.error(f"Error swapping window to main: {e}")
