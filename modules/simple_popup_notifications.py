#!/usr/bin/env python3
"""
Simple Popup Notifications using QtileExtras

@brief Simple hook-based popup notifications using qtile-extras
@author Andrath

This module provides a simple way to show popup notifications in the top-right
corner using qtile-extras popup toolkit. It works alongside the standard Notify
widget to provide cross-platform popup notifications.

Features:
- Cross-platform (X11 and Wayland)
- Simple hook-based approach
- Configurable positioning and styling
- Urgency-based styling
- Auto-dismiss with timeouts
- Multiple notification stacking

Usage:
    from modules.simple_popup_notifications import setup_popup_notifications
    setup_popup_notifications(qtile, color_manager)
"""

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from libqtile import qtile
from libqtile.log_utils import logger
from modules.font_utils import get_available_font
from modules.dpi_utils import scale_font, scale_size

try:
    import libqtile.notify
    NOTIFY_AVAILABLE = True
except ImportError:
    NOTIFY_AVAILABLE = False
    logger.warning("libqtile.notify not available")

try:
    from qtile_extras.popup.toolkit import PopupRelativeLayout, PopupText
    QTILE_EXTRAS_AVAILABLE = True
except ImportError:
    QTILE_EXTRAS_AVAILABLE = False
    logger.warning("qtile-extras not available - popup notifications disabled")


@dataclass
class PopupNotification:
    """Simple notification data structure"""
    title: str
    message: str
    urgency: str
    created_at: float
    timeout: float
    popup_layout: Optional[Any] = None


