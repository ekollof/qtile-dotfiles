#!/usr/bin/env python3
"""
Custom Notify Widget with Popup Forwarding

@brief Custom Notify widget that forwards notifications to popup manager
@author Andrath

This widget extends the standard qtile Notify widget to forward notifications
to a popup manager instead of displaying them in the status bar.

Features:
- Maintains D-Bus notification server functionality
- Forwards notifications to popup manager when enabled
- Falls back to standard bar display if popup fails
- Compatible with libnotify and notify-send
"""

import os
from typing import Any, Dict

from libqtile import widget
from libqtile.log_utils import logger
from .simple_popup_notifications import show_popup_notification


class PopupNotifyWidget(widget.Notify):
    """
    Simple Notify widget that shows popup notifications

    This widget extends the standard qtile Notify widget to show popup
    notifications instead of (or in addition to) bar notifications.
    """

    defaults = [
        ("show_in_bar", False, "Also show notifications in the status bar"),
        ("show_popups", True, "Show popup notifications"),
    ]

    def __init__(self, **config: Any):
        """Initialize popup notify widget"""
        super().__init__(**config)
        self.add_defaults(PopupNotifyWidget.defaults)

        # Hide bar text if not showing in bar
        if not self.show_in_bar:
            self.text = ""

    def update(self, notification: Any) -> None:
        """Override update method to show popup notifications (called by D-Bus)"""

        try:
            if self.show_popups:
                # Extract notification data
                title = getattr(notification, 'summary', 'Notification')
                message = getattr(notification, 'body', '')

                # Map urgency levels (D-Bus uses 0=low, 1=normal, 2=critical)
                # Extract urgency from hints as per D-Bus specification
                try:
                    hints = getattr(notification, 'hints', {})
                    urgency_hint = hints.get("urgency") if hints else None
                    raw_urgency = getattr(urgency_hint, 'value', 1) if urgency_hint else 1
                except:
                    raw_urgency = 1
                urgency_map = {0: 'low', 1: 'normal', 2: 'critical'}
                urgency = urgency_map.get(raw_urgency, 'normal')

                # Extract icon information from D-Bus notification
                icon_path = None
                try:
                    # Check app_icon attribute (this is where notify-send puts icons)
                    icon_path = getattr(notification, 'app_icon', None)

                    # Fallback to hints if app_icon is empty
                    if not icon_path:
                        hints = getattr(notification, 'hints', {})
                        if hints:
                            icon_path = (hints.get('image-path') or
                                       hints.get('image_path') or
                                       hints.get('icon_data'))

                    # Validate icon path exists
                    if icon_path and not os.path.exists(str(icon_path)):
                        logger.debug(f"Icon path not found: {icon_path}")
                        icon_path = None
                    elif icon_path:
                        logger.debug(f"Found valid icon: {icon_path}")

                except Exception as e:
                    logger.warning(f"Error extracting icon: {e}")
                    icon_path = None

                # Show popup using simple popup system
                show_popup_notification(title, message, urgency, icon_path)
            else:
                # show_popups is False - not showing popup
                pass

            # Optionally also show in bar
            if self.show_in_bar:
                super().update(notification)

        except Exception as e:
            logger.error(f"Error in popup notification update: {e}")
            # Fall back to bar display on error
            super().update(notification)

    def clear(self, notification=None) -> None:
        """Clear notification display"""
        if self.show_in_bar:
            super().clear(notification)

    def cmd_test_popup_notification(self) -> None:
        """Command to test popup notification functionality"""
        show_popup_notification(
            "Test Popup",
            "This is a test popup notification",
            "normal"
        )


def create_popup_notify_widget(**kwargs: Any) -> PopupNotifyWidget:
    """
    Factory function to create a popup notify widget

    Args:
        **kwargs: Widget configuration options

    Returns:
        Configured PopupNotifyWidget instance
    """
    try:
        widget_instance = PopupNotifyWidget(**kwargs)
        logger.info("Popup notify widget created successfully")
        return widget_instance

    except Exception as e:
        logger.error(f"Failed to create popup notify widget: {e}")
        # Return standard notify widget as fallback
        return widget.Notify(**kwargs)
