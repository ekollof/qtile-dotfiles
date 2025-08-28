#!/usr/bin/env python3
"""
Consolidated commands module for qtile
Combines window commands, system commands, and layout-aware operations
"""

from typing import Any

from libqtile.log_utils import logger

from .notifications import get_popup_manager, show_popup_notification


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
            from modules.bars import create_bar_manager
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

    # ===== LAPTOP FUNCTION KEY SUPPORT =====
    # Note: Function key support removed - qtile doesn't support XF86 keysyms

    @staticmethod
    def test_notifications(qtile: Any) -> None:
        """Test notification system functionality with multiple fallbacks"""
        logger.info("Testing notification system...")

        # Try popup notification first
        try:
            show_popup_notification(
                "Qtile Popup Test",
                "Testing popup notification system - if you see this popup, it's working!",
                "normal",
            )
            logger.info("✅ Popup notification test sent")
        except Exception as e:
            logger.debug(f"Popup notification failed: {e}")

        # Try multiple notification methods
        methods_tried = []
        success = False

        # Method 1: Try our notification manager
        try:
            show_popup_notification(
                "Qtile Notification Test",
                "Testing notification system - if you see this, it's working!",
                "normal",
            )
            methods_tried.append("notification_manager: SUCCESS")
            success = True
            logger.info("✅ Notification test completed via notification manager")
        except Exception as e:
            methods_tried.append(f"notification_manager: FAILED ({e})")
            logger.debug(f"Notification manager failed: {e}")

        # Method 2: Try direct notify-send if first method failed
        if not success:
            try:
                import subprocess

                subprocess.run(
                    [
                        "notify-send",
                        "-t",
                        "5000",
                        "-u",
                        "normal",
                        "Qtile Notification Test (fallback)",
                        "Testing via notify-send command",
                    ],
                    check=True,
                    timeout=5,
                )
                methods_tried.append("notify-send: SUCCESS")
                success = True
                logger.info("✅ Notification test completed via notify-send")
            except Exception as e:
                methods_tried.append(f"notify-send: FAILED ({e})")
                logger.debug(f"notify-send failed: {e}")

        # Report results
        if success:
            logger.info("Notification test successful!")
        else:
            logger.warning("All notification methods failed:")
            for method in methods_tried:
                logger.warning(f"  - {method}")

    @staticmethod
    def test_urgent_notification(qtile: Any) -> None:
        """Test urgent notification with fallbacks"""
        logger.info("Testing urgent notification...")

        success = False

        # Try our notification manager first
        try:
            show_popup_notification(
                "🚨 Urgent Notification Test",
                "This is an urgent notification test - it should stay visible longer",
                "critical",
            )
            success = True
            logger.info(
                "✅ Urgent notification test completed via notification manager"
            )
        except Exception as e:
            logger.debug(f"Notification manager failed for urgent: {e}")

            # Fallback to notify-send
            try:
                import subprocess

                subprocess.run(
                    [
                        "notify-send",
                        "-t",
                        "0",  # No timeout
                        "-u",
                        "critical",
                        "🚨 Urgent Test (fallback)",
                        "This urgent notification uses notify-send",
                    ],
                    check=True,
                    timeout=5,
                )
                success = True
                logger.info("✅ Urgent notification test completed via notify-send")
            except Exception as e2:
                logger.warning(f"All urgent notification methods failed: {e}, {e2}")

        if not success:
            logger.error(
                "Urgent notification test failed - no working notification method"
            )

    @staticmethod
    def notification_status(qtile: Any) -> None:
        """Show comprehensive notification system status"""
        logger.info("Checking notification system status...")

        # Check popup manager status
        popup_manager = get_popup_manager()
        popup_status = "Available" if popup_manager else "Not initialized"
        active_popups = len(popup_manager.active_notifications) if popup_manager else 0

        # Collect status information
        status_info = {
            "notification_manager": "Unknown",
            "popup_manager": popup_status,
            "active_popups": active_popups,
            "qtile_builtin": "Unknown",
            "qtile_builtin_working": "Unknown",
            "notify_send": "Unknown",
            "dbus": "Unknown",
        }

        # Test popup notification system
        try:
            popup_manager = get_popup_manager()
            status_info.update(
                {
                    "notification_system": "SimplePopup",
                    "popup_manager": "Available"
                    if popup_manager
                    else "Not initialized",
                    "qtile_extras": "Available",
                    "dbus_integration": "Yes",
                }
            )
        except Exception as e:
            status_info["notification_system"] = f"Error: {str(e)[:50]}"

        # Test Notify widget availability
        try:
            from libqtile import widget

            if hasattr(widget, "Notify"):
                status_info["notify_widget"] = "Available"
            else:
                status_info["notify_widget"] = "Not available"
        except Exception:
            status_info["notify_widget"] = "Error checking"

        # Format status message
        status_lines = [
            "📊 Notification System Status:",
            f"• Manager: {status_info['notification_manager']}",
            f"• Qtile built-in: {status_info['qtile_builtin']}",
            f"• Qtile working: {status_info['qtile_builtin_working']}",
            f"• notify-send: {status_info['notify_send']}",
            f"• D-Bus: {status_info['dbus']}",
            f"• Notify widget: {status_info['notify_widget']}",
        ]
        status_msg = "\n".join(status_lines)

        # Try to send the status notification
        success = False
        try:
            show_popup_notification("Notification System Status", status_msg, "normal")
            success = True
            logger.info("✅ Notification status displayed successfully")
        except Exception as e:
            logger.warning(f"Could not send status via notification manager: {e}")

            # Fallback to notify-send
            try:
                import subprocess

                subprocess.run(
                    [
                        "notify-send",
                        "-t",
                        "10000",
                        "-u",
                        "normal",
                        "Notification Status (fallback)",
                        status_msg,
                    ],
                    check=True,
                    timeout=5,
                )
                success = True
                logger.info("✅ Notification status displayed via notify-send")
            except Exception as e2:
                logger.error(f"All status notification methods failed: {e}, {e2}")

        # Always log the status to console as well
        logger.info("Notification System Status:")
        for line in status_lines[1:]:  # Skip the header
            logger.info(f"  {line}")

        if not success:
            logger.error("❌ Could not display status notification, but logged above")


