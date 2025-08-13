#!/usr/bin/env python3
"""
Qtile Notification System Module

@brief Provides libnotify-compatible notification support for qtile
@author Andrath

This module provides comprehensive notification functionality including:
- Built-in notification server via qtile's Notify widget
- Libnotify compatibility for system notifications
- Notification display in the status bar
- Programmatic notification sending utilities
- Cross-platform portability (Linux, BSD)

@note This module follows modern Python 3.10+ standards
"""

import subprocess
from typing import Any, Dict, Optional

from libqtile import widget
from libqtile.log_utils import logger

from .colors import ColorManager
from .qtile_extras_notifications import QtileExtrasPopupManager, create_qtile_extras_popup_manager
from .popup_notify_widget import PopupNotifyWidget, create_popup_notify_widget


class NotificationManager:
    """
    @brief Manages qtile's notification system and libnotify compatibility

    This class provides a unified interface for handling notifications in qtile,
    including the built-in notification server and display widgets.
    """

    def __init__(self, color_manager: ColorManager) -> None:
        """
        @brief Initialize the notification manager
        @param color_manager: Color management instance for theming
        """
        self.color_manager = color_manager
        self._notification_enabled = False
        self._widget_defaults: Dict[str, Any] = {}
        self._popup_manager: Optional[QtileExtrasPopupManager] = None
        self._use_popups = False

    def _get_widget_defaults(self) -> Dict[str, Any]:
        """
        @brief Get default widget configuration with current theme colors
        @return Dictionary of widget defaults
        """
        if not self._widget_defaults:
            colordict = self.color_manager.get_colors()
            colors = colordict.get("colors", {})
            special = colordict.get("special", {})

            self._widget_defaults = {
                "font": "DejaVu Sans Mono",
                "fontsize": 12,
                "padding": 3,
                "foreground": colors.get("color5", "#ffffff"),
                "background": special.get("background", "#000000"),
            }
        return self._widget_defaults.copy()

    def create_notify_widget(self, use_popups: bool = False, **kwargs: Any) -> widget.base._Widget:
        """
        @brief Create a notification widget for the status bar
        @param use_popups: Whether to use popup notifications
        @param kwargs: Additional widget configuration options
        @return Configured Notify widget instance

        This widget displays notifications in the status bar and handles
        libnotify-compatible notification requests via D-Bus.
        """
        # Configure popup manager if using popups
        if use_popups:
            self._use_popups = True
            self._initialize_popup_manager()

        defaults = self._get_widget_defaults()
        colordict = self.color_manager.get_colors()
        colors = colordict.get("colors", {})

        # Merge user config with defaults
        config = {
            **defaults,
            "default_timeout": 10,
            "default_timeout_low": 5,
            "default_timeout_urgent": 0,  # Never timeout urgent notifications
            "foreground_urgent": colors.get("color1", "#ff0000"),
            "foreground_low": colors.get("color8", "#808080"),
            "action": True,  # Enable default action handling
            "audiofile": None,  # No audio by default
            "parse_text": None,  # No text parsing by default
            **kwargs
        }

        try:
            if use_popups:
                # Initialize popup manager if not already done
                if not self._popup_manager:
                    self._initialize_popup_manager()

                # Use custom popup notify widget
                popup_config = {
                    **config,
                    "enable_popup_forwarding": True,
                    "fallback_to_bar": False,
                    "show_popup_count": False,
                }
                notify_widget = create_popup_notify_widget(
                    popup_manager=self._popup_manager,
                    **popup_config
                )
                logger.info("Successfully created popup notify widget")
            else:
                # Use standard notify widget
                notify_widget = widget.Notify(**config)
                logger.info("Successfully created standard Notify widget")

            self._notification_enabled = True
            return notify_widget

        except ImportError:
            logger.warning("Notify widget not available - using fallback display")
            # Return a minimal text widget as fallback
            return widget.TextBox(
                text="🔔",
                **defaults,
                mouse_callbacks={"Button1": self._show_notification_error}
            )
        except Exception as e:
            logger.error(f"Failed to create Notify widget: {e}")
            # Return a minimal text widget as fallback
            return widget.TextBox(
                text="⚠",
                **defaults,
                mouse_callbacks={"Button1": self._show_notification_error}
            )

    def _show_notification_error(self) -> None:
        """
        @brief Show error message when notification system fails
        """
        try:
            self.send_notification(
                "Qtile Notification Error",
                "Notification system failed to initialize. Check logs for details.",
                urgency="critical"
            )
        except Exception:
            logger.error("Could not show notification error - notification system unavailable")

    def _show_popup_status(self) -> None:
        """
        @brief Show popup notification status when status widget is clicked
        """
        try:
            if self._popup_manager:
                status = self._popup_manager.get_status()
                status_msg = f"Active: {status['active_popups']}, Running: {status['running']}"
                self.send_notification("Popup Status", status_msg)
            else:
                self.send_notification("Popup Status", "Popup manager not initialized")
        except Exception as e:
            logger.error(f"Failed to show popup status: {e}")

    def _initialize_popup_manager(self) -> None:
        """
        @brief Initialize the popup notification manager
        """
        if not self._popup_manager:
            self._popup_manager = create_qtile_extras_popup_manager(self.color_manager)
            logger.info("QtileExtras popup notification manager initialized")

    def configure_popups(self, config: Dict[str, Any]) -> None:
        """
        @brief Configure popup notifications
        @param config: Configuration dictionary with popup settings
        """
        if not self._popup_manager:
            self._initialize_popup_manager()

        if self._popup_manager:
            self._popup_manager.configure(config)
            self._use_popups = config.get("use_popups", False)
            logger.info(f"Popup notifications configured: enabled={self._use_popups}")

    def send_notification(
        self,
        title: str,
        message: str,
        timeout: int = 5000,
        urgency: str = "normal",
        icon: Optional[str] = None,
        app_name: str = "qtile"
    ) -> bool:
        """
        @brief Send a notification using available methods
        @param title: Notification title
        @param message: Notification message body
        @param timeout: Timeout in milliseconds
        @param urgency: Urgency level (low, normal, critical)
        @param icon: Optional icon name or path
        @param app_name: Application name for the notification
        @return True if notification was sent successfully

        This method tries multiple notification methods in order of preference.
        """
        # Method 1: Try popup notifications if enabled
        if self._use_popups and self._popup_manager:
            try:
                self._popup_manager.show_notification(title, message, urgency, timeout)
                logger.debug(f"Sent popup notification: {title}")
                return True
            except Exception as e:
                logger.warning(f"Popup notification failed: {e}")

        # Method 2: Try qtile's built-in notification system (if available and working)
        if self._try_qtile_notification(title, message, timeout):
            return True

        # Method 3: Fallback to notify-send
        return self._send_via_notify_send(title, message, timeout, urgency, icon, app_name)

    def _try_qtile_notification(self, title: str, message: str, timeout: int) -> bool:
        """
        @brief Try qtile's built-in notification system
        @return True if successful, False otherwise
        """
        try:
            # Import here to avoid issues if not available
            from libqtile.utils import send_notification

            # Test if the function is actually callable and working
            send_notification(title, message, timeout=timeout//1000)
            logger.debug(f"Sent notification via qtile built-in: {title}")
            return True
        except ImportError:
            logger.debug("qtile.utils.send_notification not available")
            return False
        except AttributeError as e:
            logger.debug(f"qtile notification function not working: {e}")
            return False
        except Exception as e:
            logger.debug(f"qtile notification failed: {e}")
            return False

    def _send_via_notify_send(
        self,
        title: str,
        message: str,
        timeout: int,
        urgency: str,
        icon: Optional[str],
        app_name: str
    ) -> bool:
        """
        @brief Send notification using external notify-send command
        @param title: Notification title
        @param message: Notification message body
        @param timeout: Timeout in milliseconds
        @param urgency: Urgency level
        @param icon: Optional icon name or path
        @param app_name: Application name
        @return True if notification was sent successfully
        """
        try:
            cmd = [
                "notify-send",
                "-a", app_name,
                "-t", str(timeout),
                "-u", urgency,
                title,
                message
            ]

            if icon:
                cmd.extend(["-i", icon])

            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=5
            )

            logger.debug(f"Sent notification via notify-send: {title}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"notify-send failed: {e}")
            return False
        except subprocess.TimeoutExpired:
            logger.error("notify-send timed out")
            return False
        except FileNotFoundError:
            logger.warning("notify-send not found - install libnotify for external notifications")
            return False
        except Exception as e:
            logger.error(f"Unexpected error with notify-send: {e}")
            return False

    def test_notification_system(self) -> None:
        """
        @brief Test the notification system functionality

        Sends a test notification to verify the system is working correctly.
        """
        success = self.send_notification(
            "Qtile Notifications",
            "Notification system is working correctly!",
            timeout=3000,
            urgency="normal",
            icon="dialog-information"
        )

        if success:
            logger.info("Notification system test passed")
        else:
            logger.error("Notification system test failed")

    def is_notification_enabled(self) -> bool:
        """
        @brief Check if notifications are enabled and working
        @return True if notification system is functional
        """
        return self._notification_enabled

    def get_notification_status(self) -> Dict[str, Any]:
        """
        @brief Get comprehensive notification system status
        @return Dictionary with status information
        """
        status = {
            "enabled": self._notification_enabled,
            "use_popups": self._use_popups,
            "popup_manager_available": self._popup_manager is not None,
            "qtile_builtin": False,
            "qtile_builtin_working": False,
            "notify_send_available": False,
            "dbus_available": False
        }

        # Add popup manager status if available
        if self._popup_manager:
            popup_status = self._popup_manager.get_status()
            status["popup_status"] = popup_status

        # Check qtile built-in availability
        try:
            from libqtile.utils import send_notification
            status["qtile_builtin"] = True
            # Test if it actually works
            if self._try_qtile_notification("Test", "Test", 1000):
                status["qtile_builtin_working"] = True
        except ImportError:
            status["qtile_builtin"] = False
        except Exception:
            status["qtile_builtin"] = True
            status["qtile_builtin_working"] = False

        # Check notify-send availability
        try:
            subprocess.run(
                ["notify-send", "--version"],
                check=True,
                capture_output=True,
                timeout=2
            )
            status["notify_send_available"] = True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Check D-Bus availability
        try:
            subprocess.run(
                ["dbus-send", "--version"],
                check=True,
                capture_output=True,
                timeout=2
            )
            status["dbus_available"] = True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return status

    def refresh_theme(self) -> None:
        """
        @brief Refresh notification widget theming after color changes

        Call this method when the color scheme changes to update
        notification widget appearance.
        """
        self._widget_defaults.clear()
        # Also refresh popup manager if available
        if self._popup_manager:
            # Popup manager will get new colors from color_manager automatically
            logger.debug("Popup notification theme will be refreshed on next notification")
        logger.debug("Notification theme refreshed")


def create_notification_manager(color_manager: ColorManager) -> NotificationManager:
    """
    @brief Factory function to create a notification manager instance
    @param color_manager: Color management instance
    @return Configured NotificationManager instance
    """
    try:
        manager = NotificationManager(color_manager)
        logger.info("Notification manager created successfully")
        return manager
    except Exception as e:
        logger.error(f"Failed to create notification manager: {e}")
        # Return a minimal manager that logs errors
        return NotificationManager(color_manager)


# Convenience functions for direct notification sending
def send_qtile_notification(
    title: str,
    message: str,
    timeout: int = 5000,
    urgency: str = "normal"
) -> None:
    """
    @brief Convenience function to send a notification directly
    @param title: Notification title
    @param message: Notification message
    @param timeout: Timeout in milliseconds
    @param urgency: Urgency level

    This is a simplified interface for sending notifications without
    requiring a NotificationManager instance.
    """
    # Try multiple methods in order of preference
    success = False

    # Method 1: Try qtile built-in (if working)
    try:
        from libqtile.utils import send_notification
        send_notification(title, message, timeout=timeout//1000)
        success = True
        logger.debug(f"Direct notification sent via qtile: {title}")
    except Exception as e:
        logger.debug(f"Qtile direct notification failed: {e}")

    # Method 2: Try notify-send as fallback
    if not success:
        try:
            subprocess.run([
                "notify-send",
                "-t", str(timeout),
                "-u", urgency,
                title,
                message
            ], check=True, timeout=5)
            success = True
            logger.debug(f"Direct notification sent via notify-send: {title}")
        except Exception as e:
            logger.debug(f"notify-send fallback failed: {e}")

    if not success:
        logger.warning(f"All notification methods failed for: {title}")


def notify_qtile_event(event_type: str, details: str = "") -> None:
    """
    @brief Send a notification about a qtile event
    @param event_type: Type of qtile event (startup, restart, etc.)
    @param details: Additional event details

    Specialized function for notifying about qtile system events.
    """
    title = f"Qtile {event_type.title()}"
    message = details if details else f"Qtile {event_type} completed"

    try:
        send_qtile_notification(title, message, timeout=3000)
    except Exception as e:
        logger.debug(f"Could not send qtile event notification: {e}")
