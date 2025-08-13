#!/usr/bin/env python3
"""
Qtile-Extras Based Popup Notification System

@brief Wayland-compatible popup notifications using qtile-extras
@author Andrath

This module provides popup notifications using qtile-extras popup toolkit,
which is compatible with both X11 and Wayland.

Features:
- Cross-platform compatibility (X11 and Wayland)
- Configurable positioning and styling
- Multiple notification stacking
- Auto-dismiss with configurable timeouts
- Urgency-based styling
- Theme integration with color manager

@note This module follows modern Python 3.10+ standards
"""

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from libqtile import qtile
from libqtile.log_utils import logger

try:
    from qtile_extras.popup.toolkit import (
        PopupRelativeLayout,
        PopupText
    )
    QTILE_EXTRAS_AVAILABLE = True
except ImportError:
    QTILE_EXTRAS_AVAILABLE = False
    PopupRelativeLayout = None
    PopupText = None


@dataclass
class NotificationConfig:
    """Configuration for popup notifications"""
    width: int = 350
    height: int = 100
    margin_x: int = 20
    margin_y: int = 60
    spacing: int = 10
    timeout_normal: int = 5000
    timeout_low: int = 3000
    timeout_critical: int = 0  # Never timeout
    max_notifications: int = 5
    corner: str = "top_right"  # top_right, top_left, bottom_right, bottom_left
    background: str = "1e1e1e"
    background_urgent: str = "3e1e1e"
    foreground: str = "ffffff"
    foreground_urgent: str = "ff6666"
    border_width: int = 2
    border_color: str = "555555"
    border_color_urgent: str = "ff0000"
    font_size: int = 12
    title_font_size: int = 14


@dataclass
class NotificationPopup:
    """Represents a single popup notification"""
    title: str
    message: str
    urgency: str
    timeout: float
    created_at: float
    popup_layout: Optional[Any] = None
    x: int = 0
    y: int = 0


