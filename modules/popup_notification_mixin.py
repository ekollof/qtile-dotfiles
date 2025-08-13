#!/usr/bin/env python3
"""
Popup Notification Mixin

@brief Mixin to add popup functionality to notification widgets
@author Andrath

This mixin adds popup notification capabilities to any notification widget,
allowing notifications to appear as popups instead of or in addition to
the traditional bar display.

Features:
- Works with existing Notify widgets
- Uses qtile-extras for cross-platform compatibility
- Configurable popup positioning and styling
- Multiple notification stacking
- Auto-dismiss functionality
- Theme integration

@note This module follows modern Python 3.10+ standards
"""

from typing import Any, Dict, Optional

from libqtile.log_utils import logger

try:
    from .qtile_extras_notifications import (
        QtileExtrasPopupManager,
        create_qtile_extras_popup_manager
    )
    POPUP_MANAGER_AVAILABLE = True
except ImportError:
    POPUP_MANAGER_AVAILABLE = False
    QtileExtrasPopupManager = None
    create_qtile_extras_popup_manager = None


class PopupNotificationMixin:
    """
    @brief Mixin to add popup functionality to notification widgets

    This mixin can be applied to any notification widget to add popup
    functionality using qtile-extras.
    """

    def __init_popup_mixin__(self, color_manager: Any, **popup_config: Any) -> None:
        """
        @brief Initialize popup mixin
        @param color_manager: Color management instance
        @param popup_config: Popup configuration options
        """
        self._popup_manager: Optional[QtileExtrasPopupManager] = None
        self._popup_enabled = popup_config.get("enable_popups", True)
        self._popup_fallback_to_bar = popup_config.get("fallback_to_bar", True)
        self._popup_config = popup_config.copy()
        self._color_manager = color_manager

        # Initialize popup manager if available and enabled
        if self._popup_enabled and POPUP_MANAGER_AVAILABLE:
            self._initialize_popup_manager()

    def _initialize_popup_manager(self) -> None:
        """Initialize the popup manager"""
        if not self._popup_manager and POPUP_MANAGER_AVAILABLE:
            try:
                self._popup_manager = create_qtile_extras_popup_manager(self._color_manager)

                # Configure popup manager
                config = {
                    "width": self._popup_config.get("popup_width", 350),
                    "height": self._popup_config.get("popup_height", 100),
                    "margin_x": self._popup_config.get("popup_margin_x", 20),
                    "margin_y": self._popup_config.get("popup_margin_y", 60),
                    "spacing": self._popup_config.get("popup_spacing", 10),
                    "corner": self._popup_config.get("popup_corner", "top_right"),
                    "max_notifications": self._popup_config.get("popup_max_notifications", 5),
                    "timeout_normal": self._popup_config.get("popup_timeout_normal", 5000),
                    "timeout_low": self._popup_config.get("popup_timeout_low", 3000),
                    "timeout_critical": self._popup_config.get("popup_timeout_critical", 0),
                }

                self._popup_manager.configure(config)
                logger.info("Popup notification mixin initialized")

            except Exception as e:
                logger.error(f"Failed to initialize popup manager: {e}")
                self._popup_manager = None

    def _show_popup_notification(
        self,
        title: str,
        message: str,
        urgency: str = "normal",
        timeout: int = 5000
    ) -> bool:
        """
        @brief Show notification as popup
        @param title: Notification title
        @param message: Notification message
        @param urgency: Urgency level
        @param timeout: Timeout in milliseconds
        @return True if popup was shown successfully
        """
        if not self._popup_enabled or not self._popup_manager:
            return False

        try:
            self._popup_manager.show_notification(title, message, urgency, timeout)
            logger.debug(f"Showed popup notification: {title}")
            return True
        except Exception as e:
            logger.warning(f"Failed to show popup notification: {e}")
            return False

    def _extract_notification_data(self, notification: Any) -> Dict[str, Any]:
        """
        @brief Extract data from notification object
        @param notification: Notification object from qtile
        @return Dictionary with notification data
        """
        try:
            # Extract basic information
            title = getattr(notification, 'summary', '') or getattr(notification, 'title', 'Notification')
            message = getattr(notification, 'body', '') or getattr(notification, 'message', '')

            # Map urgency levels (qtile uses integers: 0=low, 1=normal, 2=critical)
            urgency_map = {0: 'low', 1: 'normal', 2: 'critical'}
            urgency_level = getattr(notification, 'urgency', 1)
            urgency = urgency_map.get(urgency_level, 'normal')

            # Get timeout (convert from milliseconds, -1 means default)
            timeout = getattr(notification, 'timeout', 5000)
            if timeout < 0:
                timeout = 5000

            return {
                'title': title,
                'message': message,
                'urgency': urgency,
                'timeout': timeout
            }

        except Exception as e:
            logger.debug(f"Error extracting notification data: {e}")
            return {
                'title': 'Notification',
                'message': str(notification) if notification else '',
                'urgency': 'normal',
                'timeout': 5000
            }

    def display_with_popup(self, notification: Any) -> None:
        """
        @brief Display notification with popup support
        @param notification: Notification object to display

        This method should be called from the widget's display method
        to add popup functionality.
        """
        # Extract notification data
        notif_data = self._extract_notification_data(notification)

        # Try to show popup first
        popup_shown = False
        if self._popup_enabled:
            popup_shown = self._show_popup_notification(
                notif_data['title'],
                notif_data['message'],
                notif_data['urgency'],
                notif_data['timeout']
            )

        # Fall back to bar display if configured or popup failed
        if not popup_shown and self._popup_fallback_to_bar:
            # Call the original display method if it exists
            if hasattr(super(), 'display'):
                super().display(notification)  # type: ignore

    def configure_popup(self, **config: Any) -> None:
        """
        @brief Configure popup settings
        @param config: Configuration options
        """
        self._popup_config.update(config)

        # Update popup manager if it exists
        if self._popup_