class SimplePopupManager:
    """
    @brief Simple popup notification manager

    Manages popup notifications using qtile-extras toolkit with a simple
    hook-based approach that works alongside the standard Notify widget.
    """

    def __init__(self, color_manager: Any):
        """Initialize popup manager"""
        self.color_manager = color_manager
        self.active_notifications: List[PopupNotification] = []
        self.max_notifications = 5
        self.cleanup_scheduled = False
        self.qtile_config = None  # Will be set during configuration

        # Default configuration with DPI scaling
        self.config = {
            "width": scale_size(400),
            "height": scale_size(120),
            "margin_x": scale_size(20),
            "margin_y": scale_size(20),  # Will be adjusted for bar height
            "spacing": scale_size(10),
            "corner": "top_right",
        }

        self._update_colors()

    def _update_colors(self) -> None:
        """Update colors from color manager"""
        try:
            colors = self.color_manager.get_colors()
            color_dict = colors.get("colors", {})
            special = colors.get("special", {})

            self.colors = {
                "bg_normal": special.get("background", "#1e1e1e").lstrip("#"),
                "fg_normal": special.get("foreground", "#ffffff").lstrip("#"),
                "bg_urgent": color_dict.get("color1", "#3e1e1e").lstrip("#"),
                "fg_urgent": color_dict.get("color9", "#ff6666").lstrip("#"),
                "bg_low": special.get("background", "#1e1e1e").lstrip("#"),
                "fg_low": color_dict.get("color8", "#888888").lstrip("#"),
                "border_normal": color_dict.get("color8", "#555555").lstrip("#"),
                "border_urgent": color_dict.get("color1", "#ff0000").lstrip("#"),
            }
        except Exception as e:
            logger.debug(f"Failed to update colors: {e}")
            # Fallback colors
            self.colors = {
                "bg_normal": "1e1e1e", "fg_normal": "ffffff",
                "bg_urgent": "3e1e1e", "fg_urgent": "ff6666",
                "bg_low": "1e1e1e", "fg_low": "888888",
                "border_normal": "555555", "border_urgent": "ff0000",
            }

    def _adjust_positioning(self) -> None:
        """Adjust popup positioning to respect bar height and gaps"""
        if not self.qtile_config:
            return

        try:
            # Get bar height and layout margins
            bar_height = self.qtile_config.bar_settings["height"]
            layout_margin = self.qtile_config.layout_defaults["margin"]

            # Adjust margin_y to account for bar and gap
            if self.config["corner"].startswith("top"):
                self.config["margin_y"] = bar_height + layout_margin + scale_size(10)
            else:
                self.config["margin_y"] = layout_margin + scale_size(10)

            # Adjust margin_x to account for gap
            self.config["margin_x"] = layout_margin + scale_size(10)

            logger.debug(f"Adjusted positioning: margin_x={self.config['margin_x']}, margin_y={self.config['margin_y']}")

        except Exception as e:
            logger.warning(f"Could not adjust positioning: {e}")
            # Keep defaults

    def show_notification(self, title: str, message: str, urgency: str = "normal") -> None:
        """
        @brief Show a popup notification
        @param title: Notification title
        @param message: Notification message
        @param urgency: Urgency level (low, normal, critical)
        """
        if not QTILE_EXTRAS_AVAILABLE or not qtile:
            return

        # Determine timeout based on urgency
        if urgency == "critical":
            timeout = self.config["timeout_critical"]
        elif urgency == "low":
            timeout = self.config["timeout_low"]
        else:
            timeout = self.config["timeout_normal"]

        # Limit active notifications
        while len(self.active_notifications) >= self.max_notifications:
            self._dismiss_oldest()

        # Calculate position
        stack_index = len(self.active_notifications)
        x, y = self._calculate_position(stack_index)

        # Create notification object
        notification = PopupNotification(
            title=title,
            message=message,
            urgency=urgency,
            created_at=time.time(),
            timeout=timeout
        )

        # Create and show popup
        try:
            popup_layout = self._create_popup(notification, x, y)
            # Use qtile-extras positioning: relative_to=3 is top-right corner
            popup_layout.show(
                x=x,
                y=y,
                relative_to=3,  # Top-right corner
                relative_to_bar=True  # Auto-adjust for bars and gaps
            )

            notification.popup_layout = popup_layout
            self.active_notifications.append(notification)

            logger.info(f"Showed popup notification: {title}")

            # Schedule cleanup if needed
            if timeout > 0 and not self.cleanup_scheduled:
                self._schedule_cleanup()

        except Exception as e:
            logger.error(f"Failed to show popup notification: {e}")

    def _create_popup(self, notification: PopupNotification, x: int, y: int) -> PopupRelativeLayout:
        """Create popup layout for notification"""
        # Choose colors based on urgency
        if notification.urgency == "critical":
            bg_color = self.colors["bg_urgent"]
            fg_color = self.colors["fg_urgent"]
            border_color = self.colors["border_urgent"]
        elif notification.urgency == "low":
            bg_color = self.colors["bg_low"]
            fg_color = self.colors["fg_low"]
            border_color = self.colors["border_normal"]
        else:
            bg_color = self.colors["bg_normal"]
            fg_color = self.colors["fg_normal"]
            border_color = self.colors["border_normal"]



        # Create controls
        controls = []

        # Get theme-aware font
        font_family = "sans-serif"
        if self.qtile_config and hasattr(self.qtile_config, 'preferred_font'):
            font_family = get_available_font(self.qtile_config.preferred_font)

        # Title (if present)
        if notification.title:
            controls.append(
                PopupText(
                    text=notification.title,
                    pos_x=0.05,
                    pos_y=0.1,
                    width=0.9,
                    height=0.35,
                    fontsize=scale_font(16),
                    foreground=fg_color,
                    font_family=font_family,
                    font_weight="bold",
                    h_align="left",
                    v_align="top",
                    wrap=True,
                )
            )

        # Message
        # Message text
        if notification.message:
            msg_y = 0.5 if notification.title else 0.2
            msg_height = 0.4 if notification.title else 0.6

            controls.append(
                PopupText(
                    text=notification.message,
                    pos_x=0.05,
                    pos_y=msg_y,
                    width=0.9,
                    height=msg_height,
                    fontsize=scale_font(14),
                    foreground=fg_color,
                    font_family=font_family,
                    h_align="left",
                    v_align="top",
                    wrap=True,
                )
            )

        # Create popup layout (without x,y in constructor)
        popup = PopupRelativeLayout(
            qtile,
            width=self.config["width"],
            height=self.config["height"],
            controls=controls,
            background=bg_color,
            border=border_color,
            border_width=2,
            initial_focus=None,
            close_on_click=True,
            opacity=0.95
        )

        return popup

    def _calculate_position(self, stack_index: int) -> tuple[int, int]:
        """Calculate position offset for notification using qtile-extras positioning"""
        try:
            margin_x = self.config["margin_x"]
            margin_y = self.config["margin_y"]
            spacing = self.config["spacing"]
            height = self.config["height"]
            width = self.config["width"]

            # Get current screen dimensions for bounds checking
            if qtile and qtile.current_screen:
                screen_height = qtile.current_screen.height
            else:
                screen_height = 1080

            # For qtile-extras relative positioning:
            # relative_to=3 (top-right) with relative_to_bar=True
            # x,y are offsets from the top-right corner (after bar adjustment)

            # X offset: negative margin to move left from right edge
            # For relative_to=3, negative x moves popup left to stay on screen
            x = -margin_x

            # Y offset: margin from top + stack position
            y = margin_y + (stack_index * (height + spacing))

            # Bounds checking: if notification would go below screen, limit stack
            max_y = screen_height - height - margin_y
            if y > max_y:
                # Calculate how many notifications can fit
                max_notifications = max(1, int((max_y - margin_y) / (height + spacing)) + 1)
                # Reposition within bounds
                y = margin_y + ((stack_index % max_notifications) * (height + spacing))

            logger.debug(f"Positioning notification at offset x={x}, y={y}")

            return (x, y)
        except Exception as e:
            logger.error(f"Position calculation error: {e}")
            return (-370, 60)

    def _dismiss_oldest(self) -> None:
        """Dismiss the oldest notification"""
        if self.active_notifications:
            oldest = self.active_notifications.pop(0)
            try:
                if oldest.popup_layout:
                    oldest.popup_layout.kill()
            except Exception as e:
                logger.debug(f"Error dismissing popup: {e}")

    def _schedule_cleanup(self) -> None:
        """Schedule cleanup of expired notifications"""
        if not self.cleanup_scheduled and qtile:
            self.cleanup_scheduled = True
            qtile.call_later(1.0, self._cleanup_expired)

    def _cleanup_expired(self) -> None:
        """Clean up expired notifications"""
        self.cleanup_scheduled = False
        current_time = time.time()
        expired = []

        for notification in self.active_notifications:
            if (notification.timeout > 0 and
                current_time - notification.created_at > notification.timeout):
                expired.append(notification)

        # Remove expired notifications
        for notification in expired:
            try:
                if notification.popup_layout:
                    notification.popup_layout.kill()
                self.active_notifications.remove(notification)
            except Exception as e:
                logger.debug(f"Error cleaning up notification: {e}")

        # Reposition remaining notifications
        self._reposition_notifications()

        # Schedule next cleanup if needed
        if self.active_notifications:
            self._schedule_cleanup()

    def _reposition_notifications(self) -> None:
        """Reposition remaining notifications"""
        for i, notification in enumerate(self.active_notifications):
            try:
                new_x, new_y = self._calculate_position(i)
                if notification.popup_layout and hasattr(notification.popup_layout, 'place'):
                    notification.popup_layout.place(new_x, new_y)
            except Exception as e:
                logger.debug(f"Error repositioning notification: {e}")

    def dismiss_all(self) -> None:
        """Dismiss all active notifications"""
        for notification in self.active_notifications[:]:
            try:
                if notification.popup_layout:
                    notification.popup_layout.kill()
            except Exception:
                pass
        self.active_notifications.clear()