class QtileExtrasPopupManager:
    """
    @brief Popup notification manager using qtile-extras

    Provides cross-platform popup notifications using qtile-extras popup toolkit.
    """

    def __init__(self, color_manager: Any):
        """
        @brief Initialize popup manager
        @param color_manager: Color management instance for theming
        """
        self.color_manager = color_manager
        self.config = NotificationConfig()
        self.active_popups: List[NotificationPopup] = []
        self._cleanup_scheduled = False

        if not QTILE_EXTRAS_AVAILABLE:
            logger.warning("qtile-extras not available - popup notifications disabled")

    def configure(self, config: Dict[str, Any]) -> None:
        """
        @brief Configure popup notification settings
        @param config: Configuration dictionary
        """
        for key, value in config.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

        # Update colors from color manager
        self._update_colors()
        logger.info("QtileExtras popup manager configured")

    def _update_colors(self) -> None:
        """Update colors from color manager"""
        try:
            colors = self.color_manager.get_colors()
            color_dict = colors.get("colors", {})
            special = colors.get("special", {})

            # Update background and foreground colors
            self.config.background = special.get("background", "#1e1e1e").lstrip("#")
            self.config.foreground = special.get("foreground", "#ffffff").lstrip("#")

            # Set urgent colors based on theme
            self.config.background_urgent = color_dict.get("color1", "#3e1e1e").lstrip("#")
            self.config.foreground_urgent = color_dict.get("color9", "#ff6666").lstrip("#")
            self.config.border_color = color_dict.get("color8", "#555555").lstrip("#")
            self.config.border_color_urgent = color_dict.get("color1", "#ff0000").lstrip("#")

        except Exception as e:
            logger.debug(f"Failed to update colors from color manager: {e}")

    def show_notification(
        self,
        title: str,
        message: str,
        urgency: str = "normal",
        timeout: int = 5000
    ) -> None:
        """
        @brief Show a popup notification
        @param title: Notification title
        @param message: Notification message
        @param urgency: Urgency level (low, normal, critical)
        @param timeout: Timeout in milliseconds (0 = no timeout)
        """
        if not QTILE_EXTRAS_AVAILABLE:
            logger.warning("qtile-extras not available - cannot show popup")
            return

        if not qtile:
            logger.warning("Qtile not available - cannot show popup")
            return

        # Convert timeout to seconds
        timeout_seconds = timeout / 1000.0 if timeout > 0 else 0.0

        # Apply urgency-specific timeouts
        if urgency == "critical":
            timeout_seconds = self.config.timeout_critical / 1000.0
        elif urgency == "low":
            timeout_seconds = self.config.timeout_low / 1000.0
        elif timeout_seconds <= 0:
            timeout_seconds = self.config.timeout_normal / 1000.0

        # Limit active notifications
        while len(self.active_popups) >= self.config.max_notifications:
            self._dismiss_oldest()

        # Calculate position for this notification
        stack_index = len(self.active_popups)
        x, y = self._calculate_position(stack_index)

        # Create notification popup
        try:
            popup_layout = self._create_popup_layout(title, message, urgency, x, y)

            notification = NotificationPopup(
                title=title,
                message=message,
                urgency=urgency,
                timeout=timeout_seconds,
                created_at=time.time(),
                popup_layout=popup_layout,
                x=x,
                y=y
            )

            # Show the popup
            popup_layout.show()
            self.active_popups.append(notification)

            logger.info(f"Showed qtile-extras popup: {title}")

            # Schedule cleanup if needed
            if not self._cleanup_scheduled:
                self._schedule_cleanup()

        except Exception as e:
            logger.error(f"Failed to show qtile-extras popup: {e}")

    def _create_popup_layout(
        self,
        title: str,
        message: str,
        urgency: str,
        x: int,
        y: int
    ) -> Any:
        """
        @brief Create popup layout for notification
        @param title: Notification title
        @param message: Notification message
        @param urgency: Urgency level
        @param x: X position
        @param y: Y position
        @return PopupRelativeLayout instance
        """
        # Choose colors based on urgency
        if urgency == "critical":
            bg_color = self.config.background_urgent
            fg_color = self.config.foreground_urgent
            border_color = self.config.border_color_urgent
        else:
            bg_color = self.config.background
            fg_color = self.config.foreground
            border_color = self.config.border_color

        # Create controls for the popup
        controls = []

        # Title text
        if title:
            controls.append(
                PopupText(
                    text=title,
                    pos_x=0.05,
                    pos_y=0.1,
                    width=0.9,
                    height=0.3,
                    fontsize=self.config.title_font_size,
                    foreground=fg_color,
                    font_family="sans-serif",
                    font_weight="bold",
                    name="title"
                )
            )

        # Message text
        if message:
            # Adjust position based on whether we have a title
            msg_y = 0.5 if title else 0.2
            msg_height = 0.4 if title else 0.6

            controls.append(
                PopupText(
                    text=message,
                    pos_x=0.05,
                    pos_y=msg_y,
                    width=0.9,
                    height=msg_height,
                    fontsize=self.config.font_size,
                    foreground=fg_color,
                    font_family="sans-serif",
                    wrap=True,
                    name="message"
                )
            )

        # Create popup layout
        popup = PopupRelativeLayout(
            qtile,
            x=x,
            y=y,
            width=self.config.width,
            height=self.config.height,
            controls=controls,
            background=bg_color,
            border=border_color,
            border_width=self.config.border_width,
            initial_focus=None,
            close_on_click=True,
            opacity=0.95
        )

        return popup

    def _calculate_position(self, stack_index: int) -> tuple[int, int]:
        """
        @brief Calculate position for notification
        @param stack_index: Index in the notification stack
        @return Tuple of (x, y) coordinates
        """
        try:
            # Get screen dimensions
            if qtile and qtile.current_screen:
                screen_width = qtile.current_screen.width
                screen_height = qtile.current_screen.height
            else:
                # Fallback to reasonable defaults
                screen_width = 1920
                screen_height = 1080

            width = self.config.width
            height = self.config.height
            margin_x = self.config.margin_x
            margin_y = self.config.margin_y
            spacing = self.config.spacing

            # Calculate base position based on corner
            if self.config.corner == "top_right":
                x = screen_width - width - margin_x
                y = margin_y + (stack_index * (height + spacing))
            elif self.config.corner == "top_left":
                x = margin_x
                y = margin_y + (stack_index * (height + spacing))
            elif self.config.corner == "bottom_right":
                x = screen_width - width - margin_x
                y = screen_height - margin_y - height - (stack_index * (height + spacing))
            elif self.config.corner == "bottom_left":
                x = margin_x
                y = screen_height - margin_y - height - (stack_index * (height + spacing))
            else:
                # Default to top_right
                x = screen_width - width - margin_x
                y = margin_y + (stack_index * (height + spacing))

            # Ensure popup stays on screen
            x = max(0, min(x, screen_width - width))
            y = max(0, min(y, screen_height - height))

            return (x, y)

        except Exception as e:
            logger.debug(f"Error calculating position: {e}")
            return (100, 100)

    def _dismiss_oldest(self) -> None:
        """Dismiss the oldest notification"""
        if self.active_popups:
            oldest = self.active_popups.pop(0)
            try:
                if oldest.popup_layout:
                    oldest.popup_layout.kill()
            except Exception as e:
                logger.debug(f"Error dismissing popup: {e}")

    def _schedule_cleanup(self) -> None:
        """Schedule cleanup of expired notifications"""
        if not self._cleanup_scheduled:
            self._cleanup_scheduled = True
            # Schedule cleanup in 1 second
            if qtile:
                qtile.call_later(1.0, self._cleanup_expired)

    def _cleanup_expired(self) -> None:
        """Clean up expired notifications"""
        self._cleanup_scheduled = False
        current_time = time.time()
        expired = []

        for notification in self.active_popups:
            if (notification.timeout > 0 and
                current_time - notification.created_at > notification.timeout):
                expired.append(notification)

        # Remove expired notifications
        for notification in expired:
            try:
                if notification.popup_layout:
                    notification.popup_layout.kill()
                self.active_popups.remove(notification)
            except Exception as e:
                logger.debug(f"Error cleaning up expired notification: {e}")

        # Reposition remaining notifications
        self._reposition_notifications()

        # Schedule next cleanup if there are still active notifications
        if self.active_popups:
            self._schedule_cleanup()

    def _reposition_notifications(self) -> None:
        """Reposition all active notifications"""
        for i, notification in enumerate(self.active_popups):
            try:
                new_x, new_y = self._calculate_position(i)
                if notification.popup_layout and hasattr(notification.popup_layout, 'place'):
                    notification.popup_layout.place(new_x, new_y)
                    notification.x = new_x
                    notification.y = new_y
            except Exception as e:
                logger.debug(f"Error repositioning notification: {e}")

    def dismiss_all(self) -> None:
        """Dismiss all active notifications"""
        for notification in self.active_popups[:]:
            try:
                if notification.popup_layout:
                    notification.popup_layout.kill()
            except Exception as e:
                logger.debug(f"Error dismissing notification: {e}")

        self.active_popups.clear()
        logger.info("Dismissed all popup notifications")

    def get_status(self) -> Dict[str, Any]:
        """
        @brief Get popup manager status
        @return Status dictionary
        """
        return {
            "active_notifications": len(self.active_popups),
            "max_notifications": self.config.max_notifications,
            "corner": self.config.corner,
            "qtile_extras_available": QTILE_EXTRAS_AVAILABLE,
            "cleanup_scheduled": self._cleanup_scheduled,
        }


