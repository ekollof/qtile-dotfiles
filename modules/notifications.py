#!/usr/bin/env python3
"""
Consolidated Notifications Module

@brief Unified notification system for qtile
@author Andrath

This module consolidates popup notifications and notification widgets
into a single, well-organized system with improved maintainability.

Features:
- Cross-platform popup notifications (X11 and Wayland)
- D-Bus notification server compatibility
- Configurable positioning and styling
- Urgency-based styling
- Auto-dismiss with timeouts
- Multiple notification stacking
- Action button support
- Icon support

Usage:
    from modules.notifications import setup_notifications, create_notify_widget
    setup_notifications(qtile, color_manager)
    notify_widget = create_notify_widget()
"""

import html
import re
import subprocess
import time
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libqtile import qtile, widget
from libqtile.log_utils import logger

from modules.dpi_utils import scale_font, scale_size
from modules.font_utils import get_available_font


def _check_notify_availability() -> bool:
    """Check if libqtile.notify is available"""
    try:
        import importlib.util

        return importlib.util.find_spec("libqtile.notify") is not None
    except ImportError:
        logger.warning("libqtile.notify not available")
        return False


def _check_dbus_availability() -> bool:
    """Check if D-Bus is available"""
    try:
        import importlib.util

        return importlib.util.find_spec("dbus") is not None
    except ImportError:
        logger.warning("D-Bus not available - notification actions will not work")
        return False


NOTIFY_AVAILABLE = _check_notify_availability()
DBUS_AVAILABLE = _check_dbus_availability()


# Check qtile-extras availability and import components
def _get_qtile_extras_components():
    """Get qtile-extras components if available"""
    try:
        from qtile_extras.popup.toolkit import PopupRelativeLayout, PopupText

        return True, PopupRelativeLayout, PopupText
    except ImportError:
        logger.warning("qtile-extras not available - popup notifications disabled")
        return False, None, None


_QTILE_EXTRAS_AVAILABLE, PopupRelativeLayout, PopupText = _get_qtile_extras_components()


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
    actions: list[tuple[str, str]] | None = None
    notification_id: int = 0
    callback: Any | None = None

    def __post_init__(self):
        if self.actions is None:
            self.actions = []


