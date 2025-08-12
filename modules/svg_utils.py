#!/usr/bin/env python3
"""
SVG utilities for qtile - Dynamic icon generation and manipulation
Provides tools to create, modify, scale, and color SVG icons programmatically

@brief SVG manipulation system for qtile icons with theme integration
@author qtile configuration system
"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from modules.dpi_utils import scale_size


@dataclass
class SVGIcon:
    """
    @brief Container for SVG icon data and metadata

    Holds SVG content, dimensions, and styling information
    for programmatic manipulation.
    """
    content: str
    width: int
    height: int
    fill_color: str = "#ffffff"
    stroke_color: str = "#000000"
    stroke_width: float = 1.0
    viewbox: str | None = None


class SVGBuilder:
    """
    @brief SVG builder for creating icons programmatically

    Provides methods to create common icon shapes and patterns
    with proper scaling and coloring for qtile widgets.
    """

    def __init__(self, width: int = 24, height: int = 24) -> None:
        """
        @brief Initialize SVG builder with dimensions
        @param width: SVG width in pixels
        @param height: SVG height in pixels
        """
        self.width = width
        self.height = height
        self.elements: List[str] = []
        self.defs: List[str] = []

    def add_circle(self, cx: float, cy: float, r: float,
                   fill: str = "#ffffff", stroke: str = "none",
                   stroke_width: float = 0) -> "SVGBuilder":
        """
        @brief Add a circle element to the SVG
        @param cx: Center X coordinate
        @param cy: Center Y coordinate
        @param r: Radius
        @param fill: Fill color
        @param stroke: Stroke color
        @param stroke_width: Stroke width
        @return Self for method chaining
        """
        circle = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"'
        if stroke != "none":
            circle += f' stroke="{stroke}" stroke-width="{stroke_width}"'
        circle += '/>'
        self.elements.append(circle)
        return self

    def add_rect(self, x: float, y: float, width: float, height: float,
                 fill: str = "#ffffff", stroke: str = "none",
                 stroke_width: float = 0, rx: float = 0) -> "SVGBuilder":
        """
        @brief Add a rectangle element to the SVG
        @param x: X coordinate
        @param y: Y coordinate
        @param width: Rectangle width
        @param height: Rectangle height
        @param fill: Fill color
        @param stroke: Stroke color
        @param stroke_width: Stroke width
        @param rx: Corner radius
        @return Self for method chaining
        """
        rect = f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="{fill}"'
        if rx > 0:
            rect += f' rx="{rx}"'
        if stroke != "none":
            rect += f' stroke="{stroke}" stroke-width="{stroke_width}"'
        rect += '/>'
        self.elements.append(rect)
        return self

    def add_path(self, d: str, fill: str = "#ffffff",
                 stroke: str = "none", stroke_width: float = 0) -> "SVGBuilder":
        """
        @brief Add a path element to the SVG
        @param d: Path data string
        @param fill: Fill color
        @param stroke: Stroke color
        @param stroke_width: Stroke width
        @return Self for method chaining
        """
        path = f'<path d="{d}" fill="{fill}"'
        if stroke != "none":
            path += f' stroke="{stroke}" stroke-width="{stroke_width}"'
        path += '/>'
        self.elements.append(path)
        return self

    def add_text(self, text: str, x: float, y: float,
                 font_size: int = 12, fill: str = "#ffffff",
                 font_family: str = "sans-serif",
                 text_anchor: str = "start") -> "SVGBuilder":
        """
        @brief Add text element to the SVG
        @param text: Text content
        @param x: X coordinate
        @param y: Y coordinate
        @param font_size: Font size
        @param fill: Text color
        @param font_family: Font family
        @param text_anchor: Text anchor (start, middle, end)
        @return Self for method chaining
        """
        text_elem = (f'<text x="{x}" y="{y}" font-size="{font_size}" '
                    f'fill="{fill}" font-family="{font_family}" '
                    f'text-anchor="{text_anchor}">{text}</text>')
        self.elements.append(text_elem)
        return self

    def add_polygon(self, points: List[Tuple[float, float]],
                    fill: str = "#ffffff", stroke: str = "none",
                    stroke_width: float = 0) -> "SVGBuilder":
        """
        @brief Add polygon element to the SVG
        @param points: List of (x, y) coordinate tuples
        @param fill: Fill color
        @param stroke: Stroke color
        @param stroke_width: Stroke width
        @return Self for method chaining
        """
        points_str = " ".join(f"{x},{y}" for x, y in points)
        polygon = f'<polygon points="{points_str}" fill="{fill}"'
        if stroke != "none":
            polygon += f' stroke="{stroke}" stroke-width="{stroke_width}"'
        polygon += '/>'
        self.elements.append(polygon)
        return self

    def add_gradient(self, gradient_id: str, stops: List[Tuple[str, str]]) -> "SVGBuilder":
        """
        @brief Add linear gradient definition
        @param gradient_id: Unique ID for the gradient
        @param stops: List of (offset, color) tuples
        @return Self for method chaining
        """
        gradient = [f'<linearGradient id="{gradient_id}">']
        for offset, color in stops:
            gradient.append(f'  <stop offset="{offset}" stop-color="{color}"/>')
        gradient.append('</linearGradient>')
        self.defs.extend(gradient)
        return self

    def build(self, viewbox: str | None = None) -> str:
        """
        @brief Build the complete SVG string
        @param viewbox: Optional viewbox attribute
        @return Complete SVG as string
        """
        if viewbox is None:
            viewbox = f"0 0 {self.width} {self.height}"

        svg = [
            f'<svg width="{self.width}" height="{self.height}" '
            f'viewBox="{viewbox}" xmlns="http://www.w3.org/2000/svg">',
        ]

        if self.defs:
            svg.append('<defs>')
            svg.extend(self.defs)
            svg.append('</defs>')

        svg.extend(self.elements)
        svg.append('</svg>')

        return '\n'.join(svg)


class SVGManipulator:
    """
    @brief SVG file manipulation and color management

    Provides methods to load, modify, and save SVG files with
    dynamic coloring and scaling capabilities.
    """

    def __init__(self, color_manager=None) -> None:
        """
        @brief Initialize SVG manipulator
        @param color_manager: Optional color manager for theme integration
        """
        self.color_manager = color_manager

    def load_svg(self, file_path: Path | str) -> SVGIcon | None:
        """
        @brief Load SVG file and parse metadata
        @param file_path: Path to SVG file
        @return SVGIcon object or None if load fails
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return None

            content = path.read_text(encoding='utf-8')

            # Parse basic attributes
            root = ET.fromstring(content)
            width = self._parse_dimension(root.get('width', '24'))
            height = self._parse_dimension(root.get('height', '24'))
            viewbox = root.get('viewBox')

            return SVGIcon(
                content=content,
                width=width,
                height=height,
                viewbox=viewbox
            )

        except Exception:
            return None

    def _parse_dimension(self, dim_str: str) -> int:
        """
        @brief Parse dimension string to integer
        @param dim_str: Dimension string (may include 'px', 'pt', etc.)
        @return Integer dimension value
        """
        # Remove units and convert to int
        numeric = re.sub(r'[^0-9.]', '', dim_str)
        try:
            return int(float(numeric))
        except ValueError:
            return 24  # Default fallback

    def recolor_svg(self, svg_icon: SVGIcon, color_map: Dict[str, str]) -> SVGIcon:
        """
        @brief Recolor SVG by replacing color values
        @param svg_icon: SVGIcon to modify
        @param color_map: Dictionary mapping old colors to new colors
        @return Modified SVGIcon
        """
        content = svg_icon.content

        for old_color, new_color in color_map.items():
            # Normalize color format
            old_color = old_color.lower().strip()
            if old_color.startswith('#'):
                old_hex = old_color[1:]
            else:
                old_hex = old_color

            # Replace various color formats
            patterns = [
                rf'fill="#{old_hex}"',
                rf'stroke="#{old_hex}"',
                rf'fill="{old_color}"',
                rf'stroke="{old_color}"',
                rf'fill:\s*#{old_hex}',
                rf'stroke:\s*#{old_hex}',
                rf'stop-color="#{old_hex}"',
                rf'stop-color="{old_color}"',
            ]

            replacements = [
                f'fill="{new_color}"',
                f'stroke="{new_color}"',
                f'fill="{new_color}"',
                f'stroke="{new_color}"',
                f'fill:{new_color}',
                f'stroke:{new_color}',
                f'stop-color="{new_color}"',
                f'stop-color="{new_color}"',
            ]

            for pattern, replacement in zip(patterns, replacements):
                content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

        return SVGIcon(
            content=content,
            width=svg_icon.width,
            height=svg_icon.height,
            viewbox=svg_icon.viewbox
        )

    def scale_svg(self, svg_icon: SVGIcon, scale_factor: float) -> SVGIcon:
        """
        @brief Scale SVG dimensions by factor
        @param svg_icon: SVGIcon to scale
        @param scale_factor: Scaling factor (1.0 = no change)
        @return Scaled SVGIcon
        """
        new_width = int(svg_icon.width * scale_factor)
        new_height = int(svg_icon.height * scale_factor)

        # Update width and height attributes
        content = svg_icon.content
        content = re.sub(r'width="[^"]*"', f'width="{new_width}"', content)
        content = re.sub(r'height="[^"]*"', f'height="{new_height}"', content)

        return SVGIcon(
            content=content,
            width=new_width,
            height=new_height,
            viewbox=svg_icon.viewbox
        )

    def theme_colorize(self, svg_icon: SVGIcon, theme_colors: Dict[str, str] | None = None) -> SVGIcon:
        """
        @brief Apply theme colors to SVG
        @param svg_icon: SVGIcon to colorize
        @param theme_colors: Optional color overrides
        @return Themed SVGIcon
        """
        if self.color_manager is None and theme_colors is None:
            return svg_icon

        colors = theme_colors or {}
        if self.color_manager:
            qtile_colors = self.color_manager.get_colors()
            colors.update({
                "foreground": qtile_colors["special"]["foreground"],
                "background": qtile_colors["special"]["background"],
                "accent": qtile_colors["colors"]["color5"],
                "highlight": qtile_colors["colors"]["color6"],
                "warning": qtile_colors["colors"]["color3"],
                "error": qtile_colors["colors"]["color1"],
            })

        # Common color replacements
        color_map = {
            "#ffffff": colors.get("foreground", "#ffffff"),
            "#000000": colors.get("background", "#000000"),
            "white": colors.get("foreground", "#ffffff"),
            "black": colors.get("background", "#000000"),
            "#ff0000": colors.get("error", "#ff0000"),
            "#ffff00": colors.get("warning", "#ffff00"),
            "#0000ff": colors.get("accent", "#0000ff"),
        }

        return self.recolor_svg(svg_icon, color_map)

    def save_svg(self, svg_icon: SVGIcon, file_path: Path | str) -> bool:
        """
        @brief Save SVG to file
        @param svg_icon: SVGIcon to save
        @param file_path: Output file path
        @return True if save successful
        """
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(svg_icon.content, encoding='utf-8')
            return True
        except Exception:
            return False