def create_qtile_extras_popup_manager(color_manager: Any) -> QtileExtrasPopupManager:
    """
    @brief Factory function to create qtile-extras popup manager
    @param color_manager: Color management instance
    @return QtileExtrasPopupManager instance
    """
    try:
        manager = QtileExtrasPopupManager(color_manager)
        logger.info("QtileExtras popup manager created successfully")
        return manager
    except Exception as e:
        logger.error(f"Failed to create qtile-extras popup manager: {e}")
        # Return a dummy manager that logs errors
        return QtileExtrasPopupManager(color_manager)


def test_qtile_extras_popup(color_manager: Any = None) -> None:
    """
    @brief Test function for qtile-extras popup system
    @param color_manager: Optional color manager for testing
    """
    if not QTILE_EXTRAS_AVAILABLE:
        print("❌ qtile-extras not available")
        return

    if not color_manager:
        # Create dummy color manager for testing
        class DummyColorManager:
            def get_colors(self):
                return {
                    "colors": {
                        "color0": "#000000",
                        "color1": "#ff0000",
                        "color8": "#808080",
                        "color9": "#ff6666",
                    },
                    "special": {
                        "background": "#1e1e1e",
                        "foreground": "#ffffff",
                    }
                }
        color_manager = DummyColorManager()

    try:
        manager = create_qtile_extras_popup_manager(color_manager)

        # Configure manager
        config = {
            "width": 350,
            "height": 100,
            "corner": "top_right",
            "timeout_normal": 3000,
        }
        manager.configure(config)

        # Test different notification types
        manager.show_notification(
            "Test Notification",
            "This is a test of the qtile-extras popup system",
            "normal"
        )

        print("✅ QtileExtras popup test completed")

    except Exception as e:
        print(f"❌ QtileExtras popup test failed: {e}")
        import traceback
        traceback.print_exc()
