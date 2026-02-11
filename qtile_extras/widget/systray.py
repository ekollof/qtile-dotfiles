# Copyright (c) 2022, elParaguayo. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
Enhanced Systray widget with improved dark icon visibility.

This implementation extends the base qtile Systray to provide better icon
background handling for dark themes where dark icons become invisible.
"""
import xcffib
from libqtile import widget

from qtile_extras.widget.decorations import RectDecoration

XEMBED_PROTOCOL_VERSION = 0


class Systray(widget.Systray):
    """
    Enhanced Systray widget with improved icon background handling.

    This version adds the ability to set a custom background color specifically
    for icon areas, solving the dark-icons-on-dark-background visibility problem.
    
    Key improvements over base Systray:
    - icon_background parameter for custom icon area backgrounds
    - Better integration with RectDecoration
    - Per-icon background pixel control for consistent appearance
    
    @brief Enhanced system tray with dark icon visibility fixes
    """

    _qte_compatibility = True
    
    defaults = [
        (
            "icon_background",
            None,
            "Background color for icon areas. Use a lighter color (e.g., '#A09D9B') "
            "to make dark icons visible on dark bars. Set to None to use widget background.",
        ),
    ]
    
    def __init__(self, **config):
        widget.Systray.__init__(self, **config)
        self.add_defaults(Systray.defaults)

    def draw(self):
        """
        Draw the system tray and position icons.
        
        This method handles icon background rendering with three priority levels:
        1. RectDecoration fill color (if using decorations)
        2. Custom icon_background color (if specified)
        3. Widget/bar background pixmap (fallback)
        
        @brief Render system tray icons with appropriate backgrounds
        """
        offset = self.padding
        self.drawer.clear(self.background or self.bar.background)
        self.draw_at_default_position()
        
        for pos, icon in enumerate(self.tray_icons):
            # Determine the appropriate background for this icon
            # Priority: RectDecoration > icon_background > pixmap
            background_set = False
            
            # Check if we're using a RectDecoration
            rect_decs = [d for d in self.decorations if isinstance(d, RectDecoration)]
            if rect_decs:
                top = rect_decs[-1]
                if top.filled:
                    fill_colour = top.fill_colour
                else:
                    fill_colour = self.background or self.bar.background
                
                # Convert color string to integer (remove # prefix if present)
                if fill_colour.startswith("#"):
                    fill_colour = fill_colour[1:]
                icon.window.set_attribute(backpixel=int(fill_colour, 16))
                background_set = True
            
            # Use custom icon background if specified and no decoration
            elif self.icon_background:
                fill_colour = self.icon_background
                if fill_colour.startswith("#"):
                    fill_colour = fill_colour[1:]
                icon.window.set_attribute(backpixel=int(fill_colour, 16))
                background_set = True
            
            # Fallback to pixmap (original behavior)
            if not background_set:
                # Note: backpixmap can have translation issues as it copies from 0,0
                # but this preserves compatibility with transparent bars
                icon.window.set_attribute(backpixmap=self.drawer.pixmap)

            # Position the icon based on bar orientation
            if self.bar.horizontal:
                xoffset = self.offsetx + offset
                yoffset = self.bar.height // 2 - self.icon_size // 2 + self.offsety
                step = icon.width
            else:
                xoffset = self.bar.width // 2 - self.icon_size // 2 + self.offsetx
                yoffset = self.offsety + offset
                step = icon.height

            icon.place(xoffset, yoffset, icon.width, self.icon_size, 0, None)
            
            # Send embed notification for newly visible icons
            if icon.hidden:
                icon.unhide()
                data = [
                    self.conn.atoms["_XEMBED_EMBEDDED_NOTIFY"],
                    xcffib.xproto.Time.CurrentTime,
                    0,
                    self.bar.window.wid,
                    XEMBED_PROTOCOL_VERSION,
                ]
                u = xcffib.xproto.ClientMessageData.synthetic(data, "I" * 5)
                event = xcffib.xproto.ClientMessageEvent.synthetic(
                    format=32, window=icon.wid, type=self.conn.atoms["_XEMBED"], data=u
                )
                self.window.send_event(event)

            offset += step + self.padding
