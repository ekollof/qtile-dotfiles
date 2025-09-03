#!/usr/bin/env python3
"""
Tests for SVG utilities module
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from modules.svg_utils import (
    IconGenerator,
    SVGBuilder,
    SVGIcon,
    SVGManipulator,
    create_themed_icon_cache,
    get_svg_utils,
)


class TestSVGIcon:
    """Test SVGIcon dataclass"""

    def test_initialization(self):
        """Test SVGIcon init"""
        content: str = '<svg width="24" height="24"><circle cx="12" cy="12" r="10"/></svg>'
        icon: SVGIcon = SVGIcon(
            content=content,
            width=24,
            height=24,
            fill_color="#ffffff",
            stroke_color="#000000",
            stroke_width=1.0,
            viewbox="0 0 24 24"
        )

        assert icon.content == content
        assert icon.width == 24
        assert icon.height == 24
        assert icon.fill_color == "#ffffff"
        assert icon.stroke_color == "#000000"
        assert icon.stroke_width == 1.0
        assert icon.viewbox == "0 0 24 24"

    def test_initialization_defaults(self):
        """Test SVGIcon init with defaults"""
        content: str = '<svg><rect width="10" height="10"/></svg>'
        icon: SVGIcon = SVGIcon(content=content, width=10, height=10)

        assert icon.fill_color == "#ffffff"
        assert icon.stroke_color == "#000000"
        assert icon.stroke_width == 1.0
        assert icon.viewbox is None


class TestSVGBuilder:
    """Test SVGBuilder class"""

    def test_initialization(self):
        """Test SVGBuilder init"""
        builder: SVGBuilder = SVGBuilder(32, 32)
        assert builder.width == 32
        assert builder.height == 32
        assert builder.elements == []
        assert builder.defs == []

    def test_add_circle(self):
        """Test adding circle element"""
        builder: SVGBuilder = SVGBuilder(24, 24)
        result: SVGBuilder = builder.add_circle(12, 12, 8, "#ff0000", "none", 2)

        assert result is builder  # Method chaining
        assert len(builder.elements) == 1
        assert 'cx="12"' in builder.elements[0]
        assert 'cy="12"' in builder.elements[0]
        assert 'r="8"' in builder.elements[0]
        assert 'fill="#ff0000"' in builder.elements[0]
        # Note: stroke is only added when stroke != "none"
        assert 'stroke' not in builder.elements[0]
        assert 'stroke-width' not in builder.elements[0]

    def test_add_circle_no_stroke(self):
        """Test adding circle without stroke"""
        builder: SVGBuilder = SVGBuilder(24, 24)
        builder.add_circle(12, 12, 8, "#ff0000")

        assert 'stroke="none"' not in builder.elements[0]

    def test_add_rect(self):
        """Test adding rectangle element"""
        builder: SVGBuilder = SVGBuilder(24, 24)
        result: SVGBuilder = builder.add_rect(5, 5, 14, 14, "#00ff00", "#000000", 1, 2)

        assert result is builder
        assert len(builder.elements) == 1
        assert 'x="5"' in builder.elements[0]
        assert 'y="5"' in builder.elements[0]
        assert 'width="14"' in builder.elements[0]
        assert 'height="14"' in builder.elements[0]
        assert 'fill="#00ff00"' in builder.elements[0]
        assert 'stroke="#000000"' in builder.elements[0]
        assert 'stroke-width="1"' in builder.elements[0]
        assert 'rx="2"' in builder.elements[0]

    def test_add_path(self):
        """Test adding path element"""
        builder: SVGBuilder = SVGBuilder(24, 24)
        path_data: str = "M10 10 L20 20 L10 20 Z"
        result: SVGBuilder = builder.add_path(path_data, "#0000ff", "#ff0000", 2)

        assert result is builder
        assert len(builder.elements) == 1
        assert f'd="{path_data}"' in builder.elements[0]
        assert 'fill="#0000ff"' in builder.elements[0]
        assert 'stroke="#ff0000"' in builder.elements[0]
        assert 'stroke-width="2"' in builder.elements[0]

    def test_add_polygon(self):
        """Test adding polygon element"""
        builder: SVGBuilder = SVGBuilder(24, 24)
        points: list[tuple[float, float]] = [(0.0, 0.0), (10.0, 0.0), (5.0, 10.0)]
        result: SVGBuilder = builder.add_polygon(points, "#ff00ff", "#00ff00", 1)

        assert result is builder
        assert len(builder.elements) == 1
        assert 'points="0.0,0.0 10.0,0.0 5.0,10.0"' in builder.elements[0]
        assert 'fill="#ff00ff"' in builder.elements[0]
        assert 'stroke="#00ff00"' in builder.elements[0]
        assert 'stroke-width="1"' in builder.elements[0]

    def test_build_simple(self):
        """Test building simple SVG"""
        builder: SVGBuilder = SVGBuilder(24, 24)
        builder.add_circle(12, 12, 10, "#ff0000")

        svg: str = builder.build()

        assert svg.startswith('<svg width="24" height="24"')
        assert 'viewBox="0 0 24 24"' in svg
        assert '<circle cx="12" cy="12" r="10" fill="#ff0000"/>' in svg
        assert svg.endswith('</svg>')

    def test_build_with_custom_viewbox(self):
        """Test building SVG with custom viewbox"""
        builder: SVGBuilder = SVGBuilder(24, 24)
        builder.add_rect(0, 0, 20, 20, "#000000")

        svg: str = builder.build("0 0 20 20")

        assert 'viewBox="0 0 20 20"' in svg

    def test_build_with_defs(self):
        """Test building SVG with definitions"""
        builder: SVGBuilder = SVGBuilder(24, 24)
        builder.defs.append('<linearGradient id="grad1"><stop offset="0%" stop-color="#ff0000"/><stop offset="100%" stop-color="#0000ff"/></linearGradient>')
        builder.add_rect(0, 0, 24, 24, "url(#grad1)")

        svg: str = builder.build()

        assert '<defs>' in svg
        assert 'linearGradient' in svg
        assert '</defs>' in svg


class TestSVGManipulator:
    """Test SVGManipulator class"""

    def test_initialization(self):
        """Test SVGManipulator init"""
        manipulator: SVGManipulator = SVGManipulator()
        assert manipulator.color_manager is None

    def test_initialization_with_color_manager(self):
        """Test SVGManipulator init with color manager"""
        mock_color_manager: MagicMock = MagicMock()
        manipulator: SVGManipulator = SVGManipulator(mock_color_manager)
        assert manipulator.color_manager is mock_color_manager

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.read_text')
    def test_load_svg_success(self, mock_read_text: MagicMock, mock_exists: MagicMock):
        """Test loading SVG file successfully"""
        mock_exists.return_value = True
        mock_read_text.return_value = '<svg width="24" height="24" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/></svg>'

        manipulator: SVGManipulator = SVGManipulator()
        result: SVGIcon | None = manipulator.load_svg('/path/to/test.svg')

        assert result is not None
        assert result.width == 24
        assert result.height == 24
        assert result.viewbox == "0 0 24 24"
        assert '<circle' in result.content

    @patch('pathlib.Path.exists')
    def test_load_svg_file_not_found(self, mock_exists: MagicMock):
        """Test loading SVG file that doesn't exist"""
        mock_exists.return_value = False

        manipulator: SVGManipulator = SVGManipulator()
        result: SVGIcon | None = manipulator.load_svg('/path/to/nonexistent.svg')

        assert result is None

    def test_parse_dimension_pixels(self):
        """Test parsing dimension with px units"""
        manipulator: SVGManipulator = SVGManipulator()
        result: int = manipulator._parse_dimension("24px")  # type: ignore
        assert result == 24

    def test_parse_dimension_no_units(self):
        """Test parsing dimension without units"""
        manipulator: SVGManipulator = SVGManipulator()
        result: int = manipulator._parse_dimension("32")  # type: ignore
        assert result == 32

    def test_parse_dimension_percentage(self):
        """Test parsing dimension with percentage"""
        manipulator: SVGManipulator = SVGManipulator()
        result: int = manipulator._parse_dimension("50%")  # type: ignore
        assert result == 50

    def test_parse_dimension_invalid(self):
        """Test parsing invalid dimension"""
        manipulator: SVGManipulator = SVGManipulator()
        result: int = manipulator._parse_dimension("invalid")  # type: ignore
        assert result == 24  # Default fallback

    def test_recolor_svg_simple(self):
        """Test simple SVG recoloring"""
        manipulator: SVGManipulator = SVGManipulator()
        original_svg: SVGIcon = SVGIcon(
            content='<svg><circle fill="#ff0000" stroke="#000000"/></svg>',
            width=24,
            height=24
        )

        color_map: dict[str, str] = {"#ff0000": "#00ff00", "#000000": "#ffffff"}
        result: SVGIcon = manipulator.recolor_svg(original_svg, color_map)

        assert 'fill="#00ff00"' in result.content
        assert 'stroke="#ffffff"' in result.content

    def test_recolor_svg_css_style(self):
        """Test recoloring SVG with CSS-style color definitions"""
        manipulator: SVGManipulator = SVGManipulator()
        original_svg: SVGIcon = SVGIcon(
            content='<svg><circle style="fill:#ff0000;stroke:#000000"/></svg>',
            width=24,
            height=24
        )

        color_map: dict[str, str] = {"#ff0000": "#00ff00"}
        result: SVGIcon = manipulator.recolor_svg(original_svg, color_map)

        assert 'fill:#00ff00' in result.content

    def test_recolor_svg_stop_color(self):
        """Test recoloring SVG gradient stop colors"""
        manipulator: SVGManipulator = SVGManipulator()
        original_svg: SVGIcon = SVGIcon(
            content='<svg><stop stop-color="#ff0000"/></svg>',
            width=24,
            height=24
        )

        color_map: dict[str, str] = {"#ff0000": "#00ff00"}
        result: SVGIcon = manipulator.recolor_svg(original_svg, color_map)

        assert 'stop-color="#00ff00"' in result.content

    @patch('pathlib.Path.write_text')
    @patch('pathlib.Path.parent')
    @patch('pathlib.Path.mkdir')
    def test_save_svg_success(self, mock_mkdir: MagicMock, mock_parent: MagicMock, mock_write_text: MagicMock):
        """Test saving SVG file successfully"""
        mock_parent.mkdir.return_value = None

        manipulator: SVGManipulator = SVGManipulator()
        svg_icon: SVGIcon = SVGIcon(content='<svg>test</svg>', width=24, height=24)

        result: bool = manipulator.save_svg(svg_icon, '/path/to/output.svg')

        assert result is True
        mock_write_text.assert_called_once_with('<svg>test</svg>', encoding='utf-8')

    @patch('pathlib.Path.write_text')
    def test_save_svg_failure(self, mock_write_text: MagicMock):
        """Test saving SVG file failure"""
        mock_write_text.side_effect = Exception("Write failed")

        manipulator: SVGManipulator = SVGManipulator()
        svg_icon: SVGIcon = SVGIcon(content='<svg>test</svg>', width=24, height=24)

        result: bool = manipulator.save_svg(svg_icon, '/path/to/output.svg')

        assert result is False