class IconGenerator:
    """
    @brief Generator for common qtile icons

    Creates standard icons used in qtile bars with consistent
    styling and theme integration.
    """

    def __init__(self, color_manager=None, size: int = 24) -> None:
        """
        @brief Initialize icon generator
        @param color_manager: Optional color manager for theming
        @param size: Default icon size
        """
        self.color_manager = color_manager
        self.size = scale_size(size)  # DPI-aware sizing
        self.colors = self._get_colors()

    def _get_colors(self) -> Dict[str, str]:
        """
        @brief Get color palette for icons
        @return Dictionary of colors
        """
        if self.color_manager:
            qtile_colors = self.color_manager.get_colors()
            return {
                "foreground": qtile_colors["special"]["foreground"],
                "background": qtile_colors["special"]["background"],
                "accent": qtile_colors["colors"]["color5"],
                "highlight": qtile_colors["colors"]["color6"],
                "warning": qtile_colors["colors"]["color3"],
                "error": qtile_colors["colors"]["color1"],
                "muted": qtile_colors["colors"]["color8"],
            }
        else:
            return {
                "foreground": "#ffffff",
                "background": "#000000",
                "accent": "#5f87af",
                "highlight": "#87af87",
                "warning": "#d7af5f",
                "error": "#d75f5f",
                "muted": "#808080",
            }

    def battery_icon(self, level: int = 100, charging: bool = False) -> str:
        """
        @brief Generate battery icon SVG
        @param level: Battery level (0-100)
        @param charging: Whether battery is charging
        @return SVG string
        """
        builder = SVGBuilder(self.size, self.size)

        # Battery outline
        outline_color = self.colors["foreground"]
        builder.add_rect(4, 6, 16, 12, fill="none",
                        stroke=outline_color, stroke_width=1.5, rx=1)

        # Battery terminal
        builder.add_rect(20, 9, 2, 6, fill=outline_color)

        # Battery fill based on level
        match True:
            case _ if level > 75:
                fill_color = self.colors["accent"]
            case _ if level > 50:
                fill_color = self.colors["highlight"]
            case _ if level > 25:
                fill_color = self.colors["warning"]
            case _ if level > 10:
                fill_color = self.colors["warning"]
            case _:
                fill_color = self.colors["error"]

        fill_width = max(1, (level / 100) * 14)
        builder.add_rect(5, 7, fill_width, 10, fill=fill_color)

        # Charging indicator
        if charging:
            builder.add_path("M12 8l-2 4h1.5l-.5 4 2-4h-1.5z",
                           fill=self.colors["warning"])

        return builder.build()

    def wifi_icon(self, strength: int = 3, connected: bool = True) -> str:
        """
        @brief Generate WiFi signal icon
        @param strength: Signal strength (0-3)
        @param connected: Whether WiFi is connected
        @return SVG string
        """
        builder = SVGBuilder(self.size, self.size)

        if not connected:
            # Disconnected WiFi with X
            builder.add_path("M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zM8.5 7.5l7 7-1 1-7-7 1-1z",
                           fill=self.colors["muted"])
            return builder.build()

        # WiFi signal arcs
        center_x, center_y = self.size // 2, self.size // 2 + 2

        # Signal strength arcs (from innermost to outermost)
        arcs = [
            (3, 1.5),  # Innermost arc
            (6, 2.5),  # Middle arc
            (9, 3.5),  # Outermost arc
        ]

        for i, (radius, stroke_width) in enumerate(arcs):
            if strength > i:
                color = self.colors["accent"]
            else:
                color = self.colors["muted"]

            # Create arc using path
            start_angle = 225  # Bottom-left
            end_angle = 315    # Bottom-right

            x1 = center_x + radius * 0.707  # cos(45°)
            y1 = center_y + radius * 0.707  # sin(45°)
            x2 = center_x - radius * 0.707
            y2 = center_y + radius * 0.707

            arc_path = f"M {x1} {y1} A {radius} {radius} 0 0 0 {x2} {y2}"
            builder.add_path(arc_path, fill="none", stroke=color, stroke_width=stroke_width)

        # Center dot
        builder.add_circle(center_x, center_y, 1.5, fill=self.colors["foreground"])

        return builder.build()

    def volume_icon(self, level: int = 100, muted: bool = False) -> str:
        """
        @brief Generate volume icon
        @param level: Volume level (0-100)
        @param muted: Whether volume is muted
        @return SVG string
        """
        builder = SVGBuilder(self.size, self.size)

        # Speaker base
        speaker_color = self.colors["foreground"]
        builder.add_path("M3 9v6h4l5 5V4L7 9H3z", fill=speaker_color)

        if muted:
            # Muted X
            builder.add_path("M16.5 12L14 9.5L15.5 8L18 10.5L20.5 8L22 9.5L19.5 12L22 14.5L20.5 16L18 13.5L15.5 16L14 14.5L16.5 12z",
                           fill=self.colors["error"])
        else:
            # Volume arcs based on level
            if level > 0:
                builder.add_path("M14 8.83v6.34c1.59-.72 2.5-2.07 2.5-3.67S15.59 9.55 14 8.83z",
                               fill=self.colors["accent"])
            if level > 33:
                builder.add_path("M16 6.25v11.5c2.92-1.33 4.5-3.83 4.5-6.75S18.92 7.58 16 6.25z",
                               fill=self.colors["accent"])
            if level > 66:
                builder.add_path("M18 4v16c4.06-1.86 6.5-5.85 6.5-8S22.06 5.86 18 4z",
                               fill=self.colors["accent"])

        return builder.build()

    def cpu_icon(self, usage: float = 0.0) -> str:
        """
        @brief Generate CPU usage icon
        @param usage: CPU usage percentage (0.0-1.0)
        @return SVG string
        """
        builder = SVGBuilder(self.size, self.size)

        # CPU chip outline
        chip_color = self.colors["foreground"]
        builder.add_rect(6, 6, 12, 12, fill="none", stroke=chip_color, stroke_width=1.5, rx=1)

        # CPU pins (top and bottom)
        for i in range(3):
            x = 8 + i * 3
            # Top pins
            builder.add_rect(x, 3, 1, 3, fill=chip_color)
            # Bottom pins
            builder.add_rect(x, 18, 1, 3, fill=chip_color)

        # CPU pins (left and right)
        for i in range(3):
            y = 8 + i * 3
            # Left pins
            builder.add_rect(3, y, 3, 1, fill=chip_color)
            # Right pins
            builder.add_rect(18, y, 3, 1, fill=chip_color)

        # Usage indicator (fill based on usage)
        if usage > 0.8:
            fill_color = self.colors["error"]
        elif usage > 0.6:
            fill_color = self.colors["warning"]
        else:
            fill_color = self.colors["accent"]

        # Inner square showing usage
        fill_size = 8 * usage
        fill_offset = (8 - fill_size) / 2
        builder.add_rect(8 + fill_offset, 8 + fill_offset, fill_size, fill_size, fill=fill_color)

        return builder.build()

    def memory_icon(self, usage: float = 0.0) -> str:
        """
        @brief Generate memory usage icon
        @param usage: Memory usage percentage (0.0-1.0)
        @return SVG string
        """
        builder = SVGBuilder(self.size, self.size)

        # RAM stick outline
        ram_color = self.colors["foreground"]
        builder.add_rect(6, 4, 12, 16, fill="none", stroke=ram_color, stroke_width=1.5, rx=1)

        # Memory chips (horizontal lines)
        for i in range(3):
            y = 7 + i * 4
            builder.add_rect(8, y, 8, 2, fill=ram_color)

        # Usage indicator
        if usage > 0.8:
            fill_color = self.colors["error"]
        elif usage > 0.6:
            fill_color = self.colors["warning"]
        else:
            fill_color = self.colors["accent"]

        # Fill from bottom up
        fill_height = 14 * usage
        fill_y = 20 - fill_height
        builder.add_rect(7, fill_y, 10, fill_height, fill=fill_color, rx=0.5)

        return builder.build()

    def network_icon(self, rx_active: bool = False, tx_active: bool = False) -> str:
        """
        @brief Generate network activity icon
        @param rx_active: Whether receiving data
        @param tx_active: Whether transmitting data
        @return SVG string
        """
        builder = SVGBuilder(self.size, self.size)

        # Network cable/connector
        connector_color = self.colors["foreground"]
        builder.add_rect(4, 10, 16, 4, fill="none", stroke=connector_color, stroke_width=1.5, rx=1)

        # RX indicator (down arrow)
        rx_color = self.colors["accent"] if rx_active else self.colors["muted"]
        builder.add_polygon([(8, 6), (10, 8), (6, 8)], fill=rx_color)

        # TX indicator (up arrow)
        tx_color = self.colors["accent"] if tx_active else self.colors["muted"]
        builder.add_polygon([(16, 18), (14, 16), (18, 16)], fill=tx_color)

        return builder.build()

    def python_icon(self) -> str:
        """
        @brief Generate Python logo icon
        @return SVG string
        """
        builder = SVGBuilder(self.size, self.size)

        # Python logo inspired design
        # Upper snake body (blue)
        builder.add_path("M12,4 Q8,4 8,8 L8,12 L16,12 L16,8 Q16,4 12,4 Z",
                        fill=self.colors["accent"])

        # Lower snake body (yellow/gold)
        builder.add_path("M12,20 Q16,20 16,16 L16,12 L8,12 L8,16 Q8,20 12,20 Z",
                        fill=self.colors["warning"])

        # Eyes
        builder.add_circle(10, 7, 1, fill=self.colors["foreground"])
        builder.add_circle(14, 17, 1, fill=self.colors["foreground"])

        return builder.build()

    def mail_icon(self) -> str:
        """
        @brief Generate mail/envelope icon
        @return SVG string
        """
        builder = SVGBuilder(self.size, self.size)

        # Envelope body
        builder.add_rect(4, 8, 16, 10, fill="none",
                        stroke=self.colors["foreground"], stroke_width=1.5, rx=1)

        # Envelope flap
        builder.add_path("M4,8 L12,14 L20,8", fill="none",
                        stroke=self.colors["foreground"], stroke_width=1.5)

        # Mail indicator dot
        builder.add_circle(18, 10, 2, fill=self.colors["accent"])

        return builder.build()

    def ticket_icon(self) -> str:
        """
        @brief Generate ticket/support icon
        @return SVG string
        """
        builder = SVGBuilder(self.size, self.size)

        # Ticket body
        builder.add_rect(6, 8, 12, 8, fill=self.colors["accent"],
                        stroke=self.colors["foreground"], stroke_width=1)

        # Perforated edges
        for i in range(3):
            y = 9 + i * 2
            builder.add_circle(6, y, 0.5, fill=self.colors["background"])
            builder.add_circle(18, y, 0.5, fill=self.colors["background"])

        # Ticket number lines
        builder.add_rect(8, 10, 6, 0.5, fill=self.colors["foreground"])
        builder.add_rect(8, 12, 4, 0.5, fill=self.colors["foreground"])
        builder.add_rect(8, 14, 5, 0.5, fill=self.colors["foreground"])

        return builder.build()

    def thermometer_icon(self) -> str:
        """
        @brief Generate thermometer/temperature icon
        @return SVG string
        """
        builder = SVGBuilder(self.size, self.size)

        # Thermometer bulb
        builder.add_circle(12, 18, 3, fill=self.colors["error"])

        # Thermometer tube
        builder.add_rect(11, 6, 2, 12, fill=self.colors["foreground"],
                        stroke=self.colors["foreground"], stroke_width=0.5, rx=1)

        # Temperature scale marks
        for i in range(4):
            y = 8 + i * 2
            builder.add_rect(13.5, y, 1.5, 0.5, fill=self.colors["foreground"])

        # Mercury/temperature indicator
        builder.add_rect(11.2, 15, 1.6, 3, fill=self.colors["error"], rx=0.8)

        return builder.build()