# Global popup manager instance
_popup_manager: Optional[SimplePopupManager] = None


def get_popup_manager() -> Optional[SimplePopupManager]:
    """Get the global popup manager instance"""
    return _popup_manager


def _notification_callback(notification):
    """Callback function to handle incoming D-Bus notifications"""
    logger.info(f"🔔 D-Bus notification callback triggered!")
    logger.info(f"Notification object: {notification}")
    logger.info(f"Notification type: {type(notification)}")

    if hasattr(notification, '__dict__'):
        logger.info(f"Notification attributes: {notification.__dict__}")

    if not _popup_manager:
        logger.warning("No popup manager available in callback")
        return

    try:
        # Extract notification data
        title = getattr(notification, 'summary', 'Notification')
        message = getattr(notification, 'body', '')
        logger.info(f"Extracted: title='{title}', message='{message}'")

        # Map urgency levels (D-Bus uses 0=low, 1=normal, 2=critical)
        urgency_map = {0: 'low', 1: 'normal', 2: 'critical'}
        urgency = urgency_map.get(getattr(notification, 'urgency', 1), 'normal')
        logger.info(f"Urgency: {urgency}")

        # Show popup
        _popup_manager.show_notification(title, message, urgency)
        logger.info(f"✅ Popup triggered by D-Bus notification: {title}")

    except Exception as e:
        logger.error(f"❌ Error in notification callback: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")


