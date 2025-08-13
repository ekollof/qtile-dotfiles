#!/usr/bin/env python3
"""
Window management commands for qtile
"""

from typing import Any

from libqtile.log_utils import logger


class WindowCommands:
    """Commands for managing windows across screens and groups"""

    def __init__(self, qtile_config: Any) -> None:
        self.qtile_config = qtile_config

    @staticmethod
    def window_to_previous_screen(qtile: Any) -> None:
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
    def window_to_next_screen(qtile: Any) -> None:
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
    def cycle_window_through_screens(qtile: Any) -> None:
        """Cycle current window through all screens"""
        try:
            current_screen_idx = qtile.screens.index(qtile.current_screen)
            next_screen_idx = (current_screen_idx + 1) % len(qtile.screens)

            if next_screen_idx != current_screen_idx:
                group = qtile.screens[next_screen_idx].group.name
                qtile.current_window.togroup(group)
                logger.debug(
                    f"Cycled window to screen {next_screen_idx} (group: {group})"
                )
        except Exception as e:
            logger.error(f"Error cycling window through screens: {e}")

    @staticmethod
    def focus_previous_screen(qtile: Any) -> None:
        """Focus previous screen"""
        try:
            qtile.cmd_prev_screen()
        except Exception as e:
            logger.error(f"Error focusing previous screen: {e}")

    @staticmethod
    def focus_next_screen(qtile: Any) -> None:
        """Focus next screen"""
        try:
            qtile.cmd_next_screen()
        except Exception as e:
            logger.error(f"Error focusing next screen: {e}")

    @staticmethod
    def toggle_window_floating(qtile: Any) -> None:
        """Toggle floating state of current window"""
        try:
            if qtile.current_window:
                qtile.current_window.toggle_floating()
                state = "floating" if qtile.current_window.floating else "tiled"
                logger.debug(f"Window is now {state}")
        except Exception as e:
            logger.error(f"Error toggling window floating: {e}")

    @staticmethod
    def toggle_fullscreen(qtile: Any) -> None:
        """Toggle fullscreen state of current window"""
        try:
            if qtile.current_window:
                qtile.current_window.toggle_fullscreen()
                state = "fullscreen" if qtile.current_window.fullscreen else "windowed"
                logger.debug(f"Window is now {state}")
        except Exception as e:
            logger.error(f"Error toggling window fullscreen: {e}")

    @staticmethod
    def kill_window(qtile: Any) -> None:
        """Kill the current window"""
        try:
            if qtile.current_window:
                window_name = getattr(qtile.current_window, "name", "unknown")
                qtile.current_window.kill()
                logger.debug(f"Killed window: {window_name}")
        except Exception as e:
            logger.error(f"Error killing window: {e}")

    @staticmethod
    def minimize_window(qtile: Any) -> None:
        """Minimize current window if supported"""
        try:
            if qtile.current_window and hasattr(qtile.current_window, "minimize"):
                qtile.current_window.minimize()
                logger.debug("Window minimized")
        except Exception as e:
            logger.error(f"Error minimizing window: {e}")

    @staticmethod
    def get_window_info(qtile: Any) -> dict[str, Any] | None:
        """Get information about the current window"""
        try:
            if qtile.current_window:
                return {
                    "name": getattr(qtile.current_window, "name", "unknown"),
                    "wm_class": getattr(
                        qtile.current_window, "get_wm_class", lambda: None
                    )(),
                    "floating": qtile.current_window.floating,
                    "fullscreen": qtile.current_window.fullscreen,
                    "minimized": getattr(qtile.current_window, "minimized", False),
                    "group": (
                        qtile.current_window.group.name
                        if qtile.current_window.group
                        else None
                    ),
                    "screen": qtile.screens.index(qtile.current_screen),
                }
            return None
        except Exception as e:
            logger.error(f"Error getting window info: {e}")
            return None

    @staticmethod
    def move_window_to_group(qtile: Any, group_name: str) -> None:
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
    def bring_group_to_front(qtile: Any, group_name: str) -> None:
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
    def swap_window_to_main(qtile: Any) -> None:
        """Swap current window with main window in layouts that support it"""
        try:
            layout_name = qtile.current_group.layout.name.lower()
            if layout_name in ["monadtall", "monadwide", "bsp"]:
                if hasattr(qtile.current_group.layout, "swap_main"):
                    qtile.current_group.layout.swap_main()
                    logger.debug("Swapped window to main position")
                elif hasattr(qtile.current_group.layout, "swap"):
                    qtile.current_group.layout.swap()
                    logger.debug("Swapped windows")
        except Exception as e:
            logger.error(f"Error swapping window to main: {e}")

    @staticmethod
    def smart_maximize(qtile: Any) -> None:
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
            is_maximized = getattr(current_window, "maximized", False)
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
                    if (
                        window != current_window
                        and getattr(window, "minimized", False)
                        and getattr(window, "_smart_maximized_hidden", False)
                    ):
                        window.toggle_minimize()
                        # Clear the flag
                        window._smart_maximized_hidden = False
                        restored_count += 1
                        logger.debug(f"Restored window: {window.name}")

                logger.info(f"Restored {restored_count} windows")

            else:
                # Maximize: hide other windows and maximize current
                logger.info("Maximizing window and hiding others")

                # First, minimize all other windows in the current group
                hidden_count = 0
                for window in current_group.windows:
                    if (
                        window != current_window
                        and not getattr(window, "minimized", False)
                        and not window.floating
                    ):  # Don't minimize floating windows
                        # Mark that this window was hidden by smart maximize
                        window._smart_maximized_hidden = True
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

    def _warp_mouse_to_window(self, qtile: Any) -> None:
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

    def _focus_first_window_in_stack(self, qtile: Any) -> bool:
        """Helper function to ensure focus is on the first window in the current screen's stack"""
        try:
            current_group = qtile.current_screen.group
            if current_group and current_group.windows:
                # Get the first window in the stack
                first_window = current_group.windows[0]
                if first_window:
                    # Focus the first window
                    current_group.focus(first_window)
                    logger.debug(f"Focused first window in stack: {first_window.name}")
                    return True
            return False
        except Exception as e:
            logger.debug(f"Error focusing first window in stack: {e}")
            return False

    def focus_left_with_warp(self, qtile: Any) -> None:
        """Move focus left and warp mouse to target window"""
        try:
            # Execute the layout's left focus command
            qtile.current_layout.left()

            # Warp mouse to the newly focused window (if enabled)
            self._warp_mouse_to_window(qtile)
            logger.debug("Focus moved left with mouse warp")

        except Exception as e:
            logger.error(f"Error in focus_left_with_warp: {e}")

    def focus_right_with_warp(self, qtile: Any) -> None:
        """Move focus right and warp mouse to target window"""
        try:
            # Execute the layout's right focus command
            qtile.current_layout.right()

            # Warp mouse to the newly focused window (if enabled)
            self._warp_mouse_to_window(qtile)
            logger.debug("Focus moved right with mouse warp")

        except Exception as e:
            logger.error(f"Error in focus_right_with_warp: {e}")

    def focus_up_with_warp(self, qtile: Any) -> None:
        """Move focus up and warp mouse to target window"""
        try:
            # Execute the layout's up focus command
            qtile.current_layout.up()

            # Warp mouse to the newly focused window (if enabled)
            self._warp_mouse_to_window(qtile)
            logger.debug("Focus moved up with mouse warp")

        except Exception as e:
            logger.error(f"Error in focus_up_with_warp: {e}")

    def focus_down_with_warp(self, qtile: Any) -> None:
        """Move focus down and warp mouse to target window"""
        try:
            # Execute the layout's down focus command
            qtile.current_layout.down()

            # Warp mouse to the newly focused window (if enabled)
            self._warp_mouse_to_window(qtile)
            logger.debug("Focus moved down with mouse warp")

        except Exception as e:
            logger.error(f"Error in focus_down_with_warp: {e}")

    def focus_prev_screen_with_warp(self, qtile: Any) -> None:
        """Focus previous screen, focus first window in stack, and warp mouse"""
        try:
            # Execute the previous screen focus command
            qtile.cmd_prev_screen()

            # Focus the first window in the stack on the new screen
            self._focus_first_window_in_stack(qtile)

            # Warp mouse to the newly focused window (if enabled)
            self._warp_mouse_to_window(qtile)
            logger.debug(
                "Focus moved to previous screen, first window focused, mouse warped"
            )

        except Exception as e:
            logger.error(f"Error in focus_prev_screen_with_warp: {e}")

    def focus_next_screen_with_warp(self, qtile: Any) -> None:
        """Focus next screen, focus first window in stack, and warp mouse"""
        try:
            # Execute the next screen focus command
            qtile.cmd_next_screen()

            # Focus the first window in the stack on the new screen
            self._focus_first_window_in_stack(qtile)

            # Warp mouse to the newly focused window (if enabled)
            self._warp_mouse_to_window(qtile)
            logger.debug(
                "Focus moved to next screen, first window focused, mouse warped"
            )

        except Exception as e:
            logger.error(f"Error in focus_next_screen_with_warp: {e}")