class TestIconGenerator:
    """Test IconGenerator class"""

    def test_initialization(self):
        """Test IconGenerator init"""
        generator: IconGenerator = IconGenerator()
        assert generator.size == 24  # Default scaled size
        assert hasattr(generator, 'colors')
        assert 'foreground' in generator.colors
        assert 'background' in generator.colors

    def test_initialization_with_color_manager(self):
        """Test IconGenerator init with color manager"""
        mock_color_manager: MagicMock = MagicMock()
        mock_color_manager.get_colors.return_value = {
            'special': {'foreground': '#ffffff', 'background': '#000000'},
            'colors': {
                'color0': '#424446',
                'color1': '#D75F5F',
                'color5': '#4A88A2',
                'color8': '#8A8A9B',
                'color9': '#D75F5F',
                'color11': '#D7AF5F',
                'color15': '#D0D0D0'
            }
        }

        generator: IconGenerator = IconGenerator(mock_color_manager, 32)
        assert generator.size == 32
        # Should use color5 for foreground (the main accent color)
        assert generator.colors['foreground'] == '#4A88A2'

    def test_battery_icon_full(self):
        """Test generating full battery icon"""
        generator: IconGenerator = IconGenerator()
        svg: str = generator.battery_icon(100)

        assert '<svg' in svg
        assert 'fill="' + generator.colors['accent'] + '"' in svg
        assert 'width="' + str(generator.size) + '"' in svg

    def test_battery_icon_charging(self):
        """Test generating charging battery icon"""
        generator: IconGenerator = IconGenerator()
        svg: str = generator.battery_icon(75, charging=True)

        assert '<svg' in svg
        assert 'fill="' + generator.colors['warning'] + '"' in svg  # Charging uses warning color

    def test_wifi_icon_full(self):
        """Test generating full WiFi icon"""
        generator: IconGenerator = IconGenerator()
        svg: str = generator.wifi_icon(3)

        assert '<svg' in svg
        assert 'stroke="' + generator.colors['accent'] + '"' in svg

    def test_wifi_icon_disconnected(self):
        """Test generating disconnected WiFi icon"""
        generator: IconGenerator = IconGenerator()
        svg: str = generator.wifi_icon(0, connected=False)

        assert '<svg' in svg
        assert 'fill="' + generator.colors['muted'] + '"' in svg

    def test_volume_icon_high(self):
        """Test generating high volume icon"""
        generator: IconGenerator = IconGenerator()
        svg: str = generator.volume_icon(100)

        assert '<svg' in svg
        assert 'fill="' + generator.colors['accent'] + '"' in svg

    def test_volume_icon_muted(self):
        """Test generating muted volume icon"""
        generator: IconGenerator = IconGenerator()
        svg: str = generator.volume_icon(0, muted=True)

        assert '<svg' in svg
        assert 'fill="' + generator.colors['error'] + '"' in svg

    def test_cpu_icon_high_usage(self):
        """Test generating CPU icon with high usage"""
        generator: IconGenerator = IconGenerator()
        svg: str = generator.cpu_icon(0.9)

        assert '<svg' in svg
        assert 'fill="' + generator.colors['error'] + '"' in svg

    def test_memory_icon_high_usage(self):
        """Test generating memory icon with high usage"""
        generator: IconGenerator = IconGenerator()
        svg: str = generator.memory_icon(0.85)

        assert '<svg' in svg
        assert 'fill="' + generator.colors['error'] + '"' in svg

    def test_network_icon_active(self):
        """Test generating active network icon"""
        generator: IconGenerator = IconGenerator()
        svg: str = generator.network_icon(rx_active=True, tx_active=True)

        assert '<svg' in svg
        assert 'fill="' + generator.colors['accent'] + '"' in svg

    def test_python_icon(self):
        """Test generating Python logo icon"""
        generator: IconGenerator = IconGenerator()
        svg: str = generator.python_icon()

        assert '<svg' in svg
        assert 'fill="' + generator.colors['accent'] + '"' in svg

    def test_mail_icon(self):
        """Test generating mail icon"""
        generator: IconGenerator = IconGenerator()
        svg: str = generator.mail_icon()

        assert '<svg' in svg
        assert 'fill="' + generator.colors['accent'] + '"' in svg

    def test_thermometer_icon(self):
        """Test generating thermometer icon"""
        generator: IconGenerator = IconGenerator()
        svg: str = generator.thermometer_icon()

        assert '<svg' in svg
        assert 'fill="' + generator.colors['error'] + '"' in svg

    def test_updates_icon(self):
        """Test generating updates icon"""
        generator: IconGenerator = IconGenerator()
        svg: str = generator.updates_icon()

        assert '<svg' in svg
        assert 'fill="' + generator.colors['accent'] + '"' in svg

    def test_refresh_icon(self):
        """Test generating refresh icon"""
        generator: IconGenerator = IconGenerator()
        svg: str = generator.refresh_icon()

        assert '<svg' in svg
        assert 'stroke="' + generator.colors['accent'] + '"' in svg


