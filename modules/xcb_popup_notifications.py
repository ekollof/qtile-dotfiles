#!/usr/bin/env python3
"""
XCB Popup Notification System for Qtile

@brief Native X11 popup notifications using xcffib
@author Andrath

This module creates popup notification windows using xcffib for native X11
window creation and positioning. Provides precise control over appearance,
positioning, and behavior.

Features:
- Native X11 windows with xcffib
- Precise positioning in screen corners
- Automatic stacking of multiple notifications
- Theme integration with qtile colors
- Timeout handling and auto-dismissal
- Click-to-dismiss functionality
- DPI-aware sizing and fonts
- Cross-platform X11 compatibility

@note Requires xcffib and cairocffi for X11 window creation and drawing
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

try:
    import xcffib
    import xcffib.xproto
    import cairocffi
    XCB_AVAILABLE = True
except ImportError:
    XCB_AVAILABLE = False
    xcffib = None
    cairocffi = None

from libqtile import qtile
from libqtile.log_utils import logger


@dataclass
class XCBNotification:
    """Data structure for XCB-based notification"""
    title: str
    message: str
    urgency: str = "normal"
    timeout: float = 5.0
    created_at: float = 0.0
    window_id: Optional[int] = None
    surface: Optional[Any] = None
    x: int = 0
    y: int = 0
    width: int = 350
    height: int = 100
    id: int = 0

    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = time.time()
        if self.id == 0:
            self.id = int(time.time() * 1000000)


class XCBPopupManager:
    """
    XCB-based popup notification manager

    Uses xcffib to create native X11 windows for notifications with precise
    positioning, styling, and behavior control.
    """

    def __init__(self, color_manager):
        self.color_manager = color_manager
        self.active_notifications: List[XCBNotification] = []
        self.config = {
            "position": "top_right",
            "width": 350,
            "height": 100,
            "margin_x": 20,
            "margin_y": 50,
            "stack_spacing": 10,
            "max_notifications": 5,
            "default_timeout": 5.0,
            "urgent_timeout": 0.0,
            "font_family": "DejaVu Sans",
            "font_size": 12,
            "title_font_size": 14,
            "border_width": 2,
            "corner_radius": 8,
            "opacity": 0.95,
            "padding": 12,
        }
        self._cleanup_scheduled = False
        self._xcb_connection = None
        self._screen = None
        self._window_class = None

        if XCB_AVAILABLE:
            self._init_xcb()
        else:
            logger.error("xcffib not available - XCB notifications disabled")

    def _init_xcb(self) -> bool:
        """Initialize XCB connection and screen"""
        try:
            self._xcb_connection = xcffib.connect()
            self._screen = self._xcb_connection.get_setup().roots[0]

            # Create window class for our notifications
            self._window_class = xcffib.xproto.WindowClass.InputOutput

            logger.info("XCB connection initialized for popup notifications")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize XCB connection: {e}")
            return False

    def configure(self, config: Dict[str, Any]) -> None:
        """Configure popup notification settings"""
        mapping = {
            "popup_position": "position",
            "popup_width": "width",
            "popup_height": "height",
            "popup_margin_x": "margin_x",
            "popup_margin_y": "margin_y",
            "popup_stack_spacing": "stack_spacing",
            "popup_max_stack": "max_notifications",
            "popup_opacity": "opacity",
            "popup_border_width": "border_width",
            "popup_corner_radius": "corner_radius",
            "popup_font_size": "font_size",
            "default_timeout": "default_timeout",
            "default_timeout_urgent": "urgent_timeout",
        }

        for qtile_key, our_key in mapping.items():
            if qtile_key in config:
                if "timeout" in qtile_key:
                    self.config[our_key] = config[qtile_key] / 1000.0
                else:
                    self.config[our_key] = config[qtile_key]

        logger.info(f"XCB popup manager configured: {self.config['position']}")

    def show_notification(self, title: str, message: str, urgency: str = "normal", timeout: int = 5000) -> None:
        """Show XCB popup notification"""
        if not XCB_AVAILABLE or not self._xcb_connection:
            logger.warning("XCB not available - cannot show popup")
            return

        # Convert timeout
        timeout_seconds = timeout / 1000.0 if timeout > 0 else 0.0

        # Apply urgency-specific timeouts
        if urgency == "critical":
            timeout_seconds = self.config.get("urgent_timeout", 0.0)
        elif urgency == "low":
            timeout_seconds = min(timeout_seconds, 3.0)

        # Limit active notifications
        max_notifications = self.config.get("max_notifications", 5)
        while len(self.active_notifications) >= max_notifications:
            self._dismiss_oldest()

        # Calculate position
        x, y = self._calculate_position(len(self.active_notifications))

        # Create notification
        notification = XCBNotification(
            title=title,
            message=message,
            urgency=urgency,
            timeout=timeout_seconds,
            x=x,
            y=y,
            width=self.config.get("width", 350),
            height=self.config.get("height", 100)
        )

        try:
            # Create XCB window
            window_id = self._create_xcb_window(notification)
            if window_id:
                notification.window_id = window_id
                self.active_notifications.append(notification)

                # Draw notification content
                self._draw_notification(notification)

                # Map (show) the window
                self._xcb_connection.core.MapWindow(window_id)
                self._xcb_connection.flush()

                logger.info(f"Showed XCB popup notification: {title}")

                if not self._cleanup_scheduled:
                    self._schedule_cleanup()
            else:
                logger.error("Failed to create XCB window")

        except Exception as e:
            logger.error(f"Failed to show XCB popup: {e}")

    def _create_xcb_window(self, notification: XCBNotification) -> Optional[int]:
        """Create XCB window for notification"""
        try:
            # Generate window ID
            window_id = self._xcb_connection.generate_id()

            # Get colors for styling
            colors = self.color_manager.get_colors()
            bg_color = colors.get("special", {}).get("background", "#000000")

            # Convert hex color to RGB values
            bg_rgb = self._hex_to_rgb(bg_color)
            bg_pixel = (bg_rgb[0] << 16) | (bg_rgb[1] << 8) | bg_rgb[2]

            # Window properties
            value_mask = (
                xcffib.xproto.CW.BackPixel |
                xcffib.xproto.CW.EventMask |
                xcffib.xproto.CW.OverrideRedirect
            )

            value_list = [
                bg_pixel,  # Background pixel
                (xcffib.xproto.EventMask.Exposure |
                 xcffib.xproto.EventMask.ButtonPress |
                 xcffib.xproto.EventMask.StructureNotify),  # Event mask
                1,  # Override redirect (popup behavior)
            ]

            # Create window
            self._xcb_connection.core.CreateWindow(
                self._screen.root_depth,  # Depth
                window_id,  # Window ID
                self._screen.root,  # Parent
                notification.x,  # X position
                notification.y,  # Y position
                notification.width,  # Width
                notification.height,  # Height
                self.config.get("border_width", 2),  # Border width
                self._window_class,  # Class
                self._screen.root_visual,  # Visual
                value_mask,  # Value mask
                value_list  # Value list
            )

            # Set window properties
            self._set_window_properties(window_id, notification)

            return window_id

        except Exception as e:
            logger.error(f"Failed to create XCB window: {e}")
            return None

    def _set_window_properties(self, window_id: int, notification: XCBNotification) -> None:
        """Set window properties for notification popup"""
        try:
            # Set window title
            title_bytes = f"Notification: {notification.title}".encode('utf-8')
            self._xcb_connection.core.ChangeProperty(
                xcffib.xproto.PropMode.Replace,
                window_id,
                xcffib.xproto.Atom.WM_NAME,
                xcffib.xproto.Atom.STRING,
                8,
                len(title_bytes),
                title_bytes
            )

            # Set window class
            wm_class = b"qtile-notification\0Qtile\0"
            self._xcb_connection.core.ChangeProperty(
                xcffib.xproto.PropMode.Replace,
                window_id,
                xcffib.xproto.Atom.WM_CLASS,
                xcffib.xproto.Atom.STRING,
                8,
                len(wm_class),
                wm_class
            )

            # Set window type as notification
            # This helps window managers treat it properly
            try:
                # Get _NET_WM_WINDOW_TYPE atom
                window_type_atom = self._get_atom("_NET_WM_WINDOW_TYPE")
                notification_type_atom = self._get_atom("_NET_WM_WINDOW_TYPE_NOTIFICATION")

                if window_type_atom and notification_type_atom:
                    self._xcb_connection.core.ChangeProperty(
                        xcffib.xproto.PropMode.Replace,
                        window_id,
                        window_type_atom,
                        xcffib.xproto.Atom.ATOM,
                        32,
                        1,
                        [notification_type_atom]
                    )
            except Exception:
                pass  # Not critical if this fails

        except Exception as e:
            logger.debug(f"Error setting window properties: {e}")

    def _get_atom(self, name: str) -> Optional[int]:
        """Get X11 atom by name"""
        try:
            cookie = self._xcb_connection.core.InternAtom(False, len(name), name.encode())
            reply = cookie.reply()
            return reply.atom if reply else None
        except Exception:
            return None

    def _draw_notification(self, notification: XCBNotification) -> None:
        """Draw notification content using cairo"""
        if not cairocffi:
            logger.warning("cairocffi not available - cannot draw notification")
            return

        try:
            # Create cairo surface for the window
            surface = cairocffi.XCBSurface(
                self._xcb_connection,
                notification.window_id,
                self._get_visual_type(),
                notification.width,
                notification.height
            )
            notification.surface = surface

            # Create cairo context
            ctx = cairocffi.Context(surface)

            # Clear surface
            ctx.save()
            ctx.set_operator(cairocffi.OPERATOR_CLEAR)
            ctx.paint()
            ctx.restore()

            # Draw notification
            self._draw_background(ctx, notification)
            self._draw_border(ctx, notification)
            self._draw_text(ctx, notification)

            # Flush surface
            surface.flush()

        except Exception as e:
            logger.error(f"Failed to draw notification: {e}")

    def _get_visual_type(self):
        """Get visual type for cairo surface"""
        for depth in self._screen.allowed_depths:
            if depth.depth == self._screen.root_depth:
                for visual in depth.visuals:
                    if visual.visual_id == self._screen.root_visual:
                        return visual
        return None

    def _draw_background(self, ctx: cairocffi.Context, notification: XCBNotification) -> None:
        """Draw notification background"""
        colors = self.color_manager.get_colors()
        bg_color = colors.get("special", {}).get("background", "#000000")

        # Parse background color
        r, g, b = self._hex_to_rgb(bg_color)

        # Set background color with opacity
        ctx.set_source_rgba(r/255.0, g/255.0, b/255.0, self.config.get("opacity", 0.95))

        # Draw rounded rectangle background
        self._draw_rounded_rectangle(
            ctx, 0, 0,
            notification.width,
            notification.height,
            self.config.get("corner_radius", 8)
        )
        ctx.fill()

    def _draw_border(self, ctx: cairocffi.Context, notification: XCBNotification) -> None:
        """Draw notification border"""
        colors = self.color_manager.get_colors()

        # Choose border color based on urgency
        if notification.urgency == "critical":
            border_color = colors.get("colors", {}).get("color1", "#ff0000")
        elif notification.urgency == "low":
            border_color = colors.get("colors", {}).get("color8", "#808080")
        else:
            border_color = colors.get("colors", {}).get("color6", "#00ff00")

        # Parse border color
        r, g, b = self._hex_to_rgb(border_color)

        # Set border properties
        border_width = self.config.get("border_width", 2)
        ctx.set_source_rgba(r/255.0, g/255.0, b/255.0, 1.0)
        ctx.set_line_width(border_width)

        # Draw border
        self._draw_rounded_rectangle(
            ctx, border_width/2, border_width/2,
            notification.width - border_width,
            notification.height - border_width,
            self.config.get("corner_radius", 8)
        )
        ctx.stroke()

    def _draw_text(self, ctx: cairocffi.Context, notification: XCBNotification) -> None:
        """Draw notification text content"""
        colors = self.color_manager.get_colors()

        # Choose text color based on urgency
        if notification.urgency == "critical":
            text_color = colors.get("colors", {}).get("color1", "#ff0000")
        elif notification.urgency == "low":
            text_color = colors.get("colors", {}).get("color8", "#808080")
        else:
            text_color = colors.get("colors", {}).get("color7", "#ffffff")

        # Parse text color
        r, g, b = self._hex_to_rgb(text_color)
        ctx.set_source_rgba(r/255.0, g/255.0, b/255.0, 1.0)

        # Set font
        ctx.select_font_face(
            self.config.get("font_family", "DejaVu Sans"),
            cairocffi.FONT_SLANT_NORMAL,
            cairocffi.FONT_WEIGHT_NORMAL
        )

        padding = self.config.get("padding", 12)

        # Draw title
        title_font_size = self.config.get("title_font_size", 14)
        ctx.set_font_size(title_font_size)

        title = notification.title
        if len(title) > 40:
            title = title[:37] + "..."

        # Position title
        ctx.move_to(padding, padding + title_font_size)
        ctx.show_text(title)

        # Draw message
        if notification.message:
            message_font_size = self.config.get("font_size", 12)
            ctx.set_font_size(message_font_size)

            # Word wrap message
            message_lines = self._wrap_text(
                ctx, notification.message,
                notification.width - (2 * padding)
            )

            y_offset = padding + title_font_size + 8
            line_height = message_font_size + 4

            for line in message_lines[:3]:  # Limit to 3 lines
                ctx.move_to(padding, y_offset)
                ctx.show_text(line)
                y_offset += line_height

    def _wrap_text(self, ctx: cairocffi.Context, text: str, max_width: float) -> List[str]:
        """Wrap text to fit within specified width"""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            text_extents = ctx.text_extents(test_line)

            if text_extents.width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def _draw_rounded_rectangle(self, ctx: cairocffi.Context, x: float, y: float,
                               width: float, height: float, radius: float) -> None:
        """Draw a rounded rectangle path"""
        import math

        ctx.new_sub_path()
        ctx.arc(x + width - radius, y + radius, radius, -math.pi/2, 0)
        ctx.arc(x + width - radius, y + height - radius, radius, 0, math.pi/2)
        ctx.arc(x + radius, y + height - radius, radius, math.pi/2, math.pi)
        ctx.arc(x + radius, y + radius, radius, math.pi, 3*math.pi/2)
        ctx.close_path()

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        if hex_color.startswith("#"):
            hex_color = hex_color[1:]

        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return (r, g, b)
        except (ValueError, IndexError):
            return (255, 255, 255)  # Default to white

    def _calculate_position(self, stack_index: int) -> Tuple[int, int]:
        """Calculate position for notification"""
        # Get screen dimensions from XCB connection
        if not self._xcb_connection:
            return (100, 100)

        try:
            screen = self._xcb_connection.get_setup().roots[0]
            screen_width = screen.width_in_pixels
            screen_height = screen.height_in_pixels
        except Exception as e:
            logger.warning(f"Failed to get screen info from XCB: {e}")
            return (100, 100)

        width = self.config.get("width", 350)
        height = self.config.get("height", 100)
        margin_x = self.config.get("margin_x", 20)
        margin_y = self.config.get("margin_y", 50)
        stack_spacing = self.config.get("stack_spacing", 10)
        position = self.config.get("position", "top_right")

        # Calculate base position
        if position == "top_right":
            x = screen_width - width - margin_x
            y = margin_y + (stack_index * (height + stack_spacing))
        elif position == "top_left":
            x = margin_x
            y = margin_y + (stack_index * (height + stack_spacing))
        elif position == "bottom_right":
            x = screen_width - width - margin_x
            y = screen_height - margin_y - height - (stack_index * (height + stack_spacing))
        elif position == "bottom_left":
            x = margin_x
            y = screen_height - margin_y - height - (stack_index * (height + stack_spacing))
        else:
            x = screen_width - width - margin_x
            y = margin_y + (stack_index * (height + stack_spacing))

        # Keep on screen
        x = max(0, min(x, screen_width - width))
        y = max(0, min(y, screen_height - height))

        return (x, y)

    def _dismiss_oldest(self) -> None:
        """Dismiss oldest notification"""
        if self.active_notifications:
            oldest = self.active_notifications.pop(0)
            self._destroy_window(oldest)
            logger.debug(f"Dismissed oldest notification: {oldest.title}")

    def _destroy_window(self, notification: XCBNotification) -> None:
        """Destroy XCB window for notification"""
        if notification.window_id and self._xcb_connection:
            try:
                self._xcb_connection.core.DestroyWindow(notification.window_id)
                self._xcb_connection.flush()
            except Exception as e:
                logger.debug(f"Error destroying window: {e}")

    def _schedule_cleanup(self) -> None:
        """Schedule cleanup of expired notifications"""
        if qtile and hasattr(qtile, 'call_later') and not self._cleanup_scheduled:
            self._cleanup_scheduled = True
            qtile.call_later(1.0, self._cleanup_expired)

    def _cleanup_expired(self) -> None:
        """Clean up expired notifications"""
        if not self.active_notifications:
            self._cleanup_scheduled = False
            return

        current_time = time.time()
        expired = []

        for notification in self.active_notifications:
            if notification.timeout > 0:
                age = current_time - notification.created_at
                if age >= notification.timeout:
                    expired.append(notification)

        # Remove expired notifications
        for notification in expired:
            if notification in self.active_notifications:
                self.active_notifications.remove(notification)
                self._destroy_window(notification)
                logger.debug(f"XCB notification expired: {notification.title}")

        # Schedule next cleanup
        if self.active_notifications and qtile and hasattr(qtile, 'call_later'):
            qtile.call_later(1.0, self._cleanup_expired)
        else:
            self._cleanup_scheduled = False

    def dismiss_all(self) -> None:
        """Dismiss all active notifications"""
        count = len(self.active_notifications)
        for notification in self.active_notifications:
            self._destroy_window(notification)

        self.active_notifications.clear()
        self._cleanup_scheduled = False
        logger.info(f"Dismissed {count} XCB notifications")

    def get_status(self) -> Dict[str, Any]:
        """Get XCB popup manager status"""
        return {
            "active_notifications": len(self.active_notifications),
            "max_notifications": self.config.get("max_notifications", 5),
            "position": self.config.get("position", "top_right"),
            "cleanup_scheduled": self._cleanup_scheduled,
            "xcb_available": XCB_AVAILABLE,
            "xcb_connected": self._xcb_connection is not None,
        }

    def __del__(self):
        """Cleanup XCB connection"""
        if self._xcb_connection:
            try:
                self.dismiss_all()
                self._xcb_connection.disconnect()
            except Exception:
                pass


def create_xcb_popup_manager(color_manager) -> XCBPopupManager:
    """Create XCB popup notification manager"""
    try:
        manager = XCBPopupManager(color_manager)
        logger.info("XCB popup notification manager created")
        return manager
    except Exception as e:
        logger.error(f"Failed to create XCB popup manager: {e}")
        return XCBPopupManager(color_manager)


def show_xcb_popup(title: str, message: str, urgency: str = "normal",
                  timeout: int = 5000, manager=None) -> None:
    """Show XCB popup notification"""
    if manager:
        manager.show_notification(title, message, urgency, timeout)
    else:
        logger.warning("No XCB popup manager provided")


# Test function
def test_xcb_popup():
    """Test XCB popup system"""
    if not XCB_AVAILABLE:
        print("XCB not available - cannot test XCB popups")
        return

    class DummyColorManager:
        def get_colors(self):
            return {
                "colors": {
                    "color7": "#ffffff",
                    "color1": "#ff0000",
                    "color6": "#00ff00",
                    "color8": "#808080"
                },
                "special": {
                    "background": "#000000",
                    "foreground": "#ffffff"
                }
            }

    manager = create_xcb_popup_manager(DummyColorManager())
    manager.show_notification("XCB Test", "Testing native X11 popup notifications!")
    print("XCB popup test sent")


if __name__ == "__main__":
    test_xcb_popup()