def create_themed_icon_cache(color_manager, icon_dir: Path, size: int = 24) -> Dict[str, str]:
    """
    @brief Create cache of themed icons for qtile widgets
    @param color_manager: Color manager for theme colors
    @param icon_dir: Directory to save generated icons
    @param size: Icon size in pixels
    @return Dictionary mapping icon names to file paths
    """
    generator = IconGenerator(color_manager, size)
    icon_dir = Path(icon_dir)
    icon_dir.mkdir(parents=True, exist_ok=True)

    # Generate static icons
    icons = {
        "battery_full": generator.battery_icon(100),
        "battery_high": generator.battery_icon(75),
        "battery_medium": generator.battery_icon(50),
        "battery_low": generator.battery_icon(25),
        "battery_critical": generator.battery_icon(10),
        "battery_charging": generator.battery_icon(50, charging=True),
        "wifi_full": generator.wifi_icon(3),
        "wifi_medium": generator.wifi_icon(2),
        "wifi_low": generator.wifi_icon(1),
        "wifi_none": generator.wifi_icon(0),
        "wifi_disconnected": generator.wifi_icon(0, connected=False),
        "volume_high": generator.volume_icon(100),
        "volume_medium": generator.volume_icon(50),
        "volume_low": generator.volume_icon(25),
        "volume_muted": generator.volume_icon(0, muted=True),
        "cpu_idle": generator.cpu_icon(0.1),
        "cpu_active": generator.cpu_icon(0.5),
        "cpu_high": generator.cpu_icon(0.8),
        "memory_low": generator.memory_icon(0.3),
        "memory_medium": generator.memory_icon(0.6),
        "memory_high": generator.memory_icon(0.9),
        "network_idle": generator.network_icon(),
        "network_rx": generator.network_icon(rx_active=True),
        "network_tx": generator.network_icon(tx_active=True),
        "network_active": generator.network_icon(rx_active=True, tx_active=True),
        "python": generator.python_icon(),
        "mail": generator.mail_icon(),
        "ticket": generator.ticket_icon(),
        "thermometer": generator.thermometer_icon(),
    }

    # Save icons and return paths
    icon_paths = {}
    for name, svg_content in icons.items():
        file_path = icon_dir / f"{name}.svg"
        try:
            file_path.write_text(svg_content, encoding='utf-8')
            icon_paths[name] = str(file_path)
        except Exception:
            # Skip failed icons
            continue

    return icon_paths


def get_svg_utils(color_manager=None) -> Tuple[SVGManipulator, IconGenerator]:
    """
    @brief Get SVG utility instances configured with color manager
    @param color_manager: Optional color manager for theming
    @return Tuple of (SVGManipulator, IconGenerator)
    """
    manipulator = SVGManipulator(color_manager)
    generator = IconGenerator(color_manager)
    return manipulator, generator