class TestGlobalFunctions:
    """Test global utility functions"""

    def test_get_svg_utils(self):
        """Test getting SVG utility instances"""
        manipulator: SVGManipulator
        generator: IconGenerator
        manipulator, generator = get_svg_utils()

        assert isinstance(manipulator, SVGManipulator)
        assert isinstance(generator, IconGenerator)

    def test_get_svg_utils_with_color_manager(self):
        """Test getting SVG utilities with color manager"""
        mock_color_manager: MagicMock = MagicMock()
        manipulator: SVGManipulator
        generator: IconGenerator
        manipulator, generator = get_svg_utils(mock_color_manager)

        assert manipulator.color_manager is mock_color_manager
        assert generator.color_manager is mock_color_manager

    @patch('modules.svg_utils.Path.mkdir')
    @patch('modules.svg_utils.Path.write_text')
    def test_create_themed_icon_cache(self, mock_write_text: MagicMock, mock_mkdir: MagicMock):
        """Test creating themed icon cache"""
        mock_color_manager: MagicMock = MagicMock()
        mock_color_manager.get_colors.return_value = {
            'special': {'foreground': '#ffffff', 'background': '#000000'},
            'colors': {'color5': '#4A88A2'}
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            icon_dir: Path = Path(temp_dir) / 'icons'
            result: dict[str, str] = create_themed_icon_cache(mock_color_manager, icon_dir, 24)

            assert isinstance(result, dict)
            assert 'battery_full' in result
            assert 'wifi_full' in result
            assert 'volume_high' in result

            # Verify that write_text was called for each icon
            assert mock_write_text.call_count > 10  # Should create multiple icons


class TestIntegration:
    """Integration tests for SVG functionality"""

    def test_full_svg_workflow(self):
        """Test complete SVG creation and manipulation workflow"""
        # Create an icon
        generator: IconGenerator = IconGenerator()
        svg_content: str = generator.battery_icon(75)

        # Create SVGIcon from content
        svg_icon: SVGIcon = SVGIcon(content=svg_content, width=24, height=24)

        # Manipulate the icon
        manipulator: SVGManipulator = SVGManipulator()
        color_map: dict[str, str] = {"#ffffff": "#ff0000"}
        recolored: SVGIcon = manipulator.recolor_svg(svg_icon, color_map)

        assert recolored.content != svg_icon.content
        assert "#ff0000" in recolored.content

    def test_svg_builder_method_chaining(self):
        """Test SVG builder method chaining"""
        builder: SVGBuilder = SVGBuilder(24, 24)

        # Chain multiple operations
        builder.add_circle(12, 12, 8, "#ff0000")
        builder.add_rect(2, 2, 20, 20, "#00ff00", "#000000", 1)
        builder.add_path("M5 5 L19 19", "#0000ff")
        svg: str = builder.build()

        assert '<circle' in svg
        assert '<rect' in svg
        assert '<path' in svg
        assert svg.count('<circle') == 1
        assert svg.count('<rect') == 1
        assert svg.count('<path') == 1

    def test_icon_generator_with_custom_colors(self):
        """Test icon generator with custom color scheme"""
        mock_color_manager: MagicMock = MagicMock()
        mock_color_manager.get_colors.return_value = {
            'special': {'foreground': '#ff0000', 'background': '#000000'},
            'colors': {
                'color0': '#424446',
                'color1': '#D75F5F',
                'color5': '#00ff00',
                'color8': '#0000ff',
                'color9': '#D75F5F',
                'color11': '#D7AF5F',
                'color15': '#D0D0D0'
            }
        }

        generator: IconGenerator = IconGenerator(mock_color_manager)

        # Verify colors were applied - should use color5 for foreground
        assert generator.colors['foreground'] == '#00ff00'
        assert generator.colors['background'] == '#000000'

        # Generate an icon and verify it uses the custom colors
        svg: str = generator.battery_icon(50)
        assert '#00ff00' in svg  # Should contain the custom foreground color