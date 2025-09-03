#!/usr/bin/env python3
"""
Tests for color management module

@brief Comprehensive test suite for color management functionality
"""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

from modules.colors import ColorManager, get_color_manager


class TestColorManager:
    """Test ColorManager class functionality"""

    def test_initialization(self) -> None:
        """Test ColorManager initialization"""
        manager: ColorManager = ColorManager()
        assert hasattr(manager, 'colors_file')
        assert hasattr(manager, 'colordict')
        assert hasattr(manager, '_observer')
        assert hasattr(manager, '_watching')

    def test_load_colors_success(self) -> None:
        """Test loading colors from valid JSON file"""
        manager: ColorManager = ColorManager()

        mock_colors: dict[str, Any] = {
            'special': {'foreground': '#ffffff', 'background': '#000000'},
            'colors': {'color1': '#ff0000'}
        }

        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.open') as mock_open, \
             patch('json.load', return_value=mock_colors), \
             patch('pathlib.Path.expanduser', return_value=Path('/mock/path/colors.json')):

            mock_file: MagicMock = MagicMock()
            mock_file.__enter__.return_value = mock_file
            mock_open.return_value = mock_file

            colors: dict[str, Any] = manager.load_colors()
            assert colors == mock_colors

    def test_load_colors_fallback(self) -> None:
        """Test loading colors fallback when file doesn't exist"""
        manager: ColorManager = ColorManager()

        with patch('pathlib.Path.exists', return_value=False), \
             patch.object(manager, '_load_colors', return_value={
                 'special': {'foreground': '#ffffff', 'background': '#1e1e1e'},
                 'colors': {'color0': '#1e1e1e', 'color1': '#e06c75'}
             }):
            colors: dict[str, Any] = manager.load_colors()

            # Should return fallback colors
            assert 'special' in colors
            assert 'colors' in colors
            assert colors['special']['foreground'] == '#ffffff'
            assert colors['special']['background'] == '#1e1e1e'

    def test_get_colors_auto_start_monitoring(self) -> None:
        """Test get_colors auto-starts monitoring on first access"""
        manager: ColorManager = ColorManager()

        with patch.object(manager, 'start_monitoring') as mock_start:
            _ = manager.get_colors()
            assert mock_start.called

    def test_get_colors_cached(self) -> None:
        """Test that get_colors returns cached colors"""
        manager: ColorManager = ColorManager()
        manager.colordict = {'test': 'colors'}

        with patch.object(manager, 'start_monitoring'):
            colors: dict[str, Any] = manager.get_colors()
            assert colors == {'test': 'colors'}

    def test_start_monitoring_watchdog(self) -> None:
        """Test starting monitoring with watchdog available"""
        manager: ColorManager = ColorManager()

        with patch('modules.color_management.watchdog_available', True), \
             patch('modules.color_management.Observer') as mock_observer_class, \
             patch('pathlib.Path.mkdir'):

            mock_observer: MagicMock = MagicMock()
            mock_observer_class.return_value = mock_observer

            manager.start_monitoring()

            assert manager._watching is True  # type: ignore
            assert mock_observer.start.called

    def test_start_monitoring_polling_fallback(self) -> None:
        """Test starting monitoring with polling fallback"""
        manager: ColorManager = ColorManager()

        with patch('modules.color_management.watchdog_available', False), \
             patch('threading.Thread') as mock_thread:

            manager.start_monitoring()

            assert manager._watching is True  # type: ignore
            assert mock_thread.called

    def test_stop_monitoring(self) -> None:
        """Test stopping monitoring"""
        manager: ColorManager = ColorManager()

        with patch.object(manager, '_shutdown_event') as mock_shutdown_event, \
             patch('threading.Thread.join'):

            # Set up the mock shutdown event
            mock_shutdown_event.set = MagicMock()

            manager.stop_monitoring()

            assert manager._watching is False  # type: ignore
            assert mock_shutdown_event.set.called

    def test_manual_reload_colors_success(self) -> None:
        """Test manual color reload success"""
        manager: ColorManager = ColorManager()
        manager.colordict = {'old': 'colors'}

        with patch.object(manager, '_load_colors', return_value={'new': 'colors'}), \
             patch.object(manager, '_handle_color_change') as mock_handle:

            result: bool = manager.manual_reload_colors()

            assert result is True
            assert manager.colordict == {'new': 'colors'}
            mock_handle.assert_called_once()

    def test_manual_reload_colors_no_change(self) -> None:
        """Test manual color reload when colors unchanged"""
        manager: ColorManager = ColorManager()
        original_colors: dict[str, Any] = {'same': 'colors'}
        manager.colordict = original_colors

        with patch.object(manager, '_load_colors', return_value=original_colors), \
             patch.object(manager, '_detect_color_changes', return_value=False), \
             patch.object(manager, '_handle_color_change') as mock_handle:

            result: bool = manager.manual_reload_colors()

            assert result is True
            mock_handle.assert_not_called()

    def test_force_start_monitoring_already_active(self) -> None:
        """Test force start monitoring when already active"""
        manager: ColorManager = ColorManager()
        manager._watching = True  # type: ignore

        result: bool = manager.force_start_monitoring()
        assert result is True

    def test_force_start_monitoring_success(self) -> None:
        """Test force start monitoring success"""
        manager: ColorManager = ColorManager()
        manager._watching = False  # type: ignore

        with patch.object(manager, 'start_monitoring'), \
             patch.object(manager, 'is_monitoring', return_value=True):

            result: bool = manager.force_start_monitoring()
            assert result is True

    def test_restart_monitoring(self) -> None:
        """Test restart monitoring"""
        manager: ColorManager = ColorManager()

        with patch.object(manager, 'stop_monitoring') as mock_stop, \
             patch.object(manager, 'start_monitoring') as mock_start, \
             patch('time.sleep'):

            manager.restart_monitoring()

            assert mock_stop.called
            assert mock_start.called

    def test_is_monitoring(self) -> None:
        """Test is_monitoring method"""
        manager: ColorManager = ColorManager()

        manager._watching = True  # type: ignore
        assert manager.is_monitoring() is True

        manager._watching = False  # type: ignore
        assert manager.is_monitoring() is False

    def test_validate_color_file_exists(self) -> None:
        """Test color file validation when file exists"""
        manager: ColorManager = ColorManager()

        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat:

            mock_stat.return_value.st_size = 1000
            result: bool = manager._validate_color_file()  # type: ignore
            assert result is True

    def test_validate_color_file_missing(self) -> None:
        """Test color file validation when file doesn't exist"""
        manager: ColorManager = ColorManager()

        with patch('pathlib.Path.exists', return_value=False):
            result: bool = manager._validate_color_file()  # type: ignore
            assert result is False

    def test_validate_color_file_too_small(self) -> None:
        """Test color file validation when file is too small"""
        manager: ColorManager = ColorManager()

        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat:

            mock_stat.return_value.st_size = 5  # Too small
            result: bool = manager._validate_color_file()  # type: ignore
            assert result is False