def setup_popup_notifications(color_manager: Any, qtile_config: Any = None, config: Optional[Dict[str, Any]] = None) -> None:
    """
    @brief Set up popup notifications using hooks
    @param color_manager: Color management instance
    @param qtile_config: Qtile configuration instance for positioning
    @param config: Optional configuration dictionary
    """
    global _popup_manager

    if not QTILE_EXTRAS_AVAILABLE:
        logger.warning("qtile-extras not available - popup notifications disabled")
        return

    # Create popup manager
    _popup_manager = SimplePopupManager(color_manager)

    # Apply custom configuration first
    if config:
        _popup_manager.config.update(config)
        _popup_manager._update_colors()

    # Set qtile config for smart positioning (after custom config)
    if qtile_config:
        _popup_manager.qtile_config = qtile_config
        _popup_manager._adjust_positioning()

    # Hook into D-Bus notifications to show popups (DISABLED - causing D-Bus issues)
    # TODO: Find a better way to intercept notify-send commands
    logger.info("D-Bus hook disabled - notifications will only show in bar for now")
    logger.info("Use Super+Ctrl+N to test popup system directly")

    logger.info("Simple popup notifications enabled")


def show_popup_notification(title: str, message: str, urgency: str = "normal") -> None:
    """
    @brief Show a popup notification
    @param title: Notification title
    @param message: Notification message
    @param urgency: Urgency level (low, normal, critical)
    """


    if _popup_manager:

        try:
            _popup_manager.show_notification(title, message, urgency)

        except Exception as e:
            logger.error(f"Error in _popup_manager.show_notification: {e}")
    else:
        logger.warning("Popup manager not initialized - cannot show popup")


def test_popup_notifications() -> None:
    """Test function for popup notifications"""
    if not _popup_manager:
        logger.error("Popup manager not initialized")
        return

    # Test different notification types
    test_notifications = [
        ("Normal Notification", "This is a normal priority notification", "normal"),
        ("Low Priority", "This is a low priority notification", "low"),
        ("Critical Alert", "This is a critical notification", "critical"),
    ]

    for title, message, urgency in test_notifications:
        show_popup_notification(title, message, urgency)
        time.sleep(0.5)

    logger.info("Popup notification test completed")


# Cleanup function for module unload
def cleanup_popup_notifications() -> None:
    """Clean up popup notifications on module unload"""
    global _popup_manager
    if _popup_manager:
        _popup_manager.dismiss_all()
        _popup_manager = None
