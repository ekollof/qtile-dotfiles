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

from pathlib import Path
from typing import Any

from libqtile import widget
from libqtile.log_utils import logger
from libqtile.command import base
from .simple_popup_notifications import show_popup_notification

try:
    import dbus
    DBUS_AVAILABLE = True
except ImportError:
    DBUS_AVAILABLE = False
    logger.warning("D-Bus not available - notification actions will not work")


class PopupNotifyWidget(widget.Notify):
    """
    @brief Notify widget that shows popup notifications

    This widget extends the standard qtile Notify widget to show popup
    notifications instead of (or in addition to) bar notifications.
    Maintains full D-Bus compatibility with libnotify.

    @param show_in_bar: Whether to also show notifications in status bar
    @param show_popups: Whether to show popup notifications
    """

    defaults = [
        ("show_in_bar", False, "Also show notifications in the status bar"),
        ("show_popups", True, "Show popup notifications"),
        ("enable_actions", True, "Enable notification action buttons"),
    ]

    def __init__(self, **config: Any) -> None:
        """
        @brief Initialize popup notify widget
        @param config: Widget configuration parameters
        """
        super().__init__(**config)
        self.add_defaults(PopupNotifyWidget.defaults)

        # Hide bar text if not showing in bar
        if not self.show_in_bar:
            self.text = ""

    def update(self, notification: Any) -> None:
        """
        @brief Override update method to show popup notifications
        @param notification: D-Bus notification object from libnotify
        """

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

                # Extract action buttons if enabled
                actions = []
                if self.enable_actions:
                    try:
                        raw_actions = getattr(notification, 'actions', [])
                        # Actions come in pairs: [action_key, action_label, ...]
                        for i in range(0, len(raw_actions), 2):
                            if i + 1 < len(raw_actions):
                                action_key = raw_actions[i]
                                action_label = raw_actions[i + 1]
                                actions.append((action_key, action_label))

                        if actions:
                            logger.debug(f"Found {len(actions)} action buttons: {actions}")
                    except Exception as e:
                        logger.warning(f"Error extracting actions: {e}")

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

                    # Validate icon path exists using pathlib
                    if icon_path and not Path(str(icon_path)).exists():
                        logger.debug(f"Icon path not found: {icon_path}")
                        icon_path = None
                    elif icon_path:
                        logger.debug(f"Found valid icon: {icon_path}")

                except Exception as e:
                    logger.warning(f"Error extracting icon: {e}")
                    icon_path = None

                # Show popup using simple popup system
                show_popup_notification(
                    title,
                    message,
                    urgency,
                    icon_path,
                    actions=actions,
                    notification_id=getattr(notification, 'id', 0),
                    callback=self._handle_action_callback if actions else None
                )
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

    def clear(self, notification: Any = None) -> None:
        """
        @brief Clear notification display
        @param notification: Optional notification object to clear
        """
        if self.show_in_bar:
            super().clear(notification)

    def _handle_action_callback(self, notification_id: int, action_key: str) -> None:
        """
        @brief Handle action button click callback using qtile's notification service
        @param notification_id: D-Bus notification ID
        @param action_key: Action key that was clicked
        """
        try:
            # Use qtile's built-in notification service for proper D-Bus handling
            from libqtile import notify
            if hasattr(notify, 'notifier') and notify.notifier and hasattr(notify.notifier, '_service'):
                # Send ActionInvoked signal first
                notify.notifier._service.ActionInvoked(notification_id, action_key)
                logger.info(f"Action invoked via qtile service: ID={notification_id}, action={action_key}")

                # Send NotificationClosed signal to complete the D-Bus interaction
                notify.notifier._service.NotificationClosed(notification_id, 2)  # 2 = dismissed by user action
                logger.info(f"Notification closed via qtile service: ID={notification_id}")
            else:
                logger.warning("Qtile notification service not available")

        except Exception as e:
            logger.error(f"Failed to invoke action via qtile service: {e}")

    @base.expose_command()
    def test_popup_notification(self) -> None:
        """
        @brief Command to test popup notification functionality
        @return None
        """
        show_popup_notification(
            "Test Popup",
            "This is a test popup notification",
            "normal"
        )

    @base.expose_command()
    def test_action_notification(self) -> None:
        """
        @brief Test notification with action buttons
        @return None
        """
        show_popup_notification(
            "Action Test",
            "This notification has action buttons",
            "normal",
            None,
            actions=[("accept", "Accept"), ("decline", "Decline")],
            notification_id=999,
            callback=self._handle_action_callback
        )


def create_popup_notify_widget(**kwargs: Any) -> PopupNotifyWidget:
    """
    @brief Factory function to create a popup notify widget
    @param kwargs: Keyword arguments to pass to the widget
    @return PopupNotifyWidget instance
    @throws Exception: When widget creation fails
    """
    try:
        widget_instance = PopupNotifyWidget(**kwargs)
        logger.info("Popup notify widget created successfully")
        return widget_instance

    except Exception as e:
        logger.error(f"Failed to create popup notify widget: {e}")
        # Return standard notify widget as fallback
        return widget.Notify(**kwargs)
