#!/usr/bin/env python3
"""
Window management commands for qtile
"""

from libqtile.log_utils import logger


class WindowCommands:
    """Commands for managing windows across screens and groups"""
    
    def __init__(self, qtile_config):
        self.qtile_config = qtile_config

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

    @staticmethod
    def smart_maximize(qtile):
        """
        Smart maximize that minimizes other windows when maximizing,
        and restores them when un-maximizing
        """
        try:
            current_window = qtile.current_window
            if not current_window:
                logger.debug("No current window to maximize")
                return
            
            # Check if window is currently maximized
            is_maximized = getattr(current_window, 'maximized', False)
            current_group = qtile.current_group
            
            logger.debug(f"Smart maximize called for window: {current_window.name}")
            logger.debug(f"Window currently maximized: {is_maximized}")
            logger.debug(f"Current group: {current_group.name}")
            logger.debug(f"Windows in group: {[w.name for w in current_group.windows]}")
            
            if is_maximized:
                # Un-maximize: restore the window and bring back other windows
                logger.info("Un-maximizing window and restoring other windows")
                current_window.toggle_maximize()
                
                # Restore minimized windows in current group
                restored_count = 0
                for window in current_group.windows:
                    if window != current_window and getattr(window, 'minimized', False):
                        # Check if window was minimized by our smart maximize
                        if getattr(window, '_smart_maximized_hidden', False):
                            window.toggle_minimize()
                            # Clear the flag
                            setattr(window, '_smart_maximized_hidden', False)
                            restored_count += 1
                            logger.debug(f"Restored window: {window.name}")
                
                logger.info(f"Restored {restored_count} windows")
                
            else:
                # Maximize: hide other windows and maximize current
                logger.info("Maximizing window and hiding others")
                
                # First, minimize all other windows in the current group
                hidden_count = 0
                for window in current_group.windows:
                    if (window != current_window and 
                        not getattr(window, 'minimized', False) and
                        not window.floating):  # Don't minimize floating windows
                        
                        # Mark that this window was hidden by smart maximize
                        setattr(window, '_smart_maximized_hidden', True)
                        window.toggle_minimize()
                        hidden_count += 1
                        logger.debug(f"Minimized window: {window.name}")
                
                logger.info(f"Minimized {hidden_count} windows")
                
                # Then maximize the current window
                current_window.toggle_maximize()
                logger.info(f"Maximized window: {current_window.name}")
                
        except Exception as e:
            logger.error(f"Error in smart maximize: {e}")
            # Fallback to regular maximize if something goes wrong
            try:
                qtile.current_window.toggle_maximize()
                logger.info("Fallback: Used regular maximize")
            except Exception as fallback_error:
                logger.error(f"Fallback maximize also failed: {fallback_error}")

    def _warp_mouse_to_window(self, qtile):
        """Helper function to warp mouse to center of current window"""
        try:
            # Check if mouse warping is enabled
            if not self.qtile_config.mouse_warp_focus:
                return
                
            current_window = qtile.current_window
            if not current_window:
                return
            
            # Get window geometry
            x = current_window.x
            y = current_window.y
            width = current_window.width
            height = current_window.height
            
            # Calculate center position
            center_x = x + (width // 2)
            center_y = y + (height // 2)
            
            # Warp mouse to center of window
            qtile.core.warp_pointer(center_x, center_y)
            logger.debug(f"Warped mouse to window center: ({center_x}, {center_y})")
            
        except Exception as e:
            logger.debug(f"Error warping mouse to window: {e}")

    def focus_left_with_warp(self, qtile):
        """Move focus left and warp mouse to target window"""
        try:
            # Execute the layout's left focus command
            qtile.current_layout.left()
            
            # Warp mouse to the newly focused window (if enabled)
            self._warp_mouse_to_window(qtile)
            logger.debug("Focus moved left with mouse warp")
            
        except Exception as e:
            logger.error(f"Error in focus_left_with_warp: {e}")

    def focus_right_with_warp(self, qtile):
        """Move focus right and warp mouse to target window"""
        try:
            # Execute the layout's right focus command
            qtile.current_layout.right()
            
            # Warp mouse to the newly focused window (if enabled)
            self._warp_mouse_to_window(qtile)
            logger.debug("Focus moved right with mouse warp")
            
        except Exception as e:
            logger.error(f"Error in focus_right_with_warp: {e}")

    def focus_up_with_warp(self, qtile):
        """Move focus up and warp mouse to target window"""
        try:
            # Execute the layout's up focus command
            qtile.current_layout.up()
            
            # Warp mouse to the newly focused window (if enabled)
            self._warp_mouse_to_window(qtile)
            logger.debug("Focus moved up with mouse warp")
            
        except Exception as e:
            logger.error(f"Error in focus_up_with_warp: {e}")

    def focus_down_with_warp(self, qtile):
        """Move focus down and warp mouse to target window"""
        try:
            # Execute the layout's down focus command
            qtile.current_layout.down()
            
            # Warp mouse to the newly focused window (if enabled)
            self._warp_mouse_to_window(qtile)
            logger.debug("Focus moved down with mouse warp")
            
        except Exception as e:
            logger.error(f"Error in focus_down_with_warp: {e}")

    def focus_prev_screen_with_warp(self, qtile):
        """Focus previous screen and warp mouse to focused window"""
        try:
            # Execute the previous screen focus command
            qtile.cmd_prev_screen()
            
            # Warp mouse to the newly focused window (if enabled)
            self._warp_mouse_to_window(qtile)
            logger.debug("Focus moved to previous screen with mouse warp")
            
        except Exception as e:
            logger.error(f"Error in focus_prev_screen_with_warp: {e}")

    def focus_next_screen_with_warp(self, qtile):
        """Focus next screen and warp mouse to focused window"""
        try:
            # Execute the next screen focus command
            qtile.cmd_next_screen()
            
            # Warp mouse to the newly focused window (if enabled)
            self._warp_mouse_to_window(qtile)
            logger.debug("Focus moved to next screen with mouse warp")
            
        except Exception as e:
            logger.error(f"Error in focus_next_screen_with_warp: {e}")