class PopupManager:
    """
    @brief Popup notification manager using qtile-extras

    Provides popup notifications using qtile-extras toolkit for
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

        self.update_colors()

    def update_colors(self) -> None:
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
                "bg_normal": "1e1e1e",
                "fg_normal": "ffffff",
                "bg_urgent": "3e1e1e",
                "fg_urgent": "ff6666",
                "bg_low": "1e1e1e",
                "fg_low": "888888",
                "border_normal": "555555",
                "border_urgent": "ff0000",
            }

    def adjust_positioning(self) -> None:
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

            logger.debug(
                f"Adjusted positioning: margin_x={self.config['margin_x']}, margin_y={self.config['margin_y']}"
            )

        except Exception as e:
            logger.warning(f"Could not adjust positioning: {e}")
            # Keep defaults

    def _show_notification_object(self, notification: PopupNotification) -> None:
        """
        @brief Show a popup notification using notification object
        @param notification: PopupNotification object with all details
        """
        # Determine timeout - notifications with actions should not auto-timeout
        if notification.actions:
            timeout = 0.0  # Never timeout for interactive notifications
        else:
            match notification.urgency:
                case "critical":
                    timeout = 0.0  # Never timeout for critical notifications
                case "low":
                    timeout = 3.0
                case _:  # normal or unknown urgency
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
                relative_to_bar=True,  # Auto-adjust for bars and gaps
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
        callback: Any | None = None,
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
            callback=callback,
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
            text = text.replace(match.group(0), f"<u>{link_text}</u> 🔗")

        # Extract plain URLs (http/https/ftp)
        url_pattern = (
            r'https?://[^\s<>"\']+|ftp://[^\s<>"\']+|www\.[^\s<>"\']+\.[a-zA-Z]{2,}'
        )
        for match in re.finditer(url_pattern, text):
            url = match.group(0)
            if url not in urls:
                urls.append(url)
                # Make plain URLs underlined and clickable
                text = text.replace(url, f"<u>{url}</u> 🔗")

        # Convert other HTML formatting to Pango equivalents
        text = re.sub(r"<b>(.*?)</b>", r"<b>\1</b>", text)
        text = re.sub(r"<strong>(.*?)</strong>", r"<b>\1</b>", text)
        text = re.sub(r"<i>(.*?)</i>", r"<i>\1</i>", text)
        text = re.sub(r"<em>(.*?)</em>", r"<i>\1</i>", text)
        text = re.sub(r"<u>(.*?)</u>", r"<u>\1</u>", text)

        # Remove any remaining HTML tags for safety
        text = re.sub(r"<[^>]+>", "", text)

        # Escape any remaining angle brackets that aren't Pango markup
        text = re.sub(r"<(?![biu/])", "&lt;", text)
        text = re.sub(r"(?<![biu])>", "&gt;", text)

        return text, urls

    def _open_url(self, url: str) -> None:
        """
        @brief Open URL in default browser
        @param url: URL to open
        """
        try:
            # Add protocol if missing
            if not url.startswith(("http://", "https://", "ftp://")):
                if url.startswith("www."):
                    url = f"https://{url}"
                else:
                    url = f"https://{url}"

            # Try different methods to open URL
            try:
                webbrowser.open(url)
                logger.info(f"Opened URL: {url}")
            except Exception:
                # Fallback to xdg-open
                subprocess.run(["xdg-open", url], check=False)
                logger.info(f"Opened URL with xdg-open: {url}")

        except Exception as e:
            logger.error(f"Failed to open URL {url}: {e}")

    def _calculate_text_height(
        self,
        text: str,
        width: int,
        message_font_size: int,
        has_title: bool,
        title_font_size: int | None = None,
        has_buttons: bool = False,
    ) -> int:
        """
        @brief Calculate required height for text content with proper word wrapping
        @param text: Text content to measure
        @param width: Available width for text
        @param message_font_size: DPI-scaled font size for message text
        @param has_title: Whether notification has a title
        @param title_font_size: DPI-scaled font size for title text
        @param has_buttons: Whether notification has action buttons
        @return Required height in pixels
        """
        if not text:
            base_height = self.config["height"]
            logger.debug(f"Empty text, using base height: {base_height}px")
            return max(base_height, 80)

        # Remove HTML markup for length calculation
        import re

        clean_text = re.sub(r"<[^>]+>", "", text)

        # More conservative character width estimation
        # Account for proportional fonts being narrower on average
        avg_char_width = message_font_size * 0.35  # More generous estimation for better wrapping
        text_area_width = width * 0.9  # Give more space for text (90% instead of 85%)
        available_chars = max(
            25, int(text_area_width / avg_char_width)
        )  # Minimum 25 chars per line, increased from 20

        logger.debug(
            f"Text calc: font={message_font_size}px, width={width}px, chars_per_line={available_chars}"
        )

        # Split into paragraphs first
        paragraphs = clean_text.split("\n")
        total_lines = 0

        for paragraph in paragraphs:
            if not paragraph.strip():
                total_lines += 1  # Empty line
                continue

            # Split paragraph into words for proper word wrapping
            words = paragraph.split()
            if not words:
                total_lines += 1
                continue

            current_line_length = 0
            lines_in_paragraph = 1

            for word in words:
                word_length = len(word)
                # Check if adding this word would exceed line length (including space)
                if (
                    current_line_length > 0
                    and current_line_length + 1 + word_length > available_chars
                ):
                    lines_in_paragraph += 1
                    current_line_length = word_length
                else:
                    current_line_length += word_length + (
                        1 if current_line_length > 0 else 0
                    )

            total_lines += lines_in_paragraph

        logger.debug(
            f"Text lines calculated: {total_lines} lines for text: '{clean_text[:50]}...'"
        )

        # Log detailed text calculation info
        logger.debug(
            f"Text calculation details: width={width}px, text_area={text_area_width:.1f}px, "
            f"chars_per_line={available_chars}, total_chars={len(clean_text)}"
        )

        # Calculate height components using DPI-scaled font sizes
        title_font = title_font_size or scale_font(16)
        title_height = (
            int(title_font * 1.8) + 10 if has_title else 0
        )  # Extra padding for title
        line_height = int(message_font_size * 1.6)  # More generous line spacing (1.6x instead of 1.5)
        text_height = total_lines * line_height
        top_padding = 15
        # Match the bottom margin used in message positioning - more for notifications without buttons
        bottom_padding = 15 if has_buttons else 25

        # Add button area to total height if buttons are present
        button_area = (
            max(50, int(scale_font(12) * 3.5)) + 25 if has_buttons else 0
        )  # Increased button height and margins

        total_height = (
            top_padding + title_height + text_height + bottom_padding + button_area
        )

        logger.debug(
            f"Height components: title={title_height}px, text={text_height}px, padding={top_padding + bottom_padding}px"
        )

        # Ensure reasonable bounds - increased max height significantly
        min_height = max(self.config["height"], 120)  # Higher minimum (120px instead of 100)
        max_height = 1200  # Much higher maximum (1200px instead of 600) for very long messages

        final_height = max(min_height, min(max_height, int(total_height)))
        logger.debug(f"Final calculated height: {final_height}px (max allowed: {max_height}px)")

        return final_height

    def _create_popup(self, notification: PopupNotification, x: int, y: int) -> Any:
        """
        @brief Create popup layout for notification
        @param notification: Notification data to display
        @param x: X coordinate offset
        @param y: Y coordinate offset
        @return PopupRelativeLayout instance for display
        """
        # Calculate if we need extra height for buttons/URLs
        sanitized_message, urls = self._sanitize_markup(notification.message)
        actions_list = notification.actions or []
        total_buttons = len(actions_list) + len(urls)
        has_buttons = total_buttons > 0

        # Calculate required height based on text content with DPI-scaled fonts
        title_font_size = (
            self.qtile_config.preferred_fontsize + 2 if self.qtile_config else 16
        )
        message_font_size = (
            self.qtile_config.preferred_fontsize if self.qtile_config else 14
        )

        popup_height = self._calculate_text_height(
            sanitized_message,
            self.config["width"],
            scale_font(message_font_size),  # Message font size
            bool(notification.title),
            scale_font(title_font_size),  # Title font size
            has_buttons,  # Whether buttons are present
        )
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
        if self.qtile_config and hasattr(self.qtile_config, "preferred_font"):
            preferred_font = self.qtile_config.preferred_font
            font_family = get_available_font(preferred_font)
            logger.debug(
                f"Font selection: preferred='{preferred_font}' -> selected='{font_family}'"
            )
        else:
            logger.debug(
                f"No qtile_config or preferred_font, using fallback: '{font_family}'"
            )

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
        message_width = 0.7 if has_icon else 0.9  # Increased from 0.9 to give more text space

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
        if notification.title and _QTILE_EXTRAS_AVAILABLE:
            assert PopupText is not None
            title_font_size = scale_font(
                self.qtile_config.preferred_fontsize + 2 if self.qtile_config else 16
            )
            title_height_px = int(title_font_size * 1.5)
            controls.append(
                PopupText(
                    text=f"<b>{notification.title}</b>",
                    pos_x=title_x,
                    pos_y=10 / popup_height,  # 10px from top
                    width=title_width,
                    height=title_height_px / popup_height,
                    fontsize=title_font_size,
                    foreground=fg_color,
                    font=font_family,
                    markup=True,
                    h_align="left",
                    v_align="top",
                    wrap=True,  # Ensure title wraps if needed
                )
            )

        # Message
        # Message text
        # Message text with URL extraction
        if notification.message:
            # Calculate message area positioning based on actual pixel heights
            title_font_size = scale_font(
                self.qtile_config.preferred_fontsize + 2 if self.qtile_config else 16
            )
            title_height_px = (
                int(title_font_size * 1.8) + 10 if notification.title else 0
            )
            button_area_px = (
                max(
                    50,
                    int(
                        scale_font(
                            self.qtile_config.preferred_fontsize
                            if self.qtile_config
                            else 12
                        )
                        * 3.5
                    ),
                )
                + 25
                if has_buttons
                else 0
            )
            top_margin = 15
            title_margin = 8 if notification.title else 0
            # Increase bottom margin for notifications without buttons to prevent text creeping to border
            bottom_margin = 20 if has_buttons else 30  # Increased margins

            # Message starts after title (if present) plus margins
            msg_y_px = top_margin + title_height_px + title_margin
            # Available height for message: total popup height minus all other elements
            available_height_px = popup_height - msg_y_px - button_area_px - bottom_margin
            msg_height_px = max(available_height_px, 40)  # Minimum 40px for message area

            msg_y = msg_y_px / popup_height
            msg_height = msg_height_px / popup_height

            logger.debug(
                f"Message positioning: y={msg_y_px}px ({msg_y:.2%}), height={msg_height_px}px ({msg_height:.2%})"
            )
            logger.debug(
                f"Space allocation: popup={popup_height}px, title={title_height_px}px, buttons={button_area_px}px, margins={top_margin + bottom_margin}px"
            )
            logger.debug(
                f"Available message space: {available_height_px}px (minimum 40px enforced)"
            )
            logger.debug(
                f"Space allocation: popup={popup_height}px, title={title_height_px}px, buttons={button_area_px}px, margins={top_margin + bottom_margin}px"
            )

            assert PopupText is not None
            controls.append(
                PopupText(
                    text=sanitized_message,
                    pos_x=message_x,
                    pos_y=msg_y,
                    width=message_width,
                    height=msg_height,
                    fontsize=scale_font(message_font_size),
                    foreground=fg_color,
                    font=font_family,
                    markup=True,
                    h_align="left",
                    v_align="top",
                    wrap=True,  # Ensure text wraps instead of truncating
                )
            )

        # Add URL buttons for extracted links
        current_button = 0

        if urls:
            try:
                for url in urls[:2]:  # Limit to first 2 URLs to avoid crowding
                    button_width = 0.4 if total_buttons <= 2 else 0.3
                    button_x = 0.05 + (current_button * (button_width + 0.05))
                    # Position buttons at bottom with fixed margin
                    button_margin_bottom = 20  # Increased from 15
                    button_height_px = max(40, int(scale_font(11) * 2.8))  # Increased from 2.5
                    button_y = 1.0 - (
                        (button_height_px + button_margin_bottom) / popup_height
                    )

                    def make_url_handler(target_url: str = url, mgr: Any = self):
                        def handler(
                            popup_text: Any = None, *args: Any, **kwargs: Any
                        ) -> None:
                            logger.warning(f"🔗 URL button clicked: {target_url}")
                            try:
                                mgr._open_url(target_url)
                                logger.info(f"Successfully opened URL: {target_url}")
                            except Exception as e:
                                logger.error(f"Failed to open URL {target_url}: {e}")
                            # Keep popup open for URL clicks

                        return handler

                    if _QTILE_EXTRAS_AVAILABLE:
                        assert PopupText is not None
                        url_button = PopupText(
                            text="🔗 Open Link",
                            pos_x=button_x,
                            pos_y=button_y,
                            width=button_width,
                            height=max(
                                40,
                                int(
                                    scale_font(
                                        self.qtile_config.preferred_fontsize - 1
                                        if self.qtile_config
                                        else 11
                                    )
                                    * 2.8
                                ),
                            )
                            / popup_height,
                            fontsize=scale_font(
                                self.qtile_config.preferred_fontsize - 1
                                if self.qtile_config
                                else 11
                            ),
                            foreground="#ffffff",
                            background="#0066cc",  # Blue button color
                            font=font_family,
                            h_align="center",
                            v_align="middle",
                            markup=True,
                            wrap=True,  # Ensure button text wraps
                        )
                        url_button.mouse_callbacks = {"Button1": make_url_handler()}
                        controls.append(url_button)
                        current_button += 1

                logger.debug(f"Added {len(urls)} URL buttons")

            except Exception as e:
                logger.warning(f"Failed to add URL buttons: {e}")

        # Add action buttons if present
        if actions_list:
            try:
                for _i, (action_key, action_label) in enumerate(actions_list):
                    button_width = 0.4 if total_buttons <= 2 else 0.3
                    button_x = 0.05 + (current_button * (button_width + 0.05))
                    # Position buttons at bottom with fixed margin
                    button_margin_bottom = 20  # Increased from 15
                    button_height_px = max(40, int(scale_font(12) * 2.8))  # Increased from 2.5
                    button_y = 1.0 - (
                        (button_height_px + button_margin_bottom) / popup_height
                    )

                    def make_action_handler(
                        key: str = action_key,
                        nid: int = notification.notification_id,
                        mgr=self,
                        notif: Any = notification,
                    ):
                        def handler(
                            popup_text: Any = None, *args: Any, **kwargs: Any
                        ) -> None:
                            logger.warning(
                                f"🔘 Action button clicked: {key} (ID: {nid})"
                            )
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

                    if _QTILE_EXTRAS_AVAILABLE:
                        assert PopupText is not None
                        action_button = PopupText(
                            text=f"{action_label}",
                            pos_x=button_x,
                            pos_y=button_y,
                            width=button_width,
                            height=max(
                                40,
                                int(
                                    scale_font(
                                        self.qtile_config.preferred_fontsize
                                        if self.qtile_config
                                        else 12
                                    )
                                    * 2.8
                                ),
                            )
                            / popup_height,
                            fontsize=scale_font(
                                self.qtile_config.preferred_fontsize
                                if self.qtile_config
                                else 12
                            ),
                            foreground="#ffffff",
                            background="#28a745",  # Green button color
                            font=font_family,
                            h_align="center",
                            v_align="middle",
                            markup=True,
                            wrap=True,  # Ensure button text wraps
                        )
                        action_button.mouse_callbacks = {
                            "Button1": make_action_handler()
                        }
                        controls.append(action_button)
                        current_button += 1

                logger.debug(f"Added {len(actions_list)} action buttons")

            except Exception as e:
                logger.warning(f"Failed to add action buttons: {e}")

        # Add dismiss button if there are actions or URLs (so notification can be closed)
        if has_buttons:
            try:
                dismiss_width = 0.15  # Smaller dismiss button
                dismiss_x = 0.8  # Position on the right
                dismiss_y = 0.05  # Top right corner

                def make_dismiss_handler(mgr=self, notif: Any = notification):
                    def handler(
                        popup_text: Any = None, *args: Any, **kwargs: Any
                    ) -> None:
                        logger.info("❌ Dismiss button clicked")
                        try:
                            mgr._dismiss_notification(notif)
                            logger.info("Popup dismissed by user")
                        except Exception as e:
                            logger.error(f"Dismiss handler error: {e}")

                    return handler

                if _QTILE_EXTRAS_AVAILABLE:
                    assert PopupText is not None
                    dismiss_button = PopupText(
                        text="✕",
                        pos_x=dismiss_x,
                        pos_y=dismiss_y,
                        width=dismiss_width,
                        height=0.15,  # Small square button
                        fontsize=scale_font(
                            self.qtile_config.preferred_fontsize + 2
                            if self.qtile_config
                            else 14
                        ),
                        foreground="#ffffff",
                        background="#dc3545",  # Red dismiss button
                        font=font_family,
                        h_align="center",
                        v_align="middle",
                        markup=True,
                        wrap=True,  # Ensure dismiss button text wraps
                    )
                    dismiss_button.mouse_callbacks = {"Button1": make_dismiss_handler()}
                    controls.append(dismiss_button)

                logger.debug("Added dismiss button for interactive notification")

            except Exception as e:
                logger.warning(f"Failed to add dismiss button: {e}")

        # Create popup layout with adjusted height
        if not _QTILE_EXTRAS_AVAILABLE:
            return None
        assert PopupRelativeLayout is not None
        # Allow click dismissal for all notifications, but add dismiss button for ones with actions
        popup = PopupRelativeLayout(
            qtile,
            width=self.config["width"],
            height=popup_height,
            controls=controls,
            background=bg_color,
            border=border_color,
            border_width=2,
            initial_focus=None,
            close_on_click=True,  # Allow click dismissal for all notifications
            opacity=0.95,
        )

        return popup

    def _calculate_position(self, stack_index: int) -> tuple[int, int]:
        """Calculate position offset for notification using qtile-extras positioning"""
        try:
            margin_x = self.config["margin_x"]
            margin_y = self.config["margin_y"]
            spacing = self.config["spacing"]
            height = self.config["height"]

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
                max_notifications = max(
                    1, int((max_y - margin_y) / (height + spacing)) + 1
                )
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
            if (
                notification.timeout > 0
                and current_time - notification.created_at > notification.timeout
            ):
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
                if notification.popup_layout and hasattr(
                    notification.popup_layout, "place"
                ):
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
_popup_manager: PopupManager | None = None


def get_popup_manager() -> PopupManager | None:
    """
    @brief Get the global popup manager instance
    @return PopupManager instance or None if not initialized
    """
    return _popup_manager


def _notification_callback(notification: Any) -> None:
    """Callback function to handle incoming D-Bus notifications"""
    logger.info("🔔 D-Bus notification callback triggered!")
    logger.info(f"Notification object: {notification}")
    logger.info(f"Notification type: {type(notification)}")

    if hasattr(notification, "__dict__"):
        logger.info(f"Notification attributes: {notification.__dict__}")

    if not _popup_manager:
        logger.warning("No popup manager available in callback")
        return

    try:
        # Extract notification data
        title = getattr(notification, "summary", "Notification")
        message = getattr(notification, "body", "")
        logger.info(f"Extracted: title='{title}', message='{message}'")

        # Map urgency levels (D-Bus uses 0=low, 1=normal, 2=critical)
        urgency_map = {0: "low", 1: "normal", 2: "critical"}
        urgency = urgency_map.get(getattr(notification, "urgency", 1), "normal")
        logger.info(f"Urgency: {urgency}")

        # Show popup
        _popup_manager.show_notification(title, message, urgency)
        logger.info(f"✅ Popup triggered by D-Bus notification: {title}")

    except Exception as e:
        logger.error(f"❌ Error in notification callback: {e}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")


def setup_notifications(
    color_manager: Any,
    qtile_config: Any | None = None,
    config: dict[str, Any] | None = None,
) -> None:
    """
    @brief Set up popup notifications using hooks
    @param color_manager: Color management instance
    @param qtile_config: Qtile configuration instance for positioning
    @param config: Optional configuration dictionary
    """
    global _popup_manager

    if not _QTILE_EXTRAS_AVAILABLE:
        logger.warning("qtile-extras not available - popup notifications disabled")
        return

    # Create popup manager
    _popup_manager = PopupManager(color_manager)

    # Apply custom configuration first
    if config:
        _popup_manager.config.update(config)
        _popup_manager.update_colors()

    # Set qtile config for smart positioning (after custom config)
    if qtile_config:
        _popup_manager.qtile_config = qtile_config
        _popup_manager.adjust_positioning()

    # Hook into D-Bus notifications to show popups (DISABLED - causing D-Bus issues)
    # TODO: Find a better way to intercept notify-send commands
    logger.info("D-Bus hook disabled - notifications will only show in bar for now")
    logger.info("Use Super+Ctrl+N to test popup system directly")

    logger.info("Popup notifications enabled")


def show_popup_notification(
    title: str,
    message: str,
    urgency: str = "normal",
    icon: str | None = None,
    actions: list[tuple[str, str]] | None = None,
    notification_id: int = 0,
    callback: Any | None = None,
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
def cleanup_notifications() -> None:
    """Clean up popup notifications on module unload"""
    global _popup_manager
    if _popup_manager:
        _popup_manager.dismiss_all()
        _popup_manager = None


class NotifyWidget(widget.Notify):  # type: ignore[misc]
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
        self.add_defaults(NotifyWidget.defaults)

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
                title = getattr(notification, "summary", "Notification")
                message = getattr(notification, "body", "")

                # Map urgency levels (D-Bus uses 0=low, 1=normal, 2=critical)
                # Extract urgency from hints as per D-Bus specification
                try:
                    hints = getattr(notification, "hints", {})
                    urgency_hint = hints.get("urgency") if hints else None
                    raw_urgency = (
                        getattr(urgency_hint, "value", 1) if urgency_hint else 1
                    )
                except Exception:
                    raw_urgency = 1
                urgency_map = {0: "low", 1: "normal", 2: "critical"}
                urgency = urgency_map.get(raw_urgency, "normal")

                # Extract action buttons if enabled
                actions = []
                if self.enable_actions:
                    try:
                        raw_actions = getattr(notification, "actions", [])
                        # Actions come in pairs: [action_key, action_label, ...]
                        for i in range(0, len(raw_actions), 2):
                            if i + 1 < len(raw_actions):
                                action_key = raw_actions[i]
                                action_label = raw_actions[i + 1]
                                actions.append((action_key, action_label))

                        if actions:
                            logger.debug(
                                f"Found {len(actions)} action buttons: {actions}"
                            )
                    except Exception as e:
                        logger.warning(f"Error extracting actions: {e}")

                # Extract icon information from D-Bus notification
                icon_path = None
                try:
                    # Check app_icon attribute (this is where notify-send puts icons)
                    icon_path = getattr(notification, "app_icon", None)

                    # Fallback to hints if app_icon is empty
                    if not icon_path:
                        hints = getattr(notification, "hints", {})
                        if hints:
                            icon_path = (
                                hints.get("image-path")
                                or hints.get("image_path")
                                or hints.get("icon_data")
                            )

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
                    notification_id=getattr(notification, "id", 0),
                    callback=self._handle_action_callback if actions else None,
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

            if (
                hasattr(notify, "notifier")
                and notify.notifier
                and hasattr(notify.notifier, "_service")
            ):
                # Send ActionInvoked signal first
                notify.notifier._service.ActionInvoked(notification_id, action_key)
                logger.info(
                    f"Action invoked via qtile service: ID={notification_id}, action={action_key}"
                )

                # Send NotificationClosed signal to complete the D-Bus interaction
                notify.notifier._service.NotificationClosed(
                    notification_id, 2
                )  # 2 = dismissed by user action
                logger.info(
                    f"Notification closed via qtile service: ID={notification_id}"
                )
            else:
                logger.warning("Qtile notification service not available")

        except Exception as e:
            logger.error(f"Failed to invoke action via qtile service: {e}")


def create_notify_widget(**kwargs: Any) -> NotifyWidget:
    """
    @brief Factory function to create a popup notify widget
    @param kwargs: Keyword arguments to pass to the widget
    @return NotifyWidget instance
    @throws Exception: When widget creation fails
    """
    try:
        widget_instance = NotifyWidget(**kwargs)
        logger.info("Popup notify widget created successfully")
        return widget_instance

    except Exception as e:
        logger.error(f"Failed to create popup notify widget: {e}")
        # Return standard notify widget as fallback
        return widget.Notify(**kwargs)


# Maintain backward compatibility
__all__ = [
    "NotifyWidget",
    "PopupManager",
    "PopupNotification",
    "cleanup_notifications",
    "create_notify_widget",
    "get_popup_manager",
    "setup_notifications",
    "show_popup_notification",
    "test_popup_notifications",
]