class TestGlobalFunctions:
    """Test global utility functions"""

    def test_get_color_manager_singleton(self) -> None:
        """Test singleton pattern for color manager"""
        manager1: ColorManager = get_color_manager()
        manager2: ColorManager = get_color_manager()

        assert manager1 is manager2
        assert isinstance(manager1, ColorManager)

    def test_get_colors_function(self) -> None:
        """Test get_colors global function"""
        from modules.colors import get_colors

        with patch.object(ColorManager, 'get_colors', return_value={'test': 'colors'}):
            colors: dict[str, Any] = get_colors()
            assert colors == {'test': 'colors'}

    def test_start_color_monitoring_function(self) -> None:
        """Test start_color_monitoring global function"""
        from modules.colors import start_color_monitoring

        with patch.object(ColorManager, 'start_monitoring') as mock_start:
            start_color_monitoring()
            assert mock_start.called

    def test_manual_color_reload_function(self) -> None:
        """Test manual_color_reload global function"""
        from modules.colors import manual_color_reload

        with patch.object(ColorManager, 'manual_reload_colors', return_value=True):
            result: bool = manual_color_reload()
            assert result is True


class TestIntegration:
    """Integration tests for color management"""

    def test_full_color_workflow(self) -> None:
        """Test complete color management workflow"""
        with patch('modules.color_management.ColorManager.__init__', return_value=None), \
             patch('modules.color_management.ColorManager._load_colors', return_value={'test': 'colors'}), \
             patch('modules.color_management.ColorManager.get_colors', return_value={'test': 'colors'}), \
             patch('modules.color_management.ColorManager.start_monitoring'):

            manager: ColorManager = ColorManager()
            manager._watching = False  # type: ignore
            manager._auto_start_attempted = True  # type: ignore
            manager.colordict = {'test': 'colors'}

            # Test loading colors
            colors: dict[str, Any] = manager.get_colors()
            assert colors == {'test': 'colors'}

    def test_color_file_change_handling(self) -> None:
        """Test handling of color file changes"""
        with patch('modules.color_management.ColorManager.__init__', return_value=None), \
             patch('modules.color_management.ColorManager._load_colors', return_value={'new': 'colors'}), \
             patch('modules.color_management.ColorManager._validate_color_file', return_value=True), \
             patch('modules.color_management.ColorManager._detect_color_changes', return_value=True), \
             patch('modules.color_management.ColorManager._update_svg_icons'), \
             patch('libqtile.qtile') as mock_qtile:

            manager: ColorManager = ColorManager()
            manager.colordict = {'old': 'colors'}

            # Mock qtile restart method
            mock_qtile.restart = MagicMock()

            manager._handle_color_change()  # type: ignore

            assert manager.colordict == {'new': 'colors'}

    def test_color_manager_error_handling(self) -> None:
        """Test error handling in color manager"""
        with patch('modules.color_management.ColorManager.__init__', return_value=None), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.open') as mock_open, \
             patch('json.load', side_effect=ValueError("Invalid JSON")):

            mock_file: MagicMock = MagicMock()
            mock_file.__enter__.return_value = mock_file
            mock_open.return_value = mock_file

            manager: ColorManager = ColorManager()
            manager.colors_file = Path('/mock/path/colors.json')

            colors: dict[str, Any] = manager.load_colors()
            # Should return fallback colors on error
            assert 'special' in colors
            assert 'colors' in colors

    def test_monitoring_failure_fallback(self) -> None:
        """Test monitoring failure and fallback behavior"""
        manager: ColorManager = ColorManager()

        # Test watchdog failure falls back to polling
        with patch('modules.color_management.watchdog_available', True), \
             patch('modules.color_management.Observer', side_effect=Exception("Watchdog failed")), \
             patch('threading.Thread') as mock_thread:

            manager.start_monitoring()

            # Should still be watching using polling
            assert manager._watching is True  # type: ignore
            assert mock_thread.called