class LayoutAwareCommands:
    """Commands that adapt their behavior based on the current layout"""

    def __init__(self):
        pass

    @staticmethod
    def smart_grow(qtile: Any) -> None:
        """Smart grow that adapts to current layout"""
        layout_name = qtile.current_group.layout.name.lower()

        try:
            match layout_name:
                case "monadtall" | "monadwide":
                    # MonadTall/Wide: grow main window
                    qtile.current_group.layout.grow()
                case "tile":
                    # Tile: increase ratio
                    qtile.current_group.layout.increase_ratio()
                case "bsp":
                    # BSP: grow window
                    qtile.current_group.layout.grow_right()
                case "matrix":
                    # Matrix: add column (horizontal growth)
                    qtile.current_group.layout.add()
                case _:
                    # Max and Floating layouts: no-op (but don't error)
                    pass
        except Exception as e:
            # Fallback for layouts that don't support the operation
            logger.debug(f"Smart grow not supported in {layout_name}: {e}")

    @staticmethod
    def smart_shrink(qtile: Any) -> None:
        """Smart shrink that adapts to current layout"""
        layout_name = qtile.current_group.layout.name.lower()

        try:
            match layout_name:
                case "monadtall" | "monadwide":
                    # MonadTall/Wide: shrink main window
                    qtile.current_group.layout.shrink()
                case "tile":
                    # Tile: decrease ratio
                    qtile.current_group.layout.decrease_ratio()
                case "bsp":
                    # BSP: shrink window
                    qtile.current_group.layout.grow_left()
                case "matrix":
                    # Matrix: remove column (horizontal shrink)
                    qtile.current_group.layout.delete()
                case _:
                    # Max and Floating layouts: no-op
                    pass
        except Exception as e:
            # Fallback for layouts that don't support the operation
            logger.debug(f"Smart shrink not supported in {layout_name}: {e}")

    @staticmethod
    def smart_grow_vertical(qtile: Any) -> None:
        """Smart vertical grow that adapts to current layout"""
        layout_name = qtile.current_group.layout.name.lower()

        try:
            match layout_name:
                case "monadtall" | "monadwide":
                    # MonadTall/Wide: grow main window
                    qtile.current_group.layout.grow()
                case "tile":
                    # Tile: no vertical resize in tile layout
                    pass
                case "bsp":
                    # BSP: grow window up
                    qtile.current_group.layout.grow_up()
                case "matrix":
                    # Matrix: no vertical resize (columns only)
                    pass
                case _:
                    # Max and Floating layouts: no-op
                    pass
        except Exception as e:
            logger.debug(f"Smart vertical grow not supported in {layout_name}: {e}")

    @staticmethod
    def smart_shrink_vertical(qtile: Any) -> None:
        """Smart vertical shrink that adapts to current layout"""
        layout_name = qtile.current_group.layout.name.lower()

        try:
            match layout_name:
                case "monadtall" | "monadwide":
                    # MonadTall/Wide: shrink main window
                    qtile.current_group.layout.shrink()
                case "tile":
                    # Tile: no vertical resize in tile layout
                    pass
                case "bsp":
                    # BSP: grow window down (shrink upward space)
                    qtile.current_group.layout.grow_down()
                case "matrix":
                    # Matrix: no vertical resize (columns only)
                    pass
                case _:
                    # Max and Floating layouts: no-op
                    pass
        except Exception as e:
            logger.debug(f"Smart vertical shrink not supported in {layout_name}: {e}")

    @staticmethod
    def smart_normalize(qtile: Any) -> None:
        """Smart normalize that works with different layouts"""
        layout_name = qtile.current_group.layout.name.lower()

        try:
            match layout_name:
                case "monadtall" | "monadwide" | "monadthreecol":
                    # Monad layouts: normalize secondary windows
                    qtile.current_group.layout.normalize()
                case "tile":
                    # Tile: reset to default ratios
                    qtile.current_group.layout.reset()
                case "bsp":
                    # BSP: normalize window sizes
                    qtile.current_group.layout.normalize()
                case "columns":
                    # Columns: normalize column widths and reset ratios
                    qtile.current_group.layout.normalize()
                case "spiral":
                    # Spiral: reset ratios to config values
                    qtile.current_group.layout.reset()
                case "verticaltile":
                    # VerticalTile: normalize window sizes
                    qtile.current_group.layout.normalize()
                case "plasma":
                    # Plasma: reset current window size to automatic
                    qtile.current_group.layout.reset_size()
                case "matrix":
                    # Matrix: no normalize function, but we can do nothing gracefully
                    pass
                case "max" | "floating":
                    # Max/Floating: no normalize needed
                    pass
                case _ if hasattr(qtile.current_group.layout, "normalize"):
                    # Generic normalize fallback
                    qtile.current_group.layout.normalize()
                case _ if hasattr(qtile.current_group.layout, "reset"):
                    # Generic reset fallback
                    qtile.current_group.layout.reset()
                case _:
                    # No normalize/reset available
                    pass
        except Exception as e:
            logger.debug(f"Normalize not supported in {layout_name}: {e}")

    @staticmethod
    def layout_safe_command(
        qtile: Any, command_name: str, *args: Any, **kwargs: Any
    ) -> Any:
        """Execute a layout command only if the layout supports it"""
        try:
            layout = qtile.current_group.layout
            if hasattr(layout, command_name):
                command = getattr(layout, command_name)
                if callable(command):
                    return command(*args, **kwargs)
        except Exception as e:
            logger.debug(f"Layout command {command_name} failed: {e}")

    @staticmethod
    def get_layout_info(qtile: Any) -> dict[str, Any]:
        """Get information about the current layout"""
        layout = qtile.current_group.layout
        return {
            "name": layout.name,
            "supports_grow": hasattr(layout, "grow"),
            "supports_shrink": hasattr(layout, "shrink"),
            "supports_normalize": hasattr(layout, "normalize"),
            "supports_reset": hasattr(layout, "reset"),
            "supports_flip": hasattr(layout, "flip"),
            # Note: maximize is now handled via lazy.window.toggle_maximize() which works with all layouts
        }

    @staticmethod
    def smart_flip(qtile: Any) -> None:
        """Smart flip that works with layouts that support it"""
        layout_name = qtile.current_group.layout.name.lower()

        try:
            match layout_name:
                case "monadtall" | "monadwide" | "bsp":
                    qtile.current_group.layout.flip()
                case "tile":
                    # Tile doesn't have flip, but we can swap main/secondary
                    if hasattr(qtile.current_group.layout, "swap_main"):
                        qtile.current_group.layout.swap_main()
                case _:
                    # Other layouts don't support flip
                    pass
        except Exception as e:
            logger.debug(f"Smart flip not supported in {layout_name}: {e}")


# Maintain backward compatibility
__all__ = [
    "LayoutAwareCommands",
    "SystemCommands",
    "WindowCommands",
]
