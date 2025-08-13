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

import html
import re
import subprocess
import time
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import os

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
    """
    @brief Represents a popup notification with all display data
    @param title: Notification title text
    @param message: Notification body text
    @param urgency: Urgency level (low, normal, critical)
    @param created_at: Unix timestamp when notification was created
    @param timeout: Timeout in seconds (0 = no timeout)
    @param popup_layout: QtileExtras popup layout instance
    @param icon: Optional icon file path
    @param actions: List of (action_key, action_label) tuples
    @param notification_id: D-Bus notification ID for action callbacks
    @param callback: Callback function for action button clicks
    """
    title: str
    message: str
    urgency: str
    created_at: float
    timeout: float
    popup_layout: Any | None = None
    icon: str | None = None
    actions: list[tuple[str, str]] = None
    notification_id: int = 0
    callback: Any | None = None

    def __post_init__(self):
        if self.actions is None:
            self.actions = []


class SimplePopupManager:
    """
    @brief Simple popup notification manager using qtile-extras

    Provides basic popup notifications using qtile-extras toolkit for
    cross-platform compatibility.

    @param color_manager: Color management instance for theming
    """

    def __init__(self, color_manager: Any) -> None:
        """
        @brief Initialize popup manager
        @param color_manager: Color management instance for theming
        """
        self.color_manager = color_manager
        self.active_notifications: list[PopupNotification] = []
        self.max_notifications = 5
        self.cleanup_scheduled = False
        self.qtile_config: Any | None = None  # Will be set during configuration

        # Default configuration with DPI scaling
        self.config: dict[str, Any] = {
            "width": scale_size(400),
            "height": scale_size(120),  # Will be increased for buttons
            "margin_x": scale_size(20),
            "margin_y": scale_size(20),  # Will be adjusted for bar height
            "spacing": scale_size(10),
            "corner": "top_right",
        }

        self._update_colors()

    def _update_colors(self) -> None:
        """
        @brief Update colors from color manager
        @throws Exception: When color manager fails to provide colors
        """
        try:
            colors = self.color_manager.get_colors()
            color_dict = colors.get("colors", {})
            special = colors.get("special", {})

            self.colors: dict[str, str] = {
                "bg_normal": special.get("background", "#1e1e1e").lstrip("#"),
                "fg_normal": special.get("foreground", "#ffffff").lstrip("#"),
                "bg_urgent": color_dict.get("color1", "#3e1e1e").lstrip("#"),
                "fg_urgent": color_dict.get("color9", "#ff6666").lstrip("#"),
                "bg_low": special.get("background", "#1e1e1e").lstrip("#"),
                "fg_low": color_dict.get("color8", "#888888").lstrip("#"),
                "border_normal": color_dict.get("color6", "#555555").lstrip("#"),
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

    def _show_notification_object(self, notification: PopupNotification) -> None:
        """
        @brief Show a popup notification using notification object
        @param notification: PopupNotification object with all details
        """
        # Determine timeout
        if notification.urgency == "critical":
            timeout = 0.0  # Never timeout
        elif notification.urgency == "low":
            timeout = 3.0
        else:
            timeout = 5.0

        # Dismiss oldest if we have too many
        while len(self.active_notifications) >= self.max_notifications:
            self._dismiss_oldest()

        # Calculate position
        stack_index = len(self.active_notifications)
        x, y = self._calculate_position(stack_index)

        # Update notification with position
        notification.timeout = timeout

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

            logger.info(f"Showed popup notification: {notification.title}")

            # Schedule cleanup if needed
            if timeout > 0 and not self.cleanup_scheduled:
                self._schedule_cleanup()

        except Exception as e:
            logger.error(f"Failed to show popup notification: {e}")

    def show_notification(
        self,
        title: str,
        message: str,
        urgency: str = "normal",
        icon: str | None = None,
        actions: list[tuple[str, str]] | None = None,
        notification_id: int = 0,
        callback: Any | None = None
    ) -> None:
        """
        @brief Show a popup notification
        @param title: Notification title
        @param message: Notification message
        @param urgency: Urgency level (low, normal, critical)
        @param icon: Optional icon path
        @param actions: List of (action_key, action_label) tuples for buttons
        @param notification_id: D-Bus notification ID for callbacks
        @param callback: Callback function for action button clicks
        """
        # Create notification object and delegate to internal method
        notification = PopupNotification(
            title=title,
            message=message,
            urgency=urgency,
            created_at=time.time(),
            timeout=0.0,  # Will be set by _show_notification_object
            icon=icon,
            actions=actions or [],
            notification_id=notification_id,
            callback=callback
        )

        self._show_notification_object(notification)

    def _sanitize_markup(self, text: str) -> tuple[str, list[str]]:
        """
        @brief Sanitize HTML content and extract URLs for safe Pango markup display
        @param text: Raw text that may contain HTML
        @return Tuple of (sanitized_text, list_of_urls)
        """
        if not text:
            return "", []

        # Unescape HTML entities first
        text = html.unescape(text)

        # Extract URLs from text and HTML links
        urls = []

        # Extract URLs from HTML links
        link_pattern = r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>'
        for match in re.finditer(link_pattern, text):
            url = match.group(1)
            link_text = match.group(2)
            urls.append(url)
            # Replace with clickable text
            text = text.replace(match.group(0), f'<u>{link_text}</u> 🔗')

        # Extract plain URLs (http/https/ftp)
        url_pattern = r'https?://[^\s<>"\']+|ftp://[^\s<>"\']+|www\.[^\s<>"\']+\.[a-zA-Z]{2,}'
        for match in re.finditer(url_pattern, text):
            url = match.group(0)
            if url not in urls:
                urls.append(url)
                # Make plain URLs underlined and clickable
                text = text.replace(url, f'<u>{url}</u> 🔗')

        # Convert other HTML formatting to Pango equivalents
        text = re.sub(r'<b>(.*?)</b>', r'<b>\1</b>', text)
        text = re.sub(r'<strong>(.*?)</strong>', r'<b>\1</b>', text)
        text = re.sub(r'<i>(.*?)</i>', r'<i>\1</i>', text)
        text = re.sub(r'<em>(.*?)</em>', r'<i>\1</i>', text)
        text = re.sub(r'<u>(.*?)</u>', r'<u>\1</u>', text)

        # Remove any remaining HTML tags for safety
        text = re.sub(r'<[^>]+>', '', text)

        # Escape any remaining angle brackets that aren't Pango markup
        text = re.sub(r'<(?![biu/])', '&lt;', text)
        text = re.sub(r'(?<![biu])>', '&gt;', text)

        return text, urls

    def _open_url(self, url: str) -> None:
        """
        @brief Open URL in default browser
        @param url: URL to open
        """
        try:
            # Add protocol if missing
            if not url.startswith(('http://', 'https://', 'ftp://')):
                if url.startswith('www.'):
                    url = f'https://{url}'
                else:
                    url = f'https://{url}'

            # Try different methods to open URL
            try:
                webbrowser.open(url)
                logger.info(f"Opened URL: {url}")
            except Exception:
                # Fallback to xdg-open
                subprocess.run(['xdg-open', url], check=False)
                logger.info(f"Opened URL with xdg-open: {url}")

        except Exception as e:
            logger.error(f"Failed to open URL {url}: {e}")

    def _create_popup(self, notification: PopupNotification, x: int, y: int) -> PopupRelativeLayout:
        """
        @brief Create popup layout for notification
        @param notification: Notification data to display
        @param x: X coordinate offset
        @param y: Y coordinate offset
        @return PopupRelativeLayout instance for display
        """
        # Calculate if we need extra height for buttons/URLs
        sanitized_message, urls = self._sanitize_markup(notification.message)
        total_buttons = len(notification.actions) + len(urls)
        has_buttons = total_buttons > 0

        # Adjust popup height for buttons
        popup_height = self.config["height"]
        if has_buttons:
            popup_height = int(popup_height * 1.4)  # 40% taller for buttons
        # Choose colors based on urgency using match statement
        match notification.urgency:
            case "critical":
                bg_color = self.colors["bg_urgent"]
                fg_color = self.colors["fg_urgent"]
                border_color = self.colors["border_urgent"]
            case "low":
                bg_color = self.colors["bg_low"]
                fg_color = self.colors["fg_low"]
                border_color = self.colors["border_normal"]
            case _:
                bg_color = self.colors["bg_normal"]
                fg_color = self.colors["fg_normal"]
                border_color = self.colors["border_normal"]



        # Create controls
        controls = []

        # Get theme-aware font with debugging
        font_family = "sans-serif"
        if self.qtile_config and hasattr(self.qtile_config, 'preferred_font'):
            preferred_font = self.qtile_config.preferred_font
            font_family = get_available_font(preferred_font)
            logger.debug(f"Font selection: preferred='{preferred_font}' -> selected='{font_family}'")
        else:
            logger.debug(f"No qtile_config or preferred_font, using fallback: '{font_family}'")

        # Check for notification icon using pathlib
        has_icon = False
        icon_path = None
        if notification.icon and Path(notification.icon).exists():
            has_icon = True
            icon_path = notification.icon
            logger.debug(f"Found notification icon: {icon_path}")

        # Adjust layout for icon
        title_x = 0.25 if has_icon else 0.05
        title_width = 0.7 if has_icon else 0.9
        message_x = 0.25 if has_icon else 0.05
        message_width = 0.7 if has_icon else 0.9

        # Add icon if present
        if has_icon and icon_path:
            try:
                from qtile_extras.popup.toolkit import PopupImage
                controls.append(
                    PopupImage(
                        filename=icon_path,
                        pos_x=0.05,
                        pos_y=0.1,
                        width=0.15,
                        height=0.8,
                        highlight=fg_color,
                    )
                )
                logger.debug(f"Added icon to popup: {icon_path}")
            except Exception as e:
                logger.warning(f"Failed to add icon: {e}")
                # Reset layout if icon failed
                title_x = message_x = 0.05
                title_width = message_width = 0.9

        # Title (if present)
        if notification.title:
            controls.append(
                PopupText(
                    text=f"<b>{notification.title}</b>",
                    pos_x=title_x,
                    pos_y=0.1,
                    width=title_width,
                    height=0.35,
                    fontsize=scale_font(16),
                    foreground=fg_color,
                    font=font_family,
                    markup=True,
                    h_align="left",
                    v_align="top",
                    wrap=True,
                )
            )

        # Message
        # Message text
        # Message text with URL extraction
        if notification.message:
            # Adjust message area height if we have buttons
            if has_buttons:
                msg_y = 0.5 if notification.title else 0.25
                msg_height = 0.25 if notification.title else 0.5
            else:
                msg_y = 0.5 if notification.title else 0.2
                msg_height = 0.4 if notification.title else 0.6

            controls.append(
                PopupText(
                    text=sanitized_message,
                    pos_x=message_x,
                    pos_y=msg_y,
                    width=message_width,
                    height=msg_height,
                    fontsize=scale_font(14),
                    foreground=fg_color,
                    font=font_family,
                    markup=True,
                    h_align="left",
                    v_align="top",
                    wrap=True,
                )
            )

        # Add URL buttons for extracted links
        current_button = 0

        if urls:
            try:
                for url in urls[:2]:  # Limit to first 2 URLs to avoid crowding
                    button_width = 0.4 if total_buttons <= 2 else 0.3
                    button_x = 0.05 + (current_button * (button_width + 0.05))
                    button_y = 0.75

                    def make_url_handler(target_url=url, mgr=self):
                        def handler(popup_text=None, *args, **kwargs):
                            logger.warning(f"🔗 URL button clicked: {target_url}")
                            try:
                                mgr._open_url(target_url)
                                logger.info(f"Successfully opened URL: {target_url}")
                            except Exception as e:
                                logger.error(f"Failed to open URL {target_url}: {e}")
                            # Keep popup open for URL clicks
                        return handler

                    url_button = PopupText(
                        text=f"🔗 Open Link",
                        pos_x=button_x,
                        pos_y=button_y,
                        width=button_width,
                        height=0.15,
                        fontsize=scale_font(11),
                        foreground="#ffffff",
                        background="#0066cc",  # Blue button color
                        font=font_family,
                        h_align="center",
                        v_align="middle",
                        markup=True,
                    )
                    url_button.mouse_callbacks = {"Button1": make_url_handler()}
                    controls.append(url_button)
                    current_button += 1

                logger.debug(f"Added {len(urls)} URL buttons")

            except Exception as e:
                logger.warning(f"Failed to add URL buttons: {e}")

        # Add action buttons if present
        if notification.actions:
            try:
                for i, (action_key, action_label) in enumerate(notification.actions):
                    button_width = 0.4 if total_buttons <= 2 else 0.3
                    button_x = 0.05 + (current_button * (button_width + 0.05))
                    button_y = 0.75

                    def make_action_handler(key=action_key, nid=notification.notification_id, mgr=self, notif=notification):
                        def handler(popup_text=None, *args, **kwargs):
                            logger.warning(f"🔘 Action button clicked: {key} (ID: {nid})")
                            try:
                                if notif.callback:
                                    notif.callback(nid, key)
                                    logger.info(f"Action callback completed: {key}")
                                # Auto-close popup after action by removing from active notifications
                                mgr._dismiss_notification(notif)
                                logger.info("Popup dismissed after action")
                            except Exception as e:
                                logger.error(f"Action handler error: {e}")
                        return handler

                    action_button = PopupText(
                        text=f"{action_label}",
                        pos_x=button_x,
                        pos_y=button_y,
                        width=button_width,
                        height=0.15,
                        fontsize=scale_font(12),
                        foreground="#ffffff",
                        background="#28a745",  # Green button color
                        font=font_family,
                        h_align="center",
                        v_align="middle",
                        markup=True,
                    )
                    action_button.mouse_callbacks = {"Button1": make_action_handler()}
                    controls.append(action_button)
                    current_button += 1

                logger.debug(f"Added {len(notification.actions)} action buttons")

            except Exception as e:
                logger.warning(f"Failed to add action buttons: {e}")

        # Create popup layout with adjusted height
        popup = PopupRelativeLayout(
            qtile,
            width=self.config["width"],
            height=popup_height,
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

    def _dismiss_notification(self, notification: PopupNotification) -> None:
        """Dismiss a specific notification"""
        try:
            if notification.popup_layout:
                notification.popup_layout.kill()
            if notification in self.active_notifications:
                self.active_notifications.remove(notification)
        except Exception as e:
            logger.debug(f"Error dismissing notification: {e}")

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
_popup_manager: SimplePopupManager | None = None


def get_popup_manager() -> SimplePopupManager | None:
    """
    @brief Get the global popup manager instance
    @return SimplePopupManager instance or None if not initialized
    """
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


def setup_popup_notifications(color_manager: Any, qtile_config: Any | None = None, config: dict[str, Any] | None = None) -> None:
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


def show_popup_notification(
    title: str,
    message: str,
    urgency: str = "normal",
    icon: str | None = None,
    actions: list[tuple[str, str]] | None = None,
    notification_id: int = 0,
    callback: Any | None = None
) -> None:
    """
    @brief Show a popup notification
    @param title: Notification title
    @param message: Notification message
    @param urgency: Urgency level (low, normal, critical)
    @param icon: Optional icon path
    @param actions: List of (action_key, action_label) tuples for buttons
    @param notification_id: D-Bus notification ID for callbacks
    @param callback: Callback function for action button clicks
    """

    if _popup_manager:
        try:
            _popup_manager.show_notification(
                title, message, urgency, icon, actions, notification_id, callback
            )
        except Exception as e:
            logger.error(f"Error in popup manager: {e}")
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